# Análisis de Noticias vs COLCAP

Este módulo implementa un motor de análisis con múltiples backends (Pandas, Dask, Spark, Multiprocessing) para calcular correlaciones entre métricas agregadas de noticias y la serie temporal del índice COLCAP.

## Estructura

- `engine/`: Interfaces y backends
- `features/`: Extracción de características de noticias (sentimiento, longitud, conteo)
- `data_sources/`: Cargadores de datos (p.ej., COLCAP desde CSV)
- `scripts/`: CLI para correlación
- `metrics/`: Benchmarks de rendimiento y escalabilidad

## Uso

1. Asegúrate de tener el CSV de noticias (`data/output.csv`) generado por `ingestion` y un CSV de COLCAP con columnas `date` y `close`.

2. Correlación:

```bash
# Pandas
python -m analysis.scripts.correlate_news_colcap --backend pandas --colcap-csv path\a\colcap.csv --out correlation_results.json

# Multiprocessing (control de procesos)
python -m analysis.scripts.correlate_news_colcap --backend multiprocessing --mp-procs 8 --colcap-csv path\a\colcap.csv

# Dask (particiones y modo distribuido)
python -m analysis.scripts.correlate_news_colcap --backend dask --dask-nparts 16 --colcap-csv path\a\colcap.csv
python -m analysis.scripts.correlate_news_colcap --backend dask --dask-distributed --dask-scheduler tcp://scheduler:8786 --colcap-csv path\a\colcap.csv

# Spark (master configurable)
python -m analysis.scripts.correlate_news_colcap --backend spark --spark-master local[*] --colcap-csv path\a\colcap.csv
```

3. Benchmark:

```bash
python -m analysis.metrics.benchmark --backends pandas multiprocessing dask --mp-procs 8 --dask-nparts 16 --colcap-csv path\a\colcap.csv --out benchmark_results.json
```

## Backends

- `pandas`: buena base para datos medianos.
- `multiprocessing`: paraleliza tareas de parsing/cálculo en CPU únicas.
- `dask`: escala en un clúster Dask (instalación opcional). Puedes usar `--dask-distributed` y `--dask-scheduler` para conectarte al scheduler.
- `spark`: soportado opcionalmente si existe PySpark. Configura `--spark-master` para usar `local[*]` o un cluster.

## Requisitos

Instala las dependencias desde el `requirements.txt` de la raíz del proyecto:

```powershell
cd "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas"
& "C:\Users\Windows 11\Desktop\PFParalelas\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

## Paralelización de la carga
- Multiprocessing: controla `--mp-procs` para fijar el tamaño del pool.
- Dask: controla `--dask-nparts` para particionar el DataFrame y `--dask-distributed` para ejecutar en cluster.
- Spark: define `--spark-master` y, opcionalmente, configs adicionales vía servicio.
