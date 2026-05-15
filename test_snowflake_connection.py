from pathlib import Path
import snowflake.connector
from dotenv import load_dotenv
import os

# Load environment variables
env_path = Path(__file__).parent / "sn.env"
load_dotenv(env_path)

print("=" * 60)
print("VERIFICANDO CONEXIÓN A SNOWFLAKE")
print("=" * 60)

# Check if env variables are loaded
print("\n1. Verificando variables de entorno...")
required_vars = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", 
                 "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA"]

for var in required_vars:
    value = os.getenv(var)
    if value:
        # Ocultar información sensible
        if "PASSWORD" in var:
            print(f"   ✓ {var}: {'*' * len(value)}")
        else:
            print(f"   ✓ {var}: {value}")
    else:
        print(f"   ✗ {var}: NO ENCONTRADA")

# Try to connect
print("\n2. Intentando conectarse a Snowflake...")
try:
    conn = snowflake.connector.connect(
        account   = os.getenv("SNOWFLAKE_ACCOUNT"),
        user      = os.getenv("SNOWFLAKE_USER"),
        password  = os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse = os.getenv("SNOWFLAKE_WAREHOUSE"),
        database  = os.getenv("SNOWFLAKE_DATABASE"),
        schema    = os.getenv("SNOWFLAKE_SCHEMA")
    )
    print("   ✓ Conexión exitosa!")
    
    # Try a simple query
    print("\n3. Ejecutando consulta de prueba...")
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_USER(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
    result = cursor.fetchone()
    print(f"   ✓ Usuario: {result[0]}")
    print(f"   ✓ Warehouse: {result[1]}")
    print(f"   ✓ Database: {result[2]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ TODO FUNCIONA CORRECTAMENTE")
    print("=" * 60)
    
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}")
    print(f"   ✗ Detalle: {str(e)}")
    print("\n" + "=" * 60)
    print("✗ ERROR EN LA CONEXIÓN")
    print("=" * 60)
