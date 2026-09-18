from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID, uuid4

from bioharness.domain.data import ResolvedDataRef
from bioharness.domain.policy import PolicyOutcome


class ResolutionDenied(RuntimeError):
    pass


class TaskNotFound(LookupError):
    pass


class ResolutionService:
    def __init__(
        self,
        *,
        policy,
        provider,
        uow_factory,
        clock: Callable[[], datetime] | None = None,
    ):
        self.policy = policy
        self.provider = provider
        self.uow_factory = uow_factory
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def resolve(self, task_id: UUID, actor: str) -> tuple[ResolvedDataRef, ...]:
        with self.uow_factory() as uow:
            task = uow.planning.get_task(task_id)
            if task is None:
                raise TaskNotFound(str(task_id))

        decision = self.policy.evaluate(
            actor,
            "read_resolve",
            f"task:{task_id}",
            {"task_revision": task.revision},
        )
        with self.uow_factory() as uow:
            uow.planning.add_policy_decision(decision)
            uow.commit()

        if decision.outcome in {
            PolicyOutcome.DENY,
            PolicyOutcome.REQUIRE_APPROVAL,
        }:
            raise ResolutionDenied(
                f"resolution not authorized: {decision.outcome.value}"
            )

        logical_resources = tuple(task.biological_scope.get("resources", ()))
        resolution = self.provider.resolve(
            logical_resources,
            {"task_id": str(task.id), "task_revision": task.revision},
        )
        now = self.clock()
        refs = tuple(
            ResolvedDataRef(
                id=uuid4(),
                provider=resolution.provider,
                provider_revision=resolution.provider_revision,
                resource_type=resource.resource_type,
                logical_uri=resource.logical_uri,
                content_sha256=resource.content_identity.get("content_sha256"),
                manifest_sha256=resource.content_identity.get("manifest_sha256"),
                member_manifest_sha256=resource.content_identity.get(
                    "member_manifest_sha256"
                ),
                biological_identity=resource.biological_identity,
                metadata={
                    **resource.metadata,
                    "provider_evidence": list(resolution.evidence),
                },
                resolved_at=now,
            )
            for resource in resolution.resources
        )
        with self.uow_factory() as uow:
            for ref in refs:
                uow.planning.add_data_ref(ref)
            uow.commit()
        return refs
