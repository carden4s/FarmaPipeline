import csv
import random
from datetime import datetime, timedelta

random.seed(42)

medicamentos = [
    "Ceftriaxona 1g",
    "Metoprolol 50mg",
    "Midazolam 5mg/ml",
    "Propofol 1%",
    "Vancomicina 500mg",
    "Insulina NPH 100U",
    "Furosemida 40mg",
    "Morfina 10mg/ml",
]

departamentos = ["UCI", "Cirugía", "Pediatría", "Urgencias", "Cardiología"]

categorias = {
    "Ceftriaxona 1g":       "Antibiotico",
    "Metoprolol 50mg":      "Cardiovascular",
    "Midazolam 5mg/ml":     "Sedante",
    "Propofol 1%":          "Anestesico",
    "Vancomicina 500mg":    "Antibiotico",
    "Insulina NPH 100U":    "Endocrino",
    "Furosemida 40mg":      "Diuretico",
    "Morfina 10mg/ml":      "Analgesico",
}

costos = {
    "Ceftriaxona 1g":       85.00,
    "Metoprolol 50mg":      45.00,
    "Midazolam 5mg/ml":     150.00,
    "Propofol 1%":          200.00,
    "Vancomicina 500mg":    320.00,
    "Insulina NPH 100U":    95.00,
    "Furosemida 40mg":      35.00,
    "Morfina 10mg/ml":      180.00,
}

def fecha_aleatoria():
    inicio = datetime(2024, 1, 1)
    dias = random.randint(0, 364)
    return (inicio + timedelta(days=dias)).strftime("%Y-%m-%d")

def ensuciar_dato(valor):
    """Introduce errores realistas en los datos, como pasa en la vida real."""
    r = random.random()
    if r < 0.05:
        return ""                        # valor nulo
    elif r < 0.08:
        return str(valor).upper()        # mayusculas inconsistentes
    elif r < 0.10:
        return f" {valor} "             # espacios extra
    return str(valor)

filas = []
for _ in range(500):
    med  = random.choice(medicamentos)
    depto = random.choice(departamentos)
    dosis = random.randint(5, 50)
    costo = costos[med] * random.uniform(0.95, 1.05)  # variacion de costo

    # introduce datos sucios en algunas columnas
    filas.append({
        "fecha":             fecha_aleatoria(),
        "medicamento":       ensuciar_dato(med),
        "categoria":         categorias[med],
        "departamento":      ensuciar_dato(depto),
        "dosis_dispensadas": dosis if random.random() > 0.04 else "",  # algunos nulos
        "costo_unitario":    round(costo, 2),
        "paciente_id":       f"PAC{random.randint(1000, 9999)}" if random.random() > 0.08 else "",
    })

with open("dispensaciones_hospitalarias.csv", "w", newline="", encoding="utf-8") as f:
    campos = ["fecha", "medicamento", "categoria", "departamento",
              "dosis_dispensadas", "costo_unitario", "paciente_id"]
    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()
    writer.writerows(filas)

print("Archivo dispensaciones_hospitalarias.csv generado con 500 registros.")
print("Contiene datos de Farmacia Hospitalaria con medicamentos especializados.")
print("Incluye valores nulos, espacios extra y mayusculas inconsistentes.")
print("Tu trabajo: limpiarlo con Pandas.")
