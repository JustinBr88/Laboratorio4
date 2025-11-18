import csv
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# BASE_DIR: carpeta donde se encuentra este script.
# Usar rutas relativas al script evita errores cuando el script
# se ejecuta desde otro directorio de trabajo.
BASE_DIR = Path(__file__).resolve().parent

# Rutas de entrada y salida (archivos CSV) dentro de la misma carpeta.
INPUT = BASE_DIR / 'notas.csv'
OUTPUT = BASE_DIR / 'notas_procesadas.csv'


def safe_float(x):
    """Intentar convertir `x` a float; si falla, devolver 0.0.

    Esto permite manejar campos vacíos o valores no numéricos
    sin que el programa se rompa.
    """
    try:
        return float(x)
    except Exception:
        return 0.0


def round2(n):
    """Redondear `n` a 2 decimales usando ROUND_HALF_UP.

    Usamos Decimal para conseguir un redondeo consistente (ej. 2.345 -> 2.35).
    """
    return float(Decimal(n).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def main():
    # Comprobar que el archivo de entrada existe; si no, salir con código 1.
    if not INPUT.exists():
        print(f"Error: archivo de entrada no encontrado: {INPUT}")
        sys.exit(1)

    # Lista donde almacenaremos las filas transformadas para la salida.
    rows_out = []

    # Abrir el CSV de entrada y leerlo como diccionarios por fila.
    with INPUT.open(newline='', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)

        # Iterar cada registro/estudiante del CSV de entrada.
        for r in reader:
            # Extraer las tres notas y convertirlas a float de forma segura.
            # Si la clave no existe, usamos 0 como valor por defecto.
            n1 = safe_float(r.get('Nota1', 0))
            n2 = safe_float(r.get('Nota2', 0))
            n3 = safe_float(r.get('Nota3', 0))

            # Construir lista de notas y calcular promedio.
            notas = [n1, n2, n3]
            avg = round2(sum(notas) / len(notas)) if notas else 0.0

            # Determinar el estado según el umbral (71 puntos).
            # Si el promedio es >= 71, el estudiante está Aprobado.
            estado = 'Aprobado' if avg >= 71 else 'Reprobado'

            # Añadir la fila procesada (solo los campos solicitados)
            # al listado de salida.
            rows_out.append({
                'Cédula': r.get('Cédula', ''),          # Obtener cédula
                'Edad': r.get('Edad', ''),              # Obtener edad
                'NotaPromedio': f"{avg:.2f}",          # Promedio formateado
                'Estado': estado,                       # Aprobado/Reprobado
            })

    # Abrir el archivo de salida y escribir todas las filas procesadas.
    with OUTPUT.open('w', newline='', encoding='utf-8') as f_out:
        fieldnames = ['Cédula', 'Edad', 'NotaPromedio', 'Estado']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)

        # Escribir encabezado (nombres de columna) en el CSV de salida.
        writer.writeheader()

        # Escribir todas las filas previamente calculadas.
        writer.writerows(rows_out)

    # Mensaje informativo indicando cuántas filas fueron procesadas.
    print(f"Escrito {OUTPUT} con {len(rows_out)} filas.")


if __name__ == '__main__':
    # Punto de entrada: ejecutar la función principal.
    main()
