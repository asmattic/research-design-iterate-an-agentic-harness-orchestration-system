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


def test_live_run_writes_section_14_8_report(stub_assets, config_file, tmp_path, capsys):
    outdir = tmp_path / "results"
    code, out = tl.run_cli(
        ["eval", "run", "--benchmark", "smoke", "--config", str(config_file),
         "--output", str(outdir)],
        capsys,
    )
    assert code == 0
    report = outdir / "report.md"
    assert report.is_file(), "live run must write report.md in the output dir"
    text = report.read_text(encoding="utf-8")
    assert "# Campaign smoke report" in text
    assert str(report) in out
    for scorer_name in ("dummy", "completion", "cost"):
        assert scorer_name in out  # one line per scorer


def test_live_run_unavailable_benchmark_exits_one(stub_assets, config_file, tmp_path, capsys):
    import json

    planned = {
        "name": "planned-bench",
        "description": "not yet runnable",
        "scorers": ["dummy"],
        "status": "planned",
    }
    (stub_assets / "benchmarks" / "planned-bench.json").write_text(
        json.dumps(planned), encoding="utf-8"
    )
    from harness_evals import cli

    code = cli.main(
        ["eval", "run", "--benchmark", "planned-bench", "--config",
         str(config_file), "--output", str(tmp_path / "results")]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert "planned" in captured.err


def test_live_run_malformed_config_exits_one(stub_assets, tmp_path, capsys):
    bad_cfg = tmp_path / "bad.json"
    bad_cfg.write_text("{not json", encoding="utf-8")
    from harness_evals import cli

    code = cli.main(
        ["eval", "run", "--benchmark", "smoke", "--config", str(bad_cfg),
         "--output", str(tmp_path / "results")]
    )
    capsys.readouterr()
    assert code == 1


def test_live_run_baseline_regression_exits_one(stub_assets, tmp_path, capsys):
    import json

    # Stub events resolve every claimed ticket, so completion scores 1.0;
    # demand an impossible completion baseline of 2.0 to trip the gate.
    cfg = tmp_path / "baseline-config.json"
    cfg.write_text(
        json.dumps(
            {"baseline": {"completion": 2.0}, "thresholds": {"completion": 0.05}}
        ),
        encoding="utf-8",
    )
    outdir = tmp_path / "results"
    code, _ = tl.run_cli(
        ["eval", "run", "--benchmark", "smoke", "--config", str(cfg),
         "--output", str(outdir)],
        capsys,
    )
    assert code == 1
    assert (outdir / "report.md").is_file(), "report is written even when gated"


def test_live_run_baseline_pass_exits_zero(stub_assets, tmp_path, capsys):
    import json

    cfg = tmp_path / "baseline-config.json"
    cfg.write_text(
        json.dumps(
            {
                "baseline": {"completion": 1.0, "cost": 10},
                "thresholds": {"completion": 0.05, "cost": 5000},
            }
        ),
        encoding="utf-8",
    )
    code, _ = tl.run_cli(
        ["eval", "run", "--benchmark", "smoke", "--config", str(cfg),
         "--output", str(tmp_path / "results")],
        capsys,
    )
    assert code == 0


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
