"""Conformance runner: check schemas are meta-valid, versioned, and match examples."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

from jsonschema import Draft202012Validator

from harness_protocol.assets import assets_root
from harness_protocol.validate import SCHEMA_NAMES

_ID_TEMPLATE = "https://harness.example/schemas/v0.2/{name}.schema.json"


def _load_json(path: pathlib.Path) -> Any:
    """Parse one JSON file."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _check_examples(
    name: str, validator: Draft202012Validator, examples: pathlib.Path
) -> tuple[int, int, int]:
    """Validate valid-*/invalid-* examples for one schema; return (passed, failed, seen)."""
    passed = failed = seen = 0
    for path in sorted(examples.glob("valid-*.json")):
        seen += 1
        errors = sorted(validator.iter_errors(_load_json(path)), key=str)
        if not errors:
            passed += 1
            print(f"OK   example {name}/{path.name}: valid as expected")
        else:
            failed += 1
            print(f"FAIL example {name}/{path.name}: expected valid, got: {errors[0].message}")
    for path in sorted(examples.glob("invalid-*.json")):
        seen += 1
        if any(True for _ in validator.iter_errors(_load_json(path))):
            passed += 1
            print(f"OK   example {name}/{path.name}: rejected as expected")
        else:
            failed += 1
            print(f"FAIL example {name}/{path.name}: expected FAIL but instance validated")
    return passed, failed, seen


def main(argv: list[str] | None = None) -> int:
    """Run all conformance checks; return 0 iff every check passed."""
    parser = argparse.ArgumentParser(
        prog="python -m harness_protocol.conform",
        description="Harness-protocol conformance runner (protocol v0.2).",
    )
    parser.add_argument(
        "--assets", metavar="DIR", default=None,
        help="assets root containing schemas/ and examples/ (overrides env/bundled/repo)",
    )
    args = parser.parse_args(argv)

    root = assets_root(args.assets)
    passed = failed = examples_seen = 0
    for name in SCHEMA_NAMES:
        try:
            schema = _load_json(root / "schemas" / f"{name}.schema.json")
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # missing file, bad JSON, or meta-invalid schema
            failed += 1
            print(f"FAIL schema {name}: not meta-valid ({type(exc).__name__}: {exc})")
            continue
        passed += 1
        print(f"OK   schema {name}: meta-valid")

        expected_id = _ID_TEMPLATE.format(name=name)
        if schema.get("$id") == expected_id:
            passed += 1
            print(f"OK   schema {name}: $id matches version path v0.2")
        else:
            failed += 1
            print(f"FAIL schema {name}: $id {schema.get('$id')!r} != {expected_id!r}")

        examples = root / "examples" / name
        if not examples.is_dir():
            print(f"WARN examples/{name}: directory missing, skipping (skeleton tolerance)")
            continue
        p, f, seen = _check_examples(name, Draft202012Validator(schema), examples)
        passed, failed, examples_seen = passed + p, failed + f, examples_seen + seen

    if examples_seen == 0:
        failed += 1
        print("FAIL examples: zero examples found across all schemas")

    print(f"conformance: {passed}/{passed + failed} checks passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
