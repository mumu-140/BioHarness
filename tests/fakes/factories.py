from datetime import datetime, timezone
from uuid import UUID

from bioharness.domain.data import ResolvedDataRef
from bioharness.domain.task import OutputIntent, ScientificTaskSpec

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def make_task() -> ScientificTaskSpec:
    return ScientificTaskSpec(
        id=UUID("00000000-0000-0000-0000-000000000101"),
        revision=1,
        question="Analyze requested resource",
        requested_inference="generic scientific analysis",
        analysis_class="generic",
        biological_scope={"resources": ["provider://resource/A"]},
        output_intent=OutputIntent.CANDIDATE,
        created_at=NOW,
    )


def make_data_ref() -> ResolvedDataRef:
    return ResolvedDataRef(
        id=UUID("00000000-0000-0000-0000-000000000102"),
        provider="fake",
        provider_revision="r1",
        resource_type="generic",
        logical_uri="provider://resource/A",
        content_sha256="a" * 64,
        biological_identity={"name": "A"},
        resolved_at=NOW,
    )


def make_run_spec():
    from bioharness.domain.run import RunSpec

    return RunSpec(
        id=UUID("00000000-0000-0000-0000-000000000103"),
        task_spec_id=make_task().id,
        assessment_id=UUID("00000000-0000-0000-0000-000000000104"),
        configuration_id=UUID("00000000-0000-0000-0000-000000000105"),
        context_snapshot_id=UUID("00000000-0000-0000-0000-000000000106"),
        resolved_data_ref_ids=(make_data_ref().id,),
        analysis_hash="b" * 64,
        run_spec_hash="c" * 64,
        validation_profile_id="candidate",
        validation_profile_revision="1",
        expected_outputs=(),
        executable=True,
        created_at=NOW,
    )
