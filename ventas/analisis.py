from __future__ import annotations

from pathlib import Path
import csv
from typing import Dict, List


# 1. Cargar datos del CSV
# -----------------------------------------------------------------------------
import pandas as pd

def cargar_datos_csv(ruta: str = "ventas.csv") -> List[Dict[str, str]]:
    """Carga el archivo CSV de ventas y devuelve una lista de filas (dict).

    - Usa pandas para la lectura.
    - Normaliza espacios en blanco alrededor de claves/valores.
    - Usa codificación UTF-8 con firma (maneja BOM si existe).
    """
    ruta_path = Path(ruta)
    if not ruta_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    # Leemos con pandas, asegurando dtype str y BOM
    df = pd.read_csv(ruta_path, dtype=str, encoding='utf-8-sig', keep_default_na=False)

    # Limpiamos espacios en los nombres de columna
    df.columns = [str(col).strip() for col in df.columns]
    # Limpiamos espacios en valores
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Convertimos a lista de dicts
    filas = df.to_dict(orient='records')
    df['mes'] = df['fecha'].dt.to_period('M')

    ventas_por_mes = df.groupby('mes').apply(lambda d: (d['cantidad'] * d['precio']).sum())

    ventas_por_mes = ventas_por_mes.sort_index()

    print("Ventas por mes:")

    print(ventas_por_mes)
    return filas


# 2. Calcular ventas totales por mes
# -----------------------------------------------------------------------------
# Implementaremos funciones para agrupar por mes y sumar ventas.


# 3. Determinar producto más vendido y con mayor ingresos
# -----------------------------------------------------------------------------
# Implementaremos funciones para obtener top por unidades y por ingresos.


# 4. Graficar ventas por mes
# -----------------------------------------------------------------------------
# Implementaremos una función que grafique la serie temporal de ventas mensuales.


# 5. Graficar top 5 productos por ingresos
# -----------------------------------------------------------------------------
# Implementaremos una función que grafique el top 5 por ingresos.


if __name__ == "__main__":
    # Ejecución manual rápida del paso 1 para validar carga
    try:
        datos = cargar_datos_csv()
        print(f"Filas cargadas: {len(datos)}")
    except Exception as exc:
        print(f"Error cargando CSV: {exc}")


