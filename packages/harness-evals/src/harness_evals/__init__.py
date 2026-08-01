"""harness-evals: eval-harness skeleton — CLI, registries, dummy scorer."""

from __future__ import annotations

from ._assets import assets_root
from .benchmarks import Benchmark, get_benchmark, list_benchmarks
from .scorers import SCORER_NAMES, ScoreResult, get_scorer

__version__ = "0.2.0"

__all__ = [
    "Benchmark",
    "SCORER_NAMES",
    "ScoreResult",
    "assets_root",
    "get_benchmark",
    "get_scorer",
    "list_benchmarks",
    "__version__",
]
