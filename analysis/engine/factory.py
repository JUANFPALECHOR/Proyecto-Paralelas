from typing import Literal, Any

from .base import AnalysisEngine
from .backends.pandas_engine import PandasEngine
try:
    from .backends.dask_engine import DaskEngine
except Exception:
    DaskEngine = None  # optional
try:
    from .backends.spark_engine import SparkEngine
except Exception:
    SparkEngine = None  # optional
from .backends.mp_engine import MultiprocessingEngine


BackendName = Literal["pandas", "dask", "spark", "multiprocessing"]


def get_engine(backend: BackendName = "pandas", **kwargs: Any) -> AnalysisEngine:
    if backend == "pandas":
        return PandasEngine()
    if backend == "multiprocessing":
        # kwargs: nprocs
        return MultiprocessingEngine(nprocs=kwargs.get("nprocs"))
    if backend == "dask":
        if DaskEngine is None:
            raise ImportError("Dask is not available. Install dask[dataframe].")
        # kwargs: npartitions, distributed, scheduler_address
        return DaskEngine(
            npartitions=kwargs.get("npartitions"),
            distributed=kwargs.get("distributed", False),
            scheduler_address=kwargs.get("scheduler_address"),
        )
    if backend == "spark":
        if SparkEngine is None:
            raise ImportError("PySpark is not available. Install pyspark.")
        # kwargs: master, configs
        return SparkEngine(master=kwargs.get("master"), configs=kwargs.get("configs"))
    raise ValueError(f"Unknown backend: {backend}")
