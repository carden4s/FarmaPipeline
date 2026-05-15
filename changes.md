
# Plan de Limpieza de Datos - Farmacia Hospitalaria

## Tareas de Limpieza

### 1. Limpieza General
- [ ] Eliminar espacios en blanco al inicio y final de todas las columnas (trim)
- [ ] Convertir valores de texto a MAYÚSCULAS donde sea apropiado
- [ ] Manejar valores nulos y datos faltantes

### 2. Transformación por Columna

#### `fecha`
- Tipo: TIMESTAMP
- Convertir string a formato de fecha (YYYY-MM-DD)
- Validar fechas válidas (no futuras, rango 2024)

#### `medicamento`
- Tipo: VARCHAR
- Aplicar trim() para remover espacios extras
- Estandarizar nombres (verificar consistencia)

#### `categoria`
- Tipo: VARCHAR
- Aplicar trim() y UPPER() para estandarización
- Valores esperados: Antibiotico, Sedante, Anestesico, Endocrino, Diuretico, Analgesico, Cardiovascular

#### `departamento`
- Tipo: VARCHAR
- Aplicar trim() y UPPER() para estandarización
- Valores esperados: UCI, CIRUGÍA, PEDIATRÍA, URGENCIAS, CARDIOLOGÍA

#### `dosis_dispensadas`
- Tipo: INTEGER
- Convertir a número entero
- Eliminar valores nulos o reemplazar con 0
- Validar rango positivo (> 0)

#### `costo_unitario`
- Tipo: DECIMAL/FLOAT
- Convertir a número con 2 decimales
- Validar valores positivos

#### `paciente_id`
- Tipo: VARCHAR
- Aplicar trim()
- Validar formato PAC#### (4 dígitos)
- Manejar valores faltantes

### 3. Validaciones Finales
- [ ] Verificar no hay duplicados innecesarios
- [ ] Confirmar tipos de datos correctos
- [ ] Guardar datos limpios en `clean_dispensaciones_hospitalarias.csv`
- [ ] Cargar a Snowflake tabla: `Hospital_Medicamentos`