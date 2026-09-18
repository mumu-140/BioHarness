import os
from pathlib import Path

from bioharness.ports.workflow_executor import ExecutionBinding


def linux_process_start_token(pid: int) -> str | None:
    stat_path = Path(f"/proc/{pid}/stat")
    try:
        raw = stat_path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, OSError):
        return None
    close = raw.rfind(")")
    if close < 0:
        return None
    fields_after_comm = raw[close + 2 :].split()
    if len(fields_after_comm) <= 19:
        return None
    return fields_after_comm[19]


class LocalProcessProbe:
    def probe(self, binding: ExecutionBinding) -> bool | None:
        if binding.pid is None:
            return None
        try:
            os.kill(binding.pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return None
        current_token = linux_process_start_token(binding.pid)
        if binding.process_start_token is None or current_token is None:
            return None
        if current_token != binding.process_start_token:
            return None
        return True
