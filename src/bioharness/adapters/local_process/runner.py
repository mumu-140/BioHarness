import socket
import subprocess

from bioharness.ports.workflow_executor import ExecutionBinding, InvocationSpec

from .probe import linux_process_start_token


class LocalProcessRunner:
    def spawn(self, invocation: InvocationSpec) -> ExecutionBinding:
        invocation.stdout_path.parent.mkdir(parents=True, exist_ok=True)
        invocation.stderr_path.parent.mkdir(parents=True, exist_ok=True)
        with invocation.stdout_path.open("ab") as stdout_handle, invocation.stderr_path.open("ab") as stderr_handle:
            process = subprocess.Popen(
                invocation.argv,
                cwd=invocation.cwd,
                env=invocation.env,
                stdout=stdout_handle,
                stderr=stderr_handle,
                start_new_session=True,
                shell=False,
            )
        return ExecutionBinding(
            host=socket.gethostname(),
            pid=process.pid,
            process_start_token=linux_process_start_token(process.pid),
            external_execution_id=None,
            metadata={"argv": list(invocation.argv), "cwd": str(invocation.cwd)},
        )
