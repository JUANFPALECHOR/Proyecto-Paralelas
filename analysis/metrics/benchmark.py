import argparse
import json
import os
import time
from typing import List

import psutil

from ..engine.factory import get_engine


def run_benchmark(backend: str, news_csv: str, colcap_csv: str, rolling: List[int]):
    engine = get_engine(backend)  # type: ignore
    t0 = time.perf_counter()
    rss0 = psutil.Process().memory_info().rss

    news_df = engine.load_news(news_csv)
    t1 = time.perf_counter()
    news_feat = engine.compute_news_features(news_df)
    t2 = time.perf_counter()
    colcap_df = engine.load_colcap(colcap_csv)
    t3 = time.perf_counter()
    joined = engine.align_series(news_feat, colcap_df)
    t4 = time.perf_counter()
    results = engine.compute_correlations(joined, methods=["pearson", "spearman"], rolling_windows=rolling)
    t5 = time.perf_counter()

    rss1 = psutil.Process().memory_info().rss

    metrics = {
        "backend": backend,
        "timings_sec": {
            "load_news": round(t1 - t0, 4),
            "features": round(t2 - t1, 4),
            "load_colcap": round(t3 - t2, 4),
            "align": round(t4 - t3, 4),
            "correlate": round(t5 - t4, 4),
            "total": round(t5 - t0, 4),
        },
        "memory_bytes": {
            "rss_start": rss0,
            "rss_end": rss1,
            "delta": rss1 - rss0,
        },
        "results": results,
    }
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Benchmark de rendimiento y escalabilidad")
    parser.add_argument(
        "--backends",
        type=str,
        nargs="*",
        default=["pandas", "multiprocessing"],
        help="Lista de backends a evaluar",
    )
    parser.add_argument(
        "--news-csv",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", "..", "data", "output.csv"),
    )
    parser.add_argument("--colcap-csv", type=str, required=True)
    parser.add_argument("--rolling", type=int, nargs="*", default=[7, 14, 30])
    parser.add_argument("--out", type=str, default=os.path.join(os.getcwd(), "benchmark_results.json"))

    # Parallelization flags
    parser.add_argument("--mp-procs", type=int, default=None)
    parser.add_argument("--dask-nparts", type=int, default=None)
    parser.add_argument("--dask-distributed", action="store_true")
    parser.add_argument("--dask-scheduler", type=str, default=None)
    parser.add_argument("--spark-master", type=str, default=None)

    args = parser.parse_args()

    all_metrics = []
    for backend in args.backends:
        print(f"▶ Ejecutando benchmark backend={backend}")
        # build engine with config to include in metrics
        engine_cfg = {
            "backend": backend,
            "mp_procs": args.mp_procs,
            "dask_nparts": args.dask_nparts,
            "dask_distributed": args.dask_distributed,
            "dask_scheduler": args.dask_scheduler,
            "spark_master": args.spark_master,
        }
        m = run_benchmark(backend, args.news_csv, args.colcap_csv, args.rolling)
        m["engine_config"] = engine_cfg
        all_metrics.append(m)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, ensure_ascii=False, indent=2)

    print(f"✔ Benchmarks guardados en {args.out}")


if __name__ == "__main__":
    main()
