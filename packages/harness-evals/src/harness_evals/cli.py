"""The ``harness`` CLI: ``harness eval list`` and ``harness eval run``.

Live benchmark execution is gated until Phase 2D (ROUND-2-PLAN §8 risk
mitigation): without ``--dry-run`` the run command refuses cleanly.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from ._assets import assets_root
from .benchmarks import get_benchmark, list_benchmarks
from .scorers import SCORER_NAMES


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harness", description=__doc__)
    top = parser.add_subparsers(dest="command", required=True)
    evalp = top.add_parser("eval", help="run and inspect eval benchmarks")
    sub = evalp.add_subparsers(dest="subcommand", required=True)

    sub.add_parser("list", help="list known benchmarks and scorers")

    run = sub.add_parser("run", help="run one benchmark (dry-run only in Phase 2A)")
    run.add_argument("--benchmark", required=True, help="benchmark name")
    run.add_argument("--config", required=True, help="path to a run config file")
    run.add_argument("--output", required=True, help="output directory for results")
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="print the execution plan without side effects",
    )
    return parser


def _scorer_note(name: str) -> str:
    return "real" if name == "dummy" else "stub — Phase 2D"


def _cmd_list() -> int:
    try:
        root = assets_root()
    except RuntimeError as exc:
        print(f"no benchmarks found ({exc})")
    else:
        benchmarks = list_benchmarks()
        if benchmarks:
            print("benchmarks:")
            for b in benchmarks:
                scorers = ", ".join(b.scorer_names) or "(none)"
                print(f"  {b.name}  [{b.status}]  scorers: {scorers}")
        else:
            print(f"no benchmarks found at {root / 'benchmarks'}")
    print("scorers:")
    for name in SCORER_NAMES:
        print(f"  {name}  ({_scorer_note(name)})")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    try:
        bench = get_benchmark(args.benchmark)
    except (KeyError, RuntimeError, ValueError) as exc:
        message = exc.args[0] if exc.args else str(exc)
        print(f"error: {message}", file=sys.stderr)
        return 1
    config = pathlib.Path(args.config)
    if not config.is_file():
        print(f"error: config file not found: {config}", file=sys.stderr)
        return 1
    if not args.dry_run:
        print(
            "live benchmark execution lands in Phase 2D; re-run with --dry-run",
            file=sys.stderr,
        )
        return 1
    print(f"execution plan for benchmark {bench.name!r} [{bench.status}]:")
    for name in bench.scorer_names:
        print(f"  scorer: {name}  ({_scorer_note(name)})")
    print(f"  config: {config}")
    print(f"  output dir: {args.output}")
    print("no side effects — dry run")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Argparse usage errors exit with argparse's code 2."""
    args = _build_parser().parse_args(argv)
    if args.subcommand == "list":
        return _cmd_list()
    return _cmd_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
