# BioHarness P0 Workflow-Executor Source Audit — 2026-09-18

Date: 2026-09-18
Status: Source audit / non-authoritative rationale
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN

> This file records what was observed in the current Genome-web TF Nextflow pilot and why the P0 contract was narrowed. Final execution semantics are integrated into `scientific-contracts-and-run-semantics.md` and `p0-genome-web-tf-vertical-slice.md`. This audit does not override those files.

## 1. Sources Inspected

Repository: `mumu-140/genome-web-backend`
Branch inspected: `main`
Checked: 2026-09-18
Inspection depth: repository code + workflow configuration + README

Files inspected:

- `pipeline/nextflow/run.sh`
- `pipeline/nextflow/scripts/run.py`
- `pipeline/nextflow/scripts/validate_genomes.py`
- `pipeline/nextflow/main.nf`
- `pipeline/nextflow/nextflow.config`
- `pipeline/nextflow/README.md`

The audit goal was to compare the planned generic WorkflowExecutor abstraction with the provider that actually exists today.

## 2. Observed Launcher Shape

Current flow:

```text
run.sh
  -> source existing Genome-web config
  -> exec Python run.py
      -> validate args and paths
      -> require Nextflow 25.10.4
      -> fingerprint Python/Biopython, MAFFT, IQ-TREE, workflow sources
      -> acquire RUN_ROOT/.launch.lock
      -> create attempts/<attempt>
      -> resolve/validate genomes manifest
      -> write invocation.json
      -> subprocess.run(nextflow ..., check=True)
      -> require output/candidate/manifest.json
```

This is a synchronous process launcher, not a generic server-style submit/poll API.

## 3. Observed Compute and Concurrency Behavior

Current `nextflow.config` fixes:

```text
process.executor = local
executor.cpus = 4
executor.memory = 8 GB
cache = deep
```

`run.py` takes a non-blocking exclusive filesystem lock on:

```text
RUN_ROOT/.launch.lock
```

The lock serializes launches within one run root. It does not establish distributed idempotency or global exactly-once execution.

Attempt directories are explicit and non-reusable:

```text
RUN_ROOT/attempts/<attempt>
```

This maps naturally to BioHarness RunAttempt identity but is not itself a globally stable BioHarness identifier.

## 4. Observed Resume Behavior

Launcher supports:

```text
--resume
--resume <session>
```

Bare `--resume` maps to Nextflow `-resume` using the current workspace's most recent session. An explicit session is therefore preferable for automated lineage when it can be captured reliably.

Engine cache/reuse is valuable execution behavior but must not be treated as BioHarness scientific identity by itself.

## 5. Observed Provenance

`invocation.json` records among other fields:

- command;
- Nextflow version;
- MAFFT/IQ-TREE versions and executable fingerprints;
- Python/Biopython identity and Python executable fingerprint;
- SHA256 for relevant workflow/source files;
- SHA256 of the original genomes manifest;
- database-collision-check state.

This is strong provider provenance for a pilot.

One gap remains for BioHarness-level identity: the launcher resolves/canonicalizes the manifest and scientific input paths but does not currently persist a BioHarness-owned digest of the resolved manifest plus all consumed member identities in the invocation record.

The adapter can add that provenance without rewriting provider scientific logic.

## 6. Observed Validation Boundary

The workflow ends with BUNDLE assembly/verification, and the launcher requires `output/candidate/manifest.json` after successful Nextflow exit.

This provides useful provider-contract/artifact-integrity evidence.

It does **not** by itself prove:

- full scientific interpretation;
- publication readiness;
- canonical acceptance;
- BioHarness provenance completeness.

The authoritative contract therefore maps it into typed ValidationReports.

## 7. Capability Conclusions

For the inspected provider revision, a truthful capability snapshot should resemble:

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

These are claims about this concrete integration, not timeless claims about Nextflow.

## 8. Architectural Consequences Already Integrated

The source audit led to these final decisions:

1. WorkflowExecutor capabilities are revision-scoped and declared explicitly.
2. Core does not fabricate exactly-once or async reconciliation guarantees.
3. Uncertain execution may stop at `NEEDS_OPERATOR_RECONCILIATION`.
4. Automated resume should prefer explicit prior session lineage when available.
5. BioHarness records the resolved inputs actually consumed, not only the original manifest path.
6. Provider BUNDLE/launcher PASS is typed validation evidence, not canonical scientific approval.
7. P0 validates current local execution only; Slurm/SSH/Kubernetes are later slices.

Final normative wording is in the authoritative contract and P0 files, not here.

## 9. Audit Status

```text
source_audit = COMPLETED
observations_integrated_into_authoritative_docs = DESIGNED
adapter_implementation = NOT_IMPLEMENTED
runtime_validation = NOT_RUN
```
