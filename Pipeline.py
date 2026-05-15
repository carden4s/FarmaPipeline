from pathlib import Path
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import os

# Specify the exact path to .env file
env_path = Path(__file__).parent / "sn.env"
load_dotenv(env_path)


# folder structure
incoming_folder    = Path("incoming")
processed_folder   = Path("processed")
output_folder      = Path("output")
need_review_folder = Path("need_review")

# timestamp for logging
today = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")

# create folders if they don't exist
for folder in [incoming_folder, processed_folder, output_folder, need_review_folder]:
    folder.mkdir(parents=True, exist_ok=True)

def get_snowflake_connection():
    return snowflake.connector.connect(
        account   = os.getenv("SNOWFLAKE_ACCOUNT"),
        user      = os.getenv("SNOWFLAKE_USER"),
        password  = os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse = os.getenv("SNOWFLAKE_WAREHOUSE"),
        database  = os.getenv("SNOWFLAKE_DATABASE"),
        schema    = os.getenv("SNOWFLAKE_SCHEMA")
    )

with open("pipeline_log.txt", "a", encoding="utf-8") as log:
    csv_files = list(incoming_folder.glob("*.csv"))
    
    if not csv_files:
        log.write(f"No new files found - {today}\n")
        print("No new files to process")
    
    else:
        for file_path in csv_files:
            try:
                print(f"Processing: {file_path.name}")
                
                # read and clean
                df = pd.read_csv(file_path, encoding="utf-8")
                df = df.dropna().copy()
                
                # save local backup
                output_path = output_folder / f"clean_{file_path.name}"
                df.to_csv(output_path, index=False, encoding="utf-8")
                
                # load into Snowflake
                with get_snowflake_connection() as conn:
                    write_pandas(
                        conn,
                        df,
                        "Hospital_Medicamentos",
                        auto_create_table=True
                    )
                
                # only move to processed if EVERYTHING succeeded including Snowflake load
                file_path.rename(processed_folder / file_path.name)
                
                log.write(f"SUCCESS: {file_path.name} loaded to Snowflake - {today}\n")
                print(f"Done: {file_path.name}")
                    
            except pd.errors.EmptyDataError:
                file_path.rename(need_review_folder / file_path.name)
                log.write(f"SKIPPED: {file_path.name} - file is empty - {today}\n")
                    
            except Exception as e:
                file_path.rename(need_review_folder / file_path.name)
                log.write(f"ERROR: {file_path.name} - {str(e)} - {today}\n")
                print(f"Error processing {file_path.name}: {e}")