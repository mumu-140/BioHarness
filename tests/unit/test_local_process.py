import os
import sys

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
