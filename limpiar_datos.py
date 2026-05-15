import pandas as pd
from pathlib import Path
from datetime import datetime

def limpiar_datos_hospitalarios(file_path):
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
    df['medicamento'] = df['medicamento'].str.strip()
    
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
    print(f"  Duplicados eliminados: {removed_duplicates}")
    
    print(f"\nRegistros finales: {len(df)}")
    
    # Resumen de cambios
    print("\n" + "="*60)
    print("RESUMEN DE LIMPIEZA")
    print("="*60)
    print(f"Registros procesados: {len(df)}")
    print(f"\nTipos de datos:")
    print(df.dtypes)
    print(f"\nMuestra de datos limpios:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    # Procesar archivo de datos sucios
    input_file = "dispensaciones_hospitalarias.csv"
    output_file = "dispensaciones_limpias.csv"
    
    if Path(input_file).exists():
        df_limpio = limpiar_datos_hospitalarios(input_file)
        df_limpio.to_csv(output_file, index=False, encoding="utf-8")
        print(f"\n✓ Archivo limpio guardado: {output_file}")
    else:
        print(f"✗ Archivo no encontrado: {input_file}")
