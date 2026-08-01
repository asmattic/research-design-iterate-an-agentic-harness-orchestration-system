"""Phase 2B behavior contract for harness_reference.event_log.

Split out of test_phase2b_behavior.py so each module's implementation lane
owns exactly one behavior-test file. While the module is a stub, every test
carries strict xfail; the implementing lane removes the markers and these
become the acceptance tests.
"""

from __future__ import annotations

import json

import pytest

hr = pytest.importorskip("harness_reference", reason="stub lane not landed")
if not hasattr(hr, "__version__"):
    pytest.skip("harness_reference is a bare namespace package (stub lane not landed)",
                allow_module_level=True)
event_log = pytest.importorskip("harness_reference.event_log")


def xfail2b(reason: str):
    return pytest.mark.xfail(strict=True, raises=NotImplementedError,
                             reason=f"Phase 2B: {reason}")


@xfail2b("EventLog append returns event_id; events() filters; JSONL is append-only")
def test_event_log_append_filter_jsonl(tmp_log_path, valid_event):
    log = event_log.EventLog(tmp_log_path)
    eid = log.append(valid_event)
    assert eid == valid_event["event_id"]
    assert len(log) == 1
    assert [e["event_id"] for e in log.events(kind=valid_event["kind"])] == [eid]
    assert list(log.events(kind="decision")) == []
    assert [e["event_id"] for e in log.events(task_id=valid_event["task_id"])] == [eid]
    second = dict(valid_event, event_id="evt_01jg8w3k9r2qazy1")
    log.append(second)
    lines = tmp_log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["event_id"] == eid
    assert json.loads(lines[1])["event_id"] == second["event_id"]


@xfail2b("schema-invalid envelopes are rejected with ValueError, nothing written")
def test_event_log_rejects_invalid(tmp_log_path):
    log = event_log.EventLog(tmp_log_path)
    with pytest.raises(ValueError):
        log.append({"kind": "not-a-real-kind"})
    assert len(log) == 0
