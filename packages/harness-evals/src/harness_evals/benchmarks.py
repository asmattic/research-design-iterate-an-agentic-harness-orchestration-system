"""Benchmark registry read from manifest JSON files at ``assets_root()/benchmarks``."""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

from ._assets import assets_root
from .scorers import SCORER_NAMES


@dataclass(frozen=True)
class Benchmark:
    """One benchmark as described by its on-disk manifest."""

    name: str
    description: str
    scorer_names: tuple[str, ...]
    status: str  # "planned" | "available"
    manifest_path: pathlib.Path


def _load_manifest(path: pathlib.Path) -> Benchmark | None:
    """Parse one manifest file; return None for files that are not manifests.

    Non-JSON files (and JSON that is not an object with a ``name``) are
    skipped. A manifest naming an unknown scorer raises ValueError.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("name"), str):
        return None
    scorers = tuple(data.get("scorers", ()))
    for scorer in scorers:
        if scorer not in SCORER_NAMES:
            raise ValueError(
                f"benchmark manifest {path} names unknown scorer {scorer!r}; "
                f"known scorers: {', '.join(SCORER_NAMES)}"
            )
    return Benchmark(
        name=data["name"],
        description=str(data.get("description", "")),
        scorer_names=scorers,
        status=str(data.get("status", "planned")),
        manifest_path=path,
    )


def list_benchmarks() -> list[Benchmark]:
    """Return all benchmarks found under ``assets_root()/benchmarks``, by name."""
    benchmarks_dir = assets_root() / "benchmarks"
    out: list[Benchmark] = []
    if benchmarks_dir.is_dir():
        for path in sorted(benchmarks_dir.glob("*.json")):
            bench = _load_manifest(path)
            if bench is not None:
                out.append(bench)
    return sorted(out, key=lambda b: b.name)


def get_benchmark(name: str) -> Benchmark:
    """Return the benchmark named *name*; KeyError lists the known names."""
    benchmarks = {b.name: b for b in list_benchmarks()}
    try:
        return benchmarks[name]
    except KeyError:
        known = ", ".join(sorted(benchmarks)) or "(none found)"
        raise KeyError(
            f"unknown benchmark {name!r}; known benchmarks: {known}"
        ) from None
