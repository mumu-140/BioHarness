# BioHarness P0 Workflow-Executor Source Audit — 2026-09-18

Date: 2026-09-18
Updated: 2026-09-19
Status: Source audit / non-authoritative rationale
Core status: provider-agnostic executor/reconciliation boundary IMPLEMENTED + TESTED
Reference adapter status: IMPLEMENTED + TESTED
Live validation status: TARGETED VALIDATION PASS — `TF-01`, `TF-02`, `EXEC-01`, `EXEC-06`, `DATA-01`

> This file records source observations that motivated the P0 boundary. Final semantics live in `scientific-contracts-and-run-semantics.md` and `p0-genome-web-tf-vertical-slice.md`. This audit never participates in precedence resolution. Fresh runtime evidence is recorded separately in [`2026-09-19 Genome-web TF P0 reference acceptance`](../validation/records/2026-09-19-genome-web-tf-p0.md).

## Inspected Source

Repository: `mumu-140/genome-web-backend`
Branch observed: `main`
Pinned commit inspected: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`
Checked: 2026-09-18
Inspection depth: repository code + workflow configuration + README

Files:

- `pipeline/nextflow/run.sh`
- `pipeline/nextflow/scripts/run.py`
- `pipeline/nextflow/scripts/validate_genomes.py`
- `pipeline/nextflow/main.nf`
- `pipeline/nextflow/nextflow.config`
- `pipeline/nextflow/README.md`
- `pipeline/nextflow/scripts/assemble_tf_bundle.py`
- `pipeline/scripts/build_tf_trees.py`
- `pipeline/scripts/build_tf_tree_summary.py`
- `pipeline/scripts/verify_tf_tree_summary.py`
- `pipeline/nextflow/tests/integration.py`
- `pipeline/nextflow/tests/run.sh`

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

Therefore the inspected integration is a synchronous local launcher, not a generic async submit/poll service.

## Identity, Resume, Cancellation, and Provenance

Observed:

- run-root `fcntl` lock provides local launch serialization, not distributed exactly-once execution;
- attempt directories are explicit/non-reusable and map naturally to provider attempt evidence;
- launcher accepts explicit Nextflow resume identity when supplied;
- launcher does **not** currently persist a durable external execution/session ID for BioHarness;
- no durable provider cancellation interface is exposed by the inspected source;
- no async polling API is exposed;
- reconciliation after disconnect is therefore limited to observable filesystem/process/log/session evidence;
- invocation evidence includes command, versions, tool/source fingerprints, original manifest SHA256, and collision-check state;
- resolved scientific member/manifest identity still needs BioHarness-adapter provenance.

## Validation Boundary

BUNDLE/launcher verification is provider-contract/artifact-integrity evidence. It does not itself prove scientific interpretation, publication readiness, canonical acceptance, or BioHarness provenance completeness.

## Source-Observed Capability Baseline

```text
submission.mode               = synchronous_process
compute.backend               = local
native_idempotency_key        = false
durable_external_execution_id = false
poll                          = false
reconcile_after_disconnect    = limited
logs                          = true
trace                         = true
engine_resume                 = true
explicit_resume_identity      = limited: accepted as input but not durably captured by launcher
cancellation                  = false: no durable provider interface observed
source_hashes                 = true
tool_fingerprints             = true
resolved_manifest_digest      = false: BioHarness adapter responsibility
```

These claims apply to the pinned source revision only, not to Nextflow generally or to future adapters.

## Consequences Integrated into Authoritative Docs

1. WorkflowExecutor capabilities are revision-scoped and evidence-backed.
2. Core does not fabricate exactly-once, async polling, durable cancellation, or reconciliation guarantees.
3. Uncertain execution may stop at `NEEDS_OPERATOR_RECONCILIATION`.
4. Automated resume remains disabled until the intended prior session can be bound reliably.
5. BioHarness records resolved inputs actually consumed.
6. Provider candidate PASS is typed validation evidence, not canonical approval.
7. P0 validates local execution only; remote schedulers are later slices.

## Status

```text
source_audit = COMPLETED
observations_integrated_into_authoritative_docs = DESIGNED
provider_agnostic_core_boundary = IMPLEMENTED + TESTED
genome_web_adapter_implementation = IMPLEMENTED + TESTED
genome_web_runtime_validation = VALIDATED (targeted reference scenarios only)
```