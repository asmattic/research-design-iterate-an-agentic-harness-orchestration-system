"""The ``harness`` CLI: ``harness eval list`` and ``harness eval run``.

``run`` without ``--dry-run`` executes the benchmark live: it scores every
scenario, writes the §14.8 ``report.md``, and (when the config carries a
``baseline``) exits via the §14.6 regression gate.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from ._assets import assets_root
from .benchmarks import Benchmark, get_benchmark, list_benchmarks
from .regression import regression_gate
from .report import write_report
from .runner import current_scores, discover_scenarios, load_config, run_benchmark
from .scorers import SCORER_NAMES


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harness", description=__doc__)
    top = parser.add_subparsers(dest="command", required=True)
    evalp = top.add_parser("eval", help="run and inspect eval benchmarks")
    sub = evalp.add_subparsers(dest="subcommand", required=True)

    sub.add_parser("list", help="list known benchmarks and scorers")

    run = sub.add_parser("run", help="run one benchmark")
    run.add_argument("--benchmark", required=True, help="benchmark name")
    run.add_argument("--config", required=True, help="path to a run config file")
    run.add_argument("--output", required=True, help="output directory for results")
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="print the execution plan without side effects",
    )
    return parser


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
        print(f"  {name}")
    return 0


def _cmd_run_live(bench: Benchmark, config: pathlib.Path, output: str) -> int:
    if bench.status != "available":
        print(
            f"error: benchmark {bench.name!r} is not runnable "
            f"(status: {bench.status})",
            file=sys.stderr,
        )
        return 1
    try:
        cfg = load_config(config)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    scenarios = discover_scenarios(bench.name)
    if not scenarios:
        print(
            f"error: no scenarios found for benchmark {bench.name!r} "
            "(no benchmarks/data/<name>/scenario-*.jsonl and no "
            "fixtures/recorded-campaign.jsonl)",
            file=sys.stderr,
        )
        return 1
    try:
        results = run_benchmark(bench, scenarios)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    report_path = write_report(bench.name, results, pathlib.Path(output))
    print(f"report: {report_path}")
    for result in results:
        print(f"  {result.scorer}: {result.value}")
    baseline = cfg.get("baseline")
    if baseline:
        return regression_gate(
            current_scores(results), baseline, cfg.get("thresholds", {})
        )
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
        return _cmd_run_live(bench, config, args.output)
    print(f"execution plan for benchmark {bench.name!r} [{bench.status}]:")
    for name in bench.scorer_names:
        print(f"  scorer: {name}")
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
