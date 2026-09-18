"""create P0 kernel tables

Revision ID: 0001_p0_kernel
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_p0_kernel"
down_revision = None
branch_labels = None
depends_on = None

JSONB = postgresql.JSONB
UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table("projects", sa.Column("id", UUID, primary_key=True), sa.Column("name", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("scientific_task_specs", sa.Column("id", UUID, primary_key=True), sa.Column("revision", sa.Integer(), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("policy_decisions", sa.Column("id", UUID, primary_key=True), sa.Column("action", sa.String(128), nullable=False), sa.Column("outcome", sa.String(64), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("resolved_data_refs", sa.Column("id", UUID, primary_key=True), sa.Column("provider", sa.String(128), nullable=False), sa.Column("provider_revision", sa.Text(), nullable=False), sa.Column("logical_uri", sa.Text(), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("scientific_assessments", sa.Column("id", UUID, primary_key=True), sa.Column("task_spec_id", UUID, nullable=False), sa.Column("status", sa.String(96), nullable=False), sa.Column("dependency_fingerprint", sa.String(64), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("assessed_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("resolved_configurations", sa.Column("id", UUID, primary_key=True), sa.Column("task_spec_id", UUID, nullable=False), sa.Column("assessment_id", UUID, nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("context_snapshots", sa.Column("id", UUID, primary_key=True), sa.Column("payload", JSONB, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("run_specs", sa.Column("id", UUID, primary_key=True), sa.Column("task_spec_id", UUID, nullable=False), sa.Column("analysis_hash", sa.String(64), nullable=False), sa.Column("run_spec_hash", sa.String(64), nullable=False, unique=True), sa.Column("executable", sa.Boolean(), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_run_specs_analysis_hash", "run_specs", ["analysis_hash"], unique=False)
    op.create_table("run_attempts", sa.Column("id", UUID, primary_key=True), sa.Column("run_spec_id", UUID, sa.ForeignKey("run_specs.id"), nullable=False), sa.Column("attempt_number", sa.Integer(), nullable=False), sa.Column("executor_namespace", sa.String(128), nullable=False), sa.Column("submission_key", sa.Text(), nullable=False, unique=True), sa.Column("provider_attempt_name", sa.Text(), nullable=False), sa.Column("state", sa.String(96), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False), sa.Column("last_reconciled_at", sa.DateTime(timezone=True), nullable=True), sa.UniqueConstraint("run_spec_id", "attempt_number", name="uq_run_attempt_spec_number"), sa.UniqueConstraint("executor_namespace", "provider_attempt_name", name="uq_run_attempt_provider_name"))
    op.create_table("run_events", sa.Column("id", UUID, primary_key=True), sa.Column("run_attempt_id", UUID, sa.ForeignKey("run_attempts.id"), nullable=False), sa.Column("sequence_no", sa.Integer(), nullable=False), sa.Column("event_type", sa.String(128), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("run_attempt_id", "sequence_no", name="uq_run_event_sequence"))
    op.create_table("artifacts", sa.Column("id", UUID, primary_key=True), sa.Column("run_spec_id", UUID, nullable=False), sa.Column("run_attempt_id", UUID, nullable=False), sa.Column("role", sa.String(128), nullable=False), sa.Column("content_sha256", sa.String(64), nullable=False), sa.Column("size_bytes", sa.BigInteger(), nullable=False), sa.Column("uri", sa.Text(), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("validation_profiles", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("profile_id", sa.String(128), nullable=False), sa.Column("revision", sa.String(128), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.UniqueConstraint("profile_id", "revision", name="uq_validation_profile_revision"))
    op.create_table("validation_reports", sa.Column("id", UUID, primary_key=True), sa.Column("kind", sa.String(128), nullable=False), sa.Column("subject_type", sa.String(128), nullable=False), sa.Column("subject_id", sa.Text(), nullable=False), sa.Column("outcome", sa.String(64), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("validation_evaluations", sa.Column("id", UUID, primary_key=True), sa.Column("profile_id", sa.String(128), nullable=False), sa.Column("profile_revision", sa.String(128), nullable=False), sa.Column("outcome", sa.String(64), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("memory_candidates", sa.Column("id", UUID, primary_key=True), sa.Column("scope", sa.String(256), nullable=False), sa.Column("kind", sa.String(128), nullable=False), sa.Column("statement", sa.Text(), nullable=False), sa.Column("payload", JSONB, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))


def downgrade() -> None:
    for name in ["memory_candidates", "validation_evaluations", "validation_reports", "validation_profiles", "artifacts", "run_events", "run_attempts", "run_specs", "context_snapshots", "resolved_configurations", "scientific_assessments", "resolved_data_refs", "policy_decisions", "scientific_task_specs", "projects"]:
        op.drop_table(name)
