"""The ``harness-verify`` CLI: ``list`` verifiers, ``run`` a claims file.

Exit codes for ``run``: 0 = no fails (abstains don't fail the run),
1 = at least one fail, 2 = usage error or unreadable/invalid claims file.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import sys
from collections import Counter

from harness_verifier.runner import run_claims

_SEMANTICS = {
    "code_test_runner": "run pytest on a target path; the exit code decides",
    "schema_validator": "validate an instance against a harness-protocol schema",
    "citation_resolver": "check a citation URL resolves (abstains when offline)",
    "numeric_bound": "check low <= value <= high for the provided bounds",
    "type_check": "check a value's runtime type against a JSON-ish type name",
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harness-verify", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list the built-in verifiers")

    run = sub.add_parser("run", help="run every claim in a JSON claims file")
    run.add_argument(
        "--claims",
        required=True,
        help="path to a JSON file holding an array of claim objects",
    )
    return parser


def _cmd_list() -> int:
    for name, semantics in _SEMANTICS.items():
        print(f"{name}  —  {semantics}")
    return 0


def _cmd_run(claims_path: str) -> int:
    path = pathlib.Path(claims_path)
    try:
        claims = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read claims file: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: claims file is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(claims, list) or not all(
        isinstance(claim, dict) for claim in claims
    ):
        print(
            "error: claims file must hold a JSON array of claim objects",
            file=sys.stderr,
        )
        return 2

    results = run_claims(claims)
    for result in results:
        print(json.dumps(dataclasses.asdict(result), sort_keys=True))
    counts = Counter(result.result for result in results)
    print(
        f"{len(results)} claims: {counts['pass']} pass, "
        f"{counts['fail']} fail, {counts['abstain']} abstain",
        file=sys.stderr,
    )
    return 1 if counts["fail"] else 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "list":
        return _cmd_list()
    return _cmd_run(args.claims)


if __name__ == "__main__":
    raise SystemExit(main())
