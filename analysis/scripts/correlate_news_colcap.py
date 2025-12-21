import argparse
import json
import os
from typing import List

from ..engine.factory import get_engine


def main():
    parser = argparse.ArgumentParser(description="Correlación entre noticias y COLCAP")
    parser.add_argument(
        "--backend",
        type=str,
        default="pandas",
        choices=["pandas", "dask", "spark", "multiprocessing"],
        help="Backend de procesamiento",
    )
    # Parallelization options
    parser.add_argument("--mp-procs", type=int, default=None, help="Número de procesos para Multiprocessing")
    parser.add_argument("--dask-nparts", type=int, default=None, help="Número de particiones para Dask")
    parser.add_argument("--dask-distributed", action="store_true", help="Usar Dask Distributed")
    parser.add_argument("--dask-scheduler", type=str, default=None, help="Dirección del scheduler Dask")
    parser.add_argument("--spark-master", type=str, default=None, help="Master URL de Spark, p.ej. local[*] o spark://...")
    parser.add_argument(
        "--news-csv",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", "..", "data", "output.csv"),
        help="Ruta al CSV de noticias (salida de ingestion)",
    )
    parser.add_argument(
        "--colcap-csv",
        type=str,
        required=True,
        help="Ruta al CSV de COLCAP con columnas date, close",
    )
    parser.add_argument(
        "--rolling",
        type=int,
        nargs="*",
        default=[7, 14, 30],
        help="Ventanas para correlación rodante",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=os.path.join(os.getcwd(), "correlation_results.json"),
        help="Salida JSON con los resultados",
    )

    args = parser.parse_args()

    engine = get_engine(
        args.backend,
        nprocs=args.mp_procs,
        npartitions=args.dask_nparts,
        distributed=args.dask_distributed,
        scheduler_address=args.dask_scheduler,
        master=args.spark_master,
    )  # type: ignore

    # Load data
    news_df = engine.load_news(args.news_csv)
    news_feat = engine.compute_news_features(news_df)
    colcap_df = engine.load_colcap(args.colcap_csv)
    joined = engine.align_series(news_feat, colcap_df)

    results = engine.compute_correlations(joined, methods=["pearson", "spearman"], rolling_windows=args.rolling)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✔ Resultados guardados en {args.out}")


if __name__ == "__main__":
    main()
