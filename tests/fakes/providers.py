from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from bioharness.domain.policy import PolicyDecision, PolicyOutcome
from bioharness.ports.data_provider import ProviderResolution, ProviderResource
from bioharness.ports.workflow_executor import (
    ExecutionBinding,
    ExecutionDescriptor,
    ExecutionEvidence,
    ExecutorCapabilities,
    InvocationSpec,
)


class FakeDataProvider:
    def __init__(self, resolution: ProviderResolution | None = None, order: list | None = None):
        self.calls: list[tuple[tuple[str, ...], dict[str, Any]]] = []
        self.order = order
        self.resolution = resolution or ProviderResolution(
            provider="fake",
            provider_revision="r1",
            resources=(
                ProviderResource(
                    logical_uri="provider://resource/A",
                    resource_type="generic",
                    biological_identity={"name": "A"},
                ),
            ),
        )

    def resolve(self, logical_resources: tuple[str, ...], context: dict[str, Any]) -> ProviderResolution:
        self.calls.append((logical_resources, context))
        if self.order is not None:
            self.order.append(("provider", "resolve"))
        return self.resolution


class FakeWorkflowExecutor:
    def __init__(
        self,
        *,
        evidence: ExecutionEvidence | None = None,
        artifacts: tuple[dict[str, Any], ...] = (),
        invocation: InvocationSpec | None = None,
    ):
        self.calls: list[tuple[str, Any]] = []
        self.prepare_calls = 0
        self._evidence = evidence or ExecutionEvidence(
            active=None, terminal_outcome=None, exit_code=None
        )
        self._artifacts = artifacts
        self._invocation = invocation or InvocationSpec(
            argv=("python", "-c", "pass"),
            cwd=Path("."),
            env={},
            stdout_path=Path("stdout.log"),
            stderr_path=Path("stderr.log"),
        )

    def capabilities(self) -> ExecutorCapabilities:
        return ExecutorCapabilities(
            mode="synchronous_process",
            native_idempotency_key=False,
            durable_external_execution_id=False,
            poll=False,
            reconcile_after_disconnect="limited",
            cancellation="unsupported",
            logs=True,
            trace=False,
        )

    def prepare(self, execution: ExecutionDescriptor) -> InvocationSpec:
        self.prepare_calls += 1
        self.calls.append(("prepare", execution))
        return self._invocation

    def inspect(self, binding: ExecutionBinding | None, attempt_payload: dict[str, Any]) -> ExecutionEvidence:
        self.calls.append(("inspect", (binding, attempt_payload)))
        return self._evidence

    def discover_artifacts(self, attempt_payload: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        self.calls.append(("discover_artifacts", attempt_payload))
        return self._artifacts


class FakeProcessRunner:
    def __init__(self, *, raise_after_possible_spawn: bool = False):
        self.calls: list[InvocationSpec] = []
        self.spawn_calls = 0
        self.raise_after_possible_spawn = raise_after_possible_spawn

    def spawn(self, invocation: InvocationSpec) -> ExecutionBinding:
        self.spawn_calls += 1
        self.calls.append(invocation)
        if self.raise_after_possible_spawn:
            raise RuntimeError("ambiguous spawn outcome")
        return ExecutionBinding(
            host="fake-host",
            pid=1234,
            process_start_token="1",
            external_execution_id=None,
        )


class FakePolicyEvaluator:
    def __init__(self, denied_actions: set[str] | None = None, order: list | None = None):
        self.denied_actions = denied_actions or set()
        self.order = order
        self.calls: list[tuple[str, str, str, dict[str, Any]]] = []

    def evaluate(self, actor: str, action: str, resource: str, context: dict[str, Any]) -> PolicyDecision:
        self.calls.append((actor, action, resource, context))
        if self.order is not None:
            self.order.append(("policy", action))
        outcome = PolicyOutcome.DENY if action in self.denied_actions else PolicyOutcome.ALLOW
        return PolicyDecision(
            id=uuid4(),
            actor=actor,
            action=action,
            resource=resource,
            policy_revision="fake-policy-v1",
            outcome=outcome,
            decided_at=datetime.now(timezone.utc),
        )
