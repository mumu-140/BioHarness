from datetime import datetime, timezone

import pytest

from bioharness.application.validate_run import ValidationService
from bioharness.domain.validation import (
    ValidationOutcome,
    ValidationProfile,
    ValidationRequirement,
)

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class ValidationRepo:
    def __init__(self):
        self.profiles = {}
        self.reports = {}
        self.evaluations = []

    def add_profile(self, value):
        self.profiles[(value.profile_id, value.revision)] = value

    def get_profile(self, profile_id, revision):
        return self.profiles.get((profile_id, revision))

    def add_report(self, value):
        self.reports[value.id] = value

    def get_report(self, value_id):
        return self.reports.get(value_id)

    def add_evaluation(self, value):
        self.evaluations.append(value)


class Uow:
    def __init__(self, repo): self.validation=repo
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def commit(self): pass
    def rollback(self): pass


def candidate_v1():
    return ValidationProfile(
        profile_id="candidate",
        revision="1",
        requirements=(
            ValidationRequirement(kind="provider_contract", allowed_outcomes=(ValidationOutcome.PASS, ValidationOutcome.PASS_WITH_LIMITATIONS)),
            ValidationRequirement(kind="artifact_integrity", allowed_outcomes=(ValidationOutcome.PASS,)),
            ValidationRequirement(kind="provenance_completeness", allowed_outcomes=(ValidationOutcome.PASS,)),
        ),
    )


def test_provider_pass_alone_does_not_open_generic_candidate_gate():
    repo=ValidationRepo(); repo.add_profile(candidate_v1())
    service=ValidationService(uow_factory=lambda: Uow(repo), clock=lambda: NOW)
    provider=service.report(
        kind="provider_contract", subject_type="run_attempt", subject_id="ra-1",
        validator="provider", validator_revision="1", outcome=ValidationOutcome.PASS,
        evidence_refs=("event:provider",),
    )
    evaluation=service.evaluate("candidate", "1", (provider.id,))
    assert evaluation.outcome is ValidationOutcome.FAIL


def test_all_required_typed_reports_pass_candidate_gate():
    repo=ValidationRepo(); repo.add_profile(candidate_v1())
    service=ValidationService(uow_factory=lambda: Uow(repo), clock=lambda: NOW)
    reports=[
        service.report(kind="provider_contract", subject_type="run_attempt", subject_id="ra-1", validator="provider", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:1",)),
        service.report(kind="artifact_integrity", subject_type="run_attempt", subject_id="ra-1", validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:2",)),
        service.report(kind="provenance_completeness", subject_type="run_attempt", subject_id="ra-1", validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:3",)),
    ]
    evaluation=service.evaluate("candidate", "1", tuple(r.id for r in reports))
    assert evaluation.outcome is ValidationOutcome.PASS
    assert evaluation.report_ids == tuple(r.id for r in reports)


def test_mixed_subject_reports_cannot_satisfy_one_gate():
    repo=ValidationRepo(); repo.add_profile(candidate_v1())
    service=ValidationService(uow_factory=lambda: Uow(repo), clock=lambda: NOW)
    reports=[
        service.report(kind="provider_contract", subject_type="run_attempt", subject_id="ra-1", validator="provider", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:1",)),
        service.report(kind="artifact_integrity", subject_type="run_attempt", subject_id="ra-2", validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:2",)),
        service.report(kind="provenance_completeness", subject_type="run_attempt", subject_id="ra-1", validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:3",)),
    ]
    with pytest.raises(ValueError, match="subject"):
        service.evaluate("candidate", "1", tuple(r.id for r in reports))
    assert repo.evaluations == []


def test_profile_revision_is_historical_not_rewritten():
    repo=ValidationRepo(); v1=candidate_v1(); repo.add_profile(v1)
    service=ValidationService(uow_factory=lambda: Uow(repo), clock=lambda: NOW)
    reports=[
        service.report(kind="provider_contract", subject_type="run_attempt", subject_id="ra-1", validator="provider", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:1",)),
        service.report(kind="artifact_integrity", subject_type="run_attempt", subject_id="ra-1", validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:2",)),
        service.report(kind="provenance_completeness", subject_type="run_attempt", subject_id="ra-1", validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:3",)),
    ]
    old=service.evaluate("candidate", "1", tuple(r.id for r in reports))
    v2=ValidationProfile(
        profile_id="candidate", revision="2",
        requirements=v1.requirements + (ValidationRequirement(kind="reproducibility", allowed_outcomes=(ValidationOutcome.PASS,)),),
    )
    repo.add_profile(v2)
    new=service.evaluate("candidate", "2", tuple(r.id for r in reports))
    assert old.profile_revision == "1" and old.outcome is ValidationOutcome.PASS
    assert new.profile_revision == "2" and new.outcome is ValidationOutcome.FAIL
    assert repo.evaluations[0] == old


def test_conflicting_duplicate_required_kind_is_rejected():
    repo=ValidationRepo(); repo.add_profile(candidate_v1())
    service=ValidationService(uow_factory=lambda: Uow(repo), clock=lambda: NOW)
    reports=[
        service.report(kind="provider_contract", subject_type="run_attempt", subject_id="ra-1", validator="provider-a", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:pass",)),
        service.report(kind="provider_contract", subject_type="run_attempt", subject_id="ra-1", validator="provider-b", validator_revision="1", outcome=ValidationOutcome.FAIL, evidence_refs=("e:fail",)),
        service.report(kind="artifact_integrity", subject_type="run_attempt", subject_id="ra-1", validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:2",)),
        service.report(kind="provenance_completeness", subject_type="run_attempt", subject_id="ra-1", validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=("e:3",)),
    ]
    with pytest.raises(ValueError, match="exactly one"):
        service.evaluate("candidate", "1", tuple(r.id for r in reports))
    assert repo.evaluations == []


@pytest.mark.parametrize(
    "outcome",
    [ValidationOutcome.PASS, ValidationOutcome.PASS_WITH_LIMITATIONS],
)
def test_positive_validation_report_requires_evidence(outcome):
    repo=ValidationRepo()
    service=ValidationService(uow_factory=lambda: Uow(repo), clock=lambda: NOW)
    with pytest.raises(ValueError, match="evidence"):
        service.report(
            kind="provider_contract",
            subject_type="run_attempt",
            subject_id="ra-1",
            validator="provider",
            validator_revision="1",
            outcome=outcome,
            evidence_refs=(),
        )
    assert repo.reports == {}
