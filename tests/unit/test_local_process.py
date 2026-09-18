import json
import os
import sys

import pytest

import bioharness.adapters.local_process.runner as runner_module
from bioharness.adapters.local_process.probe import LocalProcessProbe
from bioharness.adapters.local_process.runner import LocalProcessRunner
from bioharness.ports.workflow_executor import InvocationSpec


def test_local_process_binding_captures_identity(tmp_path):
    invocation = InvocationSpec(
        argv=(sys.executable, "-c", "import time; time.sleep(2)"),
        cwd=tmp_path,
        env=dict(os.environ),
        stdout_path=tmp_path / "logs" / "stdout.log",
        stderr_path=tmp_path / "logs" / "stderr.log",
    )
    binding = LocalProcessRunner().spawn(invocation)
    assert binding.pid is not None
    assert binding.host
    if os.path.exists(f"/proc/{binding.pid}/stat"):
        assert binding.process_start_token is not None
        assert LocalProcessProbe().probe(binding) is True


def test_local_process_spawn_writes_recovery_record(tmp_path):
    invocation = InvocationSpec(
        argv=(sys.executable, "-c", "import time; time.sleep(2)"),
        cwd=tmp_path,
        env=dict(os.environ),
        stdout_path=tmp_path / "logs" / "stdout.log",
        stderr_path=tmp_path / "logs" / "stderr.log",
    )

    binding = LocalProcessRunner().spawn(invocation)

    record_path = invocation.stdout_path.parent / "process.json"
    assert record_path.is_file()
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["host"] == binding.host
    assert record["pid"] == binding.pid
    assert record["process_start_token"] == binding.process_start_token
    assert record["argv"] == list(invocation.argv)
    assert record["cwd"] == str(invocation.cwd)



def test_process_record_failure_after_spawn_is_ambiguous(tmp_path, monkeypatch):
    invocation = InvocationSpec(
        argv=(sys.executable, "-c", "pass"),
        cwd=tmp_path,
        env=dict(os.environ),
        stdout_path=tmp_path / "logs" / "stdout.log",
        stderr_path=tmp_path / "logs" / "stderr.log",
    )

    def fail_record(*args, **kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(runner_module, "_write_process_record", fail_record)

    with pytest.raises(RuntimeError, match="recovery evidence"):
        LocalProcessRunner().spawn(invocation)
