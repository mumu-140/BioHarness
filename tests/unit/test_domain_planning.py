from datetime import datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from bioharness.domain.assessment import AssessmentStatus, ScientificAssessment
from bioharness.domain.data import ResolvedDataRef
from bioharness.domain.policy import PolicyDecision, PolicyOutcome
from bioharness.domain.task import OutputIntent, ScientificTaskSpec

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def test_task_spec_is_frozen_and_excludes_provider_defaults():
    task = ScientificTaskSpec(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        revision=1,
        question="Build a phylogeny for requested proteins",
        requested_inference="protein phylogeny",
        analysis_class="phylogeny",
        biological_scope={"resources": ["provider://proteome/A"]},
        output_intent=OutputIntent.CANDIDATE,
        unresolved_fields=(),
        created_at=NOW,
    )
    assert "min_seqs" not in type(task).model_fields
    with pytest.raises(ValidationError):
        task.revision = 2


def test_resolved_data_ref_rejects_non_sha256_digest():
    with pytest.raises(ValidationError):
        ResolvedDataRef(
            id=UUID("00000000-0000-0000-0000-000000000002"),
            provider="fake",
            provider_revision="r1",
            resource_type="proteome",
            logical_uri="provider://proteome/A",
            content_sha256="abc",
            biological_identity={"species": "A"},
            resolved_at=NOW,
        )


def test_scientific_assessment_has_explicit_status_and_dependency_fingerprint():
    assessment = ScientificAssessment(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        task_spec_id=UUID("00000000-0000-0000-0000-000000000001"),
        task_spec_revision=1,
        resolved_data_ref_ids=(UUID("00000000-0000-0000-0000-000000000002"),),
        scientific_contract_id="phylogeny",
        scientific_contract_revision="1",
        dependency_fingerprint="a" * 64,
        status=AssessmentStatus.ANALYSIS_SUPPORTED_WITH_LIMITATIONS,
        limitations=("candidate only",),
        assessed_at=NOW,
    )
    assert assessment.status is AssessmentStatus.ANALYSIS_SUPPORTED_WITH_LIMITATIONS


def test_policy_decision_keeps_warning_obligations_explicit():
    decision = PolicyDecision(
        id=UUID("00000000-0000-0000-0000-000000000004"),
        actor="researcher",
        action="run.start",
        resource="runspec:1",
        policy_revision="p1",
        outcome=PolicyOutcome.ALLOW_WITH_WARNING,
        warnings=("candidate only",),
        obligations=("preserve evidence",),
        decided_at=NOW,
    )
    assert decision.warnings == ("candidate only",)
    assert decision.obligations == ("preserve evidence",)
