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
                """
                Limpia datos de dispensaciones hospitalarias según el plan de transformación.
                
                Transformaciones:
                - fecha: TIMESTAMP (YYYY-MM-DD)
                - medicamento: VARCHAR (trim)
                - categoria: VARCHAR (trim + upper)
                - departamento: VARCHAR (trim + upper)
                - dosis_dispensadas: INTEGER
                - costo_unitario: DECIMAL
                - paciente_id: VARCHAR (trim)
                """
                
                print(f"Leyendo archivo: {file_path}")
                df = pd.read_csv(file_path, encoding="utf-8")
                
                print(f"Registros iniciales: {len(df)}")
                
                # 1. Eliminar filas completamente vacías
                df = df.dropna(how='all')
                
                # 2. Limpieza de FECHA
                print("\n► Limpiando: fecha")
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
                df = df.dropna(subset=['fecha'])  # Eliminar fechas inválidas
                df['fecha'] = df['fecha'].dt.strftime('%Y-%m-%d')
                
                # 3. Limpieza de MEDICAMENTO
                print("► Limpiando: medicamento")
                df['medicamento'] = df['medicamento'].fillna('')
                df['medicamento'] = df['medicamento'].str.strip().str.upper()
                
                # 4. Limpieza de CATEGORIA
                print("► Limpiando: categoria")
                df['categoria'] = df['categoria'].fillna('')
                df['categoria'] = df['categoria'].str.strip().str.upper()
                
                # 5. Limpieza de DEPARTAMENTO
                print("► Limpiando: departamento")
                df['departamento'] = df['departamento'].fillna('')
                df['departamento'] = df['departamento'].str.strip().str.upper()
                
                # Mapeo de departamentos con variaciones
                dept_map = {
                    'UCI': 'UCI',
                    'CIRUGÍA': 'CIRUGIA',
                    'CIRUGÍA': 'CIRUGIA',
                    'PEDIATRÍA': 'PEDIATRIA',
                    'PEDIATRIA': 'PEDIATRIA',
                    'URGENCIAS': 'URGENCIAS',
                    'CARDIOLOGÍA': 'CARDIOLOGIA',
                    'CARDIOLOGIA': 'CARDIOLOGIA'
                }
                df['departamento'] = df['departamento'].map(lambda x: dept_map.get(x, x))
                
                # 6. Limpieza de DOSIS_DISPENSADAS
                print("► Limpiando: dosis_dispensadas")
                df['dosis_dispensadas'] = pd.to_numeric(df['dosis_dispensadas'], errors='coerce')
                df['dosis_dispensadas'] = df['dosis_dispensadas'].fillna(0).astype(int)
                df = df[df['dosis_dispensadas'] > 0]  # Solo dosis positivas
                
                # 7. Limpieza de COSTO_UNITARIO
                print("► Limpiando: costo_unitario")
                df['costo_unitario'] = pd.to_numeric(df['costo_unitario'], errors='coerce')
                df['costo_unitario'] = df['costo_unitario'].fillna(0.0).round(2)
                
                # 8. Limpieza de PACIENTE_ID
                print("► Limpiando: paciente_id")
                df['paciente_id'] = df['paciente_id'].fillna('')
                df['paciente_id'] = df['paciente_id'].str.strip()
                
                # 9. Eliminar duplicados exactos
                print("► Eliminando duplicados")
                initial_count = len(df)
                df = df.drop_duplicates()
                removed_duplicates = initial_count - len(df)
                print(f"   ✓ Registros después de limpieza: {len(df)} (eliminados {removed_duplicates} duplicados)")
        
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