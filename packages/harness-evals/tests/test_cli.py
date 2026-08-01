"""CLI contract: eval list, dry-run plans, error exits, module entrypoint."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

import evals_testlib as tl

pytest.importorskip("harness_evals")
pytest.importorskip("harness_evals.cli")


@pytest.fixture
def config_file(tmp_path):
    cfg = tmp_path / "campaign-config.json"
    cfg.write_text("{}\n", encoding="utf-8")
    return cfg


def test_eval_list_exit_zero_and_names(stub_assets, capsys):
    code, out = tl.run_cli(["eval", "list"], capsys)
    assert code == 0
    assert "smoke" in out
    for scorer_name in ("dummy", "calibration", "drift", "completion", "cost", "safety"):
        assert scorer_name in out


def test_dry_run_prints_plan_and_creates_nothing(stub_assets, config_file, tmp_path, capsys):
    outdir = tmp_path / "results"
    code, out = tl.run_cli(
        ["eval", "run", "--benchmark", "smoke", "--config", str(config_file),
         "--output", str(outdir), "--dry-run"],
        capsys,
    )
    assert code == 0
    assert "smoke" in out
    assert "dry run" in out.lower() or "dry-run" in out.lower()
    assert not outdir.exists(), "dry run must not create the output dir"


def test_unknown_benchmark_exits_one(stub_assets, config_file, tmp_path, capsys):
    code, _ = tl.run_cli(
        ["eval", "run", "--benchmark", "no-such-benchmark", "--config",
         str(config_file), "--output", str(tmp_path / "results"), "--dry-run"],
        capsys,
    )
    assert code == 1


def test_missing_config_exits_one(stub_assets, tmp_path, capsys):
    code, _ = tl.run_cli(
        ["eval", "run", "--benchmark", "smoke", "--config",
         str(tmp_path / "does-not-exist.json"), "--output",
         str(tmp_path / "results"), "--dry-run"],
        capsys,
    )
    assert code == 1


def test_live_run_gated_to_phase_2d(stub_assets, config_file, tmp_path, capsys):
    from harness_evals import cli

    code = cli.main(
        ["eval", "run", "--benchmark", "smoke", "--config", str(config_file),
         "--output", str(tmp_path / "results")]
    )
    captured = capsys.readouterr()
    assert code == 1
    lowered = (captured.out + captured.err).lower()  # hint may go to stderr
    assert "phase 2d" in lowered or "dry-run" in lowered or "dry run" in lowered


def test_python_dash_m_entrypoint():
    env = dict(os.environ)
    env.pop("HARNESS_EVALS_ASSETS", None)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(tl.EVALS_SRC), str(tl.PROTOCOL_SRC)]
        + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
    )
    proc = subprocess.run(
        [sys.executable, "-m", "harness_evals.cli", "eval", "list"],
        cwd=str(tl.REPO_ROOT), env=env, capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
