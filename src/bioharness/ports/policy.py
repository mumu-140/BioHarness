from typing import Any, Protocol

from bioharness.domain.policy import PolicyDecision


class PolicyEvaluator(Protocol):
    def evaluate(
        self, actor: str, action: str, resource: str, context: dict[str, Any]
    ) -> PolicyDecision: ...
