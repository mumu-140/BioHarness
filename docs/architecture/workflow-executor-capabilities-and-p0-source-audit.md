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

Current inspected configuration:

```text
process.executor = local
executor.cpus = 4
executor.memory = 8 GB
cache = deep
```

`run.py` uses an exclusive non-blocking lock at `RUN_ROOT/.launch.lock` and requires unique non-reusable `RUN_ROOT/attempts/<attempt>` directories.

This protects one run root; it is not distributed idempotency or global exactly-once execution.

## 4. Resume and Provenance

Launcher supports bare `--resume` and explicit `--resume <session>`. Explicit prior session identity is preferable for automated lineage when available; implicit `last` is contextual to the launch workspace and is not scientific identity.

`invocation.json` records command, Nextflow/tool versions, executable fingerprints, workflow source hashes, original manifest SHA256, and collision-check state.

One BioHarness-level provenance gap remains: the provider resolves/canonicalizes scientific input paths, but BioHarness should independently register/digest the resolved manifest/member identities actually consumed rather than rely only on the original manifest or engine cache.

## 5. Provider Validation Boundary

BUNDLE/launcher candidate verification is useful provider-contract/artifact-integrity evidence.

It does not by itself prove:

- full scientific interpretation;
- publication readiness;
- canonical acceptance;
- BioHarness provenance completeness.

The authoritative contract therefore maps it into typed ValidationReports/ValidationProfiles.

## 6. Capability Conclusions

For the inspected integration, a truthful capability declaration is approximately:

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

These are observations about this concrete provider revision, not timeless claims about Nextflow.

## 7. Architectural Consequences Already Integrated

1. WorkflowExecutor capabilities are revision-scoped and declared explicitly.
2. Core does not fabricate exactly-once or async reconciliation guarantees.
3. Uncertain execution may stop at `NEEDS_OPERATOR_RECONCILIATION`.
4. Automated resume should prefer explicit prior session lineage when available.
5. BioHarness records resolved inputs actually consumed, not only the original manifest path.
6. Provider candidate PASS is typed validation evidence, not canonical scientific approval.
7. P0 validates current local execution only; Slurm/SSH/Kubernetes are later slices.

Final normative wording is in the authoritative contract and P0 files, not here.

## 8. Audit Status

```text
source_audit = COMPLETED
observations_integrated_into_authoritative_docs = DESIGNED
adapter_implementation = NOT_IMPLEMENTED
runtime_validation = NOT_RUN
```
