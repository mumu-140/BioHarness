from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID, uuid4

from bioharness.domain.validation import (
    ValidationEvaluation,
    ValidationOutcome,
    ValidationReport,
)


class ValidationProfileNotFound(LookupError):
    pass


class ValidationReportNotFound(LookupError):
    pass


class ValidationSubjectMismatch(ValueError):
    pass


class ValidationService:
    def __init__(self, *, uow_factory, clock: Callable[[], datetime] | None = None):
        self.uow_factory = uow_factory
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def report(
        self,
        *,
        kind: str,
        subject_type: str,
        subject_id: str,
        validator: str,
        validator_revision: str,
        outcome: ValidationOutcome,
        limitations: tuple[str, ...] = (),
        evidence_refs: tuple[str, ...] = (),
    ) -> ValidationReport:
        report = ValidationReport(
            id=uuid4(),
            kind=kind,
            subject_type=subject_type,
            subject_id=subject_id,
            validator=validator,
            validator_revision=validator_revision,
            outcome=outcome,
            limitations=limitations,
            evidence_refs=evidence_refs,
            created_at=self.clock(),
        )
        with self.uow_factory() as uow:
            uow.validation.add_report(report)
            uow.commit()
        return report

    def evaluate(
        self,
        profile_id: str,
        revision: str,
        report_ids: tuple[UUID, ...],
    ) -> ValidationEvaluation:
        with self.uow_factory() as uow:
            profile = uow.validation.get_profile(profile_id, revision)
            if profile is None:
                raise ValidationProfileNotFound(f"{profile_id}@{revision}")
            reports = []
            for report_id in report_ids:
                report = uow.validation.get_report(report_id)
                if report is None:
                    raise ValidationReportNotFound(str(report_id))
                reports.append(report)

        if reports:
            subject = (reports[0].subject_type, reports[0].subject_id)
            if any((report.subject_type, report.subject_id) != subject for report in reports[1:]):
                raise ValidationSubjectMismatch(
                    "validation reports for one evaluation must share the same subject"
                )

        all_requirements_met = True
        accepted_reports = []
        for requirement in profile.requirements:
            matching = [report for report in reports if report.kind == requirement.kind]
            accepted = [report for report in matching if report.outcome in requirement.allowed_outcomes]
            if not accepted:
                all_requirements_met = False
            else:
                accepted_reports.extend(accepted)

        if not all_requirements_met:
            outcome = ValidationOutcome.FAIL
        elif any(report.outcome is ValidationOutcome.PASS_WITH_LIMITATIONS for report in accepted_reports):
            outcome = ValidationOutcome.PASS_WITH_LIMITATIONS
        else:
            outcome = ValidationOutcome.PASS

        evaluation = ValidationEvaluation(
            id=uuid4(),
            profile_id=profile.profile_id,
            profile_revision=profile.revision,
            report_ids=report_ids,
            outcome=outcome,
            evaluated_at=self.clock(),
        )
        with self.uow_factory() as uow:
            uow.validation.add_evaluation(evaluation)
            uow.commit()
        return evaluation
