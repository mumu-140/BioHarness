# BioHarness P0 Workflow-Executor Source Audit — 2026-09-18

Date: 2026-09-18
Status: Source audit / non-authoritative rationale
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN

> This file records what was observed in the current Genome-web TF Nextflow pilot and why P0 was narrowed. Final execution semantics live in `scientific-contracts-and-run-semantics.md` and `p0-genome-web-tf-vertical-slice.md`. This audit never participates in precedence resolution.

## Inspected Source

Repository: `mumu-140/genome-web-backend`
Branch: `main`
Checked: 2026-09-18
Inspection depth: repository code + workflow configuration + README

Files:

- `pipeline/nextflow/run.sh`
- `pipeline/nextflow/scripts/run.py`
- `pipeline/nextflow/scripts/validate_genomes.py`
- `pipeline/nextflow/main.nf`
- `pipeline/nextflow/nextflow.config`
- `pipeline/nextflow/README.md`

## Observed Provider Shape

```text
run.sh
  -> source config
  -> Python run.py
      -> validate arguments/paths
      -> require Nextflow 25.10.4
      -> fingerprint tools/sources
      -> acquire RUN_ROOT/.launch.lock
      -> create attempts/<attempt>
      -> resolve/validate manifest
      -> write invocation.json
      -> subprocess.run(nextflow ..., check=True)
      -> require candidate/manifest.json
```

Inspected configuration:

```text
process.executor = local
executor.cpus = 4
executor.memory = 8 GB
cache = deep
```

Therefore the current integration is a synchronous local launcher, not a generic async submit/poll service.

## Identity, Resume, and Provenance

- the run-root filesystem lock is local protection, not distributed exactly-once execution;
- explicit non-reusable attempt directories map naturally to RunAttempt history;
- explicit resume session lineage is preferable to implicit `last` when available;
- invocation evidence includes command, versions, tool/source fingerprints, original manifest SHA256, and collision-check state;
- BioHarness still needs its own resolved manifest/member identity for the scientific inputs actually consumed.

## Validation Boundary

BUNDLE/launcher verification is useful provider-contract/artifact-integrity evidence. It does not itself prove scientific interpretation, publication readiness, canonical acceptance, or BioHarness provenance completeness.

## Capability Conclusion

```text
submission.mode               = synchronous_process
compute.backend               = local
native_idempotency_key        = false
remote_scheduler              = false
durable_external_execution_id = limited
poll                          = limited
reconcile_after_disconnect    = limited
logs                          = true
trace                         = true
engine_resume                 = true
explicit_resume_identity      = conditional on captured session
source_hashes                 = true
tool_fingerprints             = true
resolved_manifest_digest      = adapter responsibility / not provider-emitted today
```

These observations apply to this concrete integration/revision, not to Nextflow in general.

## Consequences Integrated into Authoritative Docs

1. WorkflowExecutor capabilities are revision-scoped and explicit.
2. Core does not fabricate exactly-once or async-reconciliation guarantees.
3. Uncertain execution may stop at `NEEDS_OPERATOR_RECONCILIATION`.
4. Automated resume prefers explicit prior session lineage when available.
5. BioHarness records resolved inputs actually consumed.
6. Provider candidate PASS is typed validation evidence, not canonical approval.
7. P0 validates local execution only; remote schedulers are later slices.

## Status

```text
source_audit = COMPLETED
observations_integrated_into_authoritative_docs = DESIGNED
adapter_implementation = NOT_IMPLEMENTED
runtime_validation = NOT_RUN
```
