"""El director de una institución educativa ha solicitado el desarrollo de una aplicación en Java para 
procesar un archivo de registros académicos de los estudiantes del centro. La información se 
encuentra almacenada en un archivo con formato CSV, cuya estructura es la siguiente: 
Nombre del 
Estudiante 
Cédula 
Edad 
Nota1 
Nota2 
Nota3 
A partir de este archivo, la aplicación debe: 
• Generar un nuevo archivo CSV con los siguientes campos: Cédula, Edad, NotaPromedio, 
Estado, donde el campo Estado debe indicar si el estudiante está Aprobado o Reprobado, 
considerando una nota mínima de aprobación de 71 puntos."""

from pathlib import Path
import sys
import pandas as pd
import polars as pl


# ----- Configuración de rutas -----
baseDir = Path(__file__).resolve().parent
defaultInput = baseDir / 'notas.csv'
outputPandas = baseDir / 'notas_calificadas_pandas.csv'
outputPolars = baseDir / 'notas_calificadas_polars.csv'


def ubicarCarp():
    if defaultInput.exists():
        return defaultInput
    matches = list(baseDir.rglob('notas.csv'))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"no se encontró 'notas.csv' en {baseDir} ni subcarpetas")


def guaradarInFloat(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def procesarPandas(inputPath: Path, outputPath: Path, umbral=71):
    df = pd.read_csv(inputPath, encoding='utf-8', dtype={'Cédula': str})

    notas = df[['Nota1', 'Nota2', 'Nota3']].apply(pd.to_numeric, errors='coerce')

    df['NotaPromedio'] = notas.mean(axis=1).round(2)

    df['Estado'] = df['NotaPromedio'].apply(lambda x: 'Aprobo' if x >= umbral else 'Reprobo')

    out = df[['Cédula', 'Edad', 'NotaPromedio', 'Estado']]
    out.to_csv(outputPath, index=False, encoding='utf-8')

    print(f"[pandas] Escrito {outputPath} con {len(out)} filas.")


def procesarPolars(inputPath: Path, outputPath: Path, umbral=71):

    try:
        df = pl.read_csv(inputPath, try_parse_dates=False, dtypes={'Cédula': pl.Utf8})
    except Exception:
        df = pl.read_csv(inputPath, try_parse_dates=False)
    df = df.with_columns([
        pl.col('Nota1').cast(pl.Float64),
        pl.col('Nota2').cast(pl.Float64),
        pl.col('Nota3').cast(pl.Float64),
    ])

    df = df.with_columns(((pl.col('Nota1') + pl.col('Nota2') + pl.col('Nota3')) / 3).alias('NotaPromedio'))
    df = df.with_columns(pl.col('NotaPromedio').map_elements(lambda x: round(x, 2), return_dtype=pl.Float64).alias('NotaPromedio'))

    # Determinar estado usando expresión condicional; usar pl.lit para literales
    df = df.with_columns(
        pl.when(pl.col('NotaPromedio') >= umbral).then(pl.lit('Paso')).otherwise(pl.lit('No paso')).alias('Estado')
    )

    # Seleccionar columnas y escribir CSV de salida
    out = df.select(['Cédula', 'Edad', 'NotaPromedio', 'Estado'])
    out = out.with_columns(pl.col('Cédula').cast(pl.Utf8))
    out.write_csv(outputPath)

    print(f"[polars] Escrito {outputPath} con {out.height} filas.")


def main():
    # Buscar el archivo de entrada
    try:
        inputPath = ubicarCarp()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Ejecutar ambos procesamientos
    procesarPandas(inputPath, outputPandas)
    procesarPolars(inputPath, outputPolars)


if __name__ == '__main__':
    main()
