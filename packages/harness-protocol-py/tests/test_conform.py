"""Conformance-runner contract tests for harness_protocol.conform.main."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

harness_protocol = pytest.importorskip("harness_protocol")
conform = pytest.importorskip("harness_protocol.conform")

from conftest import collect_examples

# tests/ -> harness-protocol-py/ -> packages/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
PY_SRC = REPO_ROOT / "packages" / "harness-protocol-py" / "src"


def _copy_assets(tmp_path):
    """Copy the real assets tree (schemas/ + examples/) into tmp_path/assets."""
    real = Path(harness_protocol.assets_root())
    dest = tmp_path / "assets"
    shutil.copytree(real, dest)
    return dest


def test_main_passes_against_repo_assets(capsys, monkeypatch):
    monkeypatch.delenv("HARNESS_PROTOCOL_ASSETS", raising=False)
    rc = conform.main([])
    captured = capsys.readouterr()
    assert rc == 0, f"conform.main([]) returned {rc}; output:\n{captured.out}{captured.err}"
    assert "conformance:" in (captured.out + captured.err)


def test_invalid_example_that_validates_is_a_conformance_failure(tmp_path):
    """An invalid-* fixture that actually validates must fail conformance."""
    assets = _copy_assets(tmp_path)

    valid_examples = collect_examples("valid")
    assert valid_examples, (
        "Need at least one valid-*.json example in the real assets to build "
        "the corrupted-assets scenario"
    )
    name, valid_path = valid_examples[0]

    plant_dir = assets / "examples" / name
    plant_dir.mkdir(parents=True, exist_ok=True)
    instance = json.loads(valid_path.read_text(encoding="utf-8"))
    # Sanity: the planted instance really does validate against its schema.
    assert harness_protocol.is_valid(name, instance) is True
    (plant_dir / "invalid-actually-valid.json").write_text(
        json.dumps(instance, indent=2), encoding="utf-8"
    )

    rc = conform.main(["--assets", str(assets)])
    assert rc != 0, (
        f"conform.main returned 0 even though examples/{name}/"
        "invalid-actually-valid.json validates — an 'invalid' example that "
        "passes must be reported as a conformance failure"
    )


def test_missing_schemas_is_not_a_pass(tmp_path):
    """Empty schemas/ dir: main must not return 0 (exception also acceptable)."""
    assets = tmp_path / "assets"
    (assets / "schemas").mkdir(parents=True)
    (assets / "examples").mkdir()
    try:
        rc = conform.main(["--assets", str(assets)])
    except Exception:
        # Raising (e.g. RuntimeError from asset resolution) is an acceptable
        # failure signal; the only unacceptable outcome is a clean 0.
        return
    assert rc != 0, "conform.main returned 0 against an assets dir with no schemas"


@pytest.mark.skipif(
    not PY_SRC.is_dir(),
    reason="packages/harness-protocol-py/src not present yet",
)
def test_module_entrypoint_runs():
    env = dict(os.environ)
    env.pop("HARNESS_PROTOCOL_ASSETS", None)
    env["PYTHONPATH"] = str(PY_SRC) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-m", "harness_protocol.conform"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"python -m harness_protocol.conform exited {proc.returncode}\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
