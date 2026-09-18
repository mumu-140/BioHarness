import json
import os
import socket
import subprocess

from bioharness.ports.workflow_executor import ExecutionBinding, InvocationSpec

from .probe import linux_process_start_token


def _write_process_record(invocation: InvocationSpec, binding: ExecutionBinding) -> str:
    record_path = invocation.stdout_path.parent / "process.json"
    temporary = record_path.with_name(record_path.name + ".tmp")
    payload = {
        "schema_version": "bioharness.local-process.v1",
        "host": binding.host,
        "pid": binding.pid,
        "process_start_token": binding.process_start_token,
        "external_execution_id": binding.external_execution_id,
        "argv": list(invocation.argv),
        "cwd": str(invocation.cwd),
    }
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, record_path)
    return str(record_path)


class LocalProcessRunner:
    def spawn(self, invocation: InvocationSpec) -> ExecutionBinding:
        invocation.stdout_path.parent.mkdir(parents=True, exist_ok=True)
        invocation.stderr_path.parent.mkdir(parents=True, exist_ok=True)
        with invocation.stdout_path.open("ab") as stdout_handle, invocation.stderr_path.open(
            "ab"
        ) as stderr_handle:
            process = subprocess.Popen(
                invocation.argv,
                cwd=invocation.cwd,
                env=invocation.env,
                stdout=stdout_handle,
                stderr=stderr_handle,
                start_new_session=True,
                shell=False,
            )
        binding = ExecutionBinding(
            host=socket.gethostname(),
            pid=process.pid,
            process_start_token=linux_process_start_token(process.pid),
            external_execution_id=None,
        )
        try:
            process_record = _write_process_record(invocation, binding)
        except Exception as exc:
            raise RuntimeError(
                "external process started but recovery evidence could not be persisted"
            ) from exc
        return binding.model_copy(
            update={
                "metadata": {
                    "argv": list(invocation.argv),
                    "cwd": str(invocation.cwd),
                    "process_record": process_record,
                }
            }
        )
