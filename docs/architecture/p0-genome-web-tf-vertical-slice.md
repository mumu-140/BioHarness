# BioHarness P0 Genome-web TF Vertical Slice

Date: 2026-09-18
Status: Authoritative P0 design record
Runtime status: NOT_IMPLEMENTED
Scenario status: NOT_RUN

## 1. Purpose

P0 proves one complete BioHarness control loop around a **real existing scientific workflow**. It exercises current provider constraints instead of a hypothetical generic workflow service.

BioHarness wraps and governs the Genome-web TF Nextflow pilot; it does not copy or rewrite its biological logic.

### Audited provider source

Repository: `mumu-140/genome-web-backend`
Audited branch: `main`
Audited commit: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`
Checked: 2026-09-18

Files inspected:

- `pipeline/nextflow/run.sh`
- `pipeline/nextflow/scripts/run.py`
- `pipeline/nextflow/scripts/validate_genomes.py`
- `pipeline/nextflow/main.nf`
- `pipeline/nextflow/nextflow.config`
- `pipeline/nextflow/README.md`

P0 capability claims below are tied to this inspected revision. A later provider revision must be reassessed rather than inheriting these claims automatically.

## 2. Scientific Task

Task intent:

> Build transcription-factor family protein phylogenies for explicitly requested registered genomes, preserve exact biological/data identity, produce auditable candidate artifacts, and stop before production publication.

Output intent is `candidate`, not `canonical` or `production-published`.

Ordinary workflow defaults such as `min_seqs`, IQ-TREE model, bootstrap values, seed, thread count, and runtime resources are not scientific intent unless the request explicitly fixes them.

## 3. Source-Observed Provider Behavior

Current launcher:

```text
run.sh
  -> source existing Genome-web config
  -> exec Python run.py
      -> validate args/protected paths
      -> require Nextflow 25.10.4
      -> fingerprint Python/Biopython, MAFFT, IQ-TREE, workflow sources
      -> acquire RUN_ROOT/.launch.lock
      -> create unique attempts/<attempt>
      -> validate/resolve genome manifest
      -> write invocation.json
      -> subprocess.run(nextflow ..., check=True)
      -> require output/candidate/manifest.json
```

Current Nextflow config uses:

```text
process.executor = local
executor.cpus = 4
executor.memory = 8 GB
cache = deep
```

This is a synchronous local launcher, not a server-style async submit/poll service.

Scientific workflow stages remain:

```text
registry/preflight
  -> PREPARE per genome
  -> MAFFT per eligible TF family
  -> IQTREE per family
  -> BUNDLE whole-batch candidate verification
```

Provider rules BioHarness preserves include explicit species/UID/build/release identity, table-based gene->transcript->protein resolution, leading-zero UID preservation, fail-fast identity/file/tool checks, threshold-only family skipping, and candidate/production separation.

## 4. ScientificTaskSpec Uses Requested/Logical Scope

TaskSpec captures requested biological scope **before** provider resolution. It must not pretend a resource is already resolved.

```yaml
scientific_task_spec:
  question: build TF-family protein phylogenies for requested registered genomes
  requested_inference: family-level protein phylogeny
  analysis_class: tf_phylogeny
  biological_scope:
    requested_genome_refs: [logical Genome-web resource identifiers]
    required_release_constraints: [...]
  output_intent: candidate
  unresolved_fields: []
```

If a requested genome/release is ambiguous or unavailable, the task remains unresolved.

## 5. Authorized Resolution and ResolvedDataRefs

Where provider access is protected, current authorization is evaluated before reading/resolving the resource.

Resolution then freezes exact scientific identity, including at least:

- species ID;
- five-digit UID;
- genome build;
- annotation release;
- release ID;
- gene TSV;
- transcript TSV;
- protein TSV;
- protein FASTA;
- TF TSV;
- TF-gene TSV.

Target provenance:

```text
requested logical genome refs
  -> authorized provider resolution
      -> original manifest identity
          -> resolved manifest Artifact/digest
              -> per-genome ResolvedDataRefs
                  -> member file identities/digests or immutable provider revisions
```

The inspected provider records the original manifest digest and uses Nextflow deep cache, but BioHarness must independently record the resolved manifest/member identity actually consumed.

## 6. ScientificAssessment

Assessment binds to:

- TaskSpec revision;
- ResolvedDataRefs;
- the TF workflow/Module scientific-contract revision;
- relevant assumptions/limitations.

P0 checks include required source availability, species/UID consistency, five-digit UID preservation, provider identity rules, and absence of unsupported inferred claims such as an unstated rooting interpretation.

Possible outcomes:

```text
ANALYSIS_SUPPORTED
ANALYSIS_SUPPORTED_WITH_LIMITATIONS
UNRESOLVED
INCOMPATIBLE
```

This is analysis feasibility, not evidence that a biological hypothesis is true.

## 7. ResolvedConfiguration

Configuration records the exact executable choice:

- workflow/provider source revision;
- representative-sequence provider rule;
- `min_seqs`;
- MAFFT parameters;
- IQ-TREE model/bootstrap/aLRT/seed;
- Python/Biopython identity;
- MAFFT/IQ-TREE executable fingerprints;
- Nextflow/runtime requirements;
- input bindings;
- validation-profile revision;
- ReproducibilityContract;
- planned resource controls.

If a chosen configuration changes an assumption used by ScientificAssessment, the assessment is refreshed before RunSpec becomes executable.

Result-affecting settings enter RunSpec analysis identity. Concrete host/allocation facts remain RunAttempt observations unless the ReproducibilityContract marks them result-affecting.

## 8. Current Provider Capability Snapshot

For the audited source revision, the truthful baseline is:

```yaml
workflow_executor_capabilities:
  provider: genome-web-tf-nextflow-pilot
  provider_revision: 05072cbbcd533ca59afa13996d8d0edd8f939c6e
  submission:
    mode: synchronous_process
    native_idempotency_key: false
    durable_external_execution_id: false
  observation:
    poll: false
    reconcile_after_disconnect: limited
    logs: true
    trace: true
  retry_resume:
    engine_resume: true
    explicit_resume_identity: limited
  cancellation:
    supported: false
  compute:
    backend: local
    remote_scheduler: false
  provenance:
    invocation_record: true
    source_hashes: true
    tool_fingerprints: true
    resolved_manifest_digest: false
  limitations:
    - launcher does not expose a durable async job lookup API
    - launcher does not currently persist a durable external execution/session ID for BioHarness
    - explicit Nextflow resume can be supplied when session identity is known, but the inspected launcher does not currently capture that identity as a durable BioHarness binding
    - no durable cancellation interface is exposed by the inspected provider
    - reconciliation after disconnect is limited to inspectable filesystem/process/log/session evidence
    - resolved scientific member digests require BioHarness-adapter provenance
```

An adapter may later implement stronger behavior, but it must publish a new capability snapshot with evidence rather than upgrading these claims by assumption.

## 9. RunSpec and RunAttempt Mapping

`RunSpec` identifies intended result-affecting scientific/computational work.

Examples:

```text
same resolved inputs + same result-affecting configuration + infrastructure retry
  -> same RunSpec, new RunAttempt

changed IQ-TREE model/bootstrap
  -> new RunSpec

changed proteome/member identity
  -> new RunSpec
```

Each BioHarness external launch is a new RunAttempt. The provider's `attempts/<attempt>` directory maps naturally to provider attempt evidence but is not the global identity.

Nextflow-internal retries stay within one RunAttempt. A new BioHarness-issued `--resume` launch is a new RunAttempt even if previous Nextflow work/cache is reused.

The RunAttempt records concrete runtime facts such as launcher host/process identity and observed resource allocation.

## 10. Action-Scoped Authorization

Historical ContextSnapshot/PolicyDecision is reproducibility evidence only.

P0 performs current authorization where applicable before:

- protected Genome-web reads/resolution;
- launching a workflow;
- cancellation or other execution control if later supported;
- artifact publication;
- canonical mutation;
- shared memory/pathway promotion.

P0 does not automatically permit production loader execution, production DB/path mutation, canonical promotion, historical overwrite, or relaxation of provider identity/validation rules.

## 11. Failure, Retry, and Safe Uncertainty

### Provider/tool failure

- current RunAttempt becomes failed;
- historical attempt remains immutable;
- later attempt may reuse compatible Nextflow cache if RunSpec identity is unchanged.

### Uncertain local launcher outcome

Possible reconciliation evidence includes attempt directory, `invocation.json`, Nextflow log/trace/session metadata, candidate manifest, and observable lock/process state.

If evidence cannot establish the prior outcome safely:

```text
UNKNOWN -> NEEDS_OPERATOR_RECONCILIATION
```

Blind duplicate submission is forbidden.

### Resume

The inspected provider accepts explicit Nextflow resume identity when supplied, but does not currently capture a durable session identity for BioHarness. Therefore automatic resume is **not** a P0 capability until the adapter can bind the intended prior session reliably. Implicit `last` is never treated as scientific identity.

## 12. Artifact and Reuse Model

Register immutable candidate artifacts/evidence where applicable:

- representative-protein bundles;
- alignments;
- trees;
- per-family execution metadata;
- audit tables;
- candidate manifest/final candidate tables;
- resolved manifest;
- invocation/log/trace/session evidence.

Reused cached work keeps explicit lineage to its prior content/execution evidence rather than being represented as newly recomputed.

### Parameter-local reuse

If only IQ-TREE result-affecting parameters change, create a new RunSpec; scientifically identical MAFFT output may be reused, while tree/downstream candidate validation is recomputed.

If input proteins change for one family, create a new RunSpec; only outputs with demonstrated compatible identity may be reused, and affected family plus whole-batch candidate validation must be updated.

## 13. Typed, Versioned Validation

Provider completion is not universal validation.

Illustrative mapping:

```text
provider input/preflight -> provider_contract
BUNDLE verifier          -> artifact_integrity / provider_contract
BioHarness provenance    -> provenance_completeness
future scientific review -> method_qc / scientific_assumptions
future production gate   -> publication_readiness
```

P0 candidate gate records the exact ValidationProfile ID/revision and report set used. A later stricter profile may re-evaluate/revalidate without rewriting historical gate evidence.

A technically valid candidate remains non-canonical/non-production until a later explicit governed Decision/gate.

## 14. Finding and Memory Boundary

P0 need not produce a broad biological conclusion merely because trees exist.

If a post-run scientific interpretation is recorded, it is an evidence-linked `Finding` with explicit scope/limitations. Operational lessons such as repeatable preflight failure, version incompatibility, resume limitation, or candidate corruption may become scoped MemoryCandidates linked to RunSpec/RunAttempt/Artifact/Validation evidence.

Memory can influence later context/assessment/configuration proposals. It does not automatically become Finding, Method/Lab Policy, or canonical state.

## 15. P0 Acceptance Criteria

Fresh executable evidence is required before P0 can be described as implemented/validated. P0 must demonstrate:

1. requested logical biological scope resolves to exact/checkable consumed input identities;
2. authorization occurs before protected resolution/access and before workflow launch;
3. TaskSpec remains intent while provider/method defaults live in configuration;
4. ScientificAssessment binds to exact method/data dependencies;
5. existing Genome-web workflow is invoked through an adapter, not copied into Core;
6. capability snapshot is revision-pinned and truthful;
7. RunSpec identity is separated from concrete RunAttempt/runtime facts;
8. engine-internal retry differs from a new BioHarness launch;
9. uncertain execution can remain `UNKNOWN/NEEDS_OPERATOR_RECONCILIATION` without blind resubmission;
10. typed/versioned validation prevents provider PASS from becoming universal validation;
11. parameter-local reuse is provenance-preserving;
12. candidate outputs remain non-production without a later explicit gate;
13. one scoped evidence-backed MemoryCandidate can affect later context without becoming Policy.

## 16. Out of Scope for P0

P0 does not establish correctness of RNA-seq/GO runtime contracts, automatic Memory Pathway mining, project closeout consolidation, graph-database performance, cross-project scope promotion, Web UI behavior, production publication, Slurm/SSH/Kubernetes execution, distributed locks, generic WES/TES compatibility, provider-native exactly-once submission, durable async polling, or durable provider cancellation.

## 17. Current Status

```text
architecture = DESIGNED
provider_adapter = NOT_IMPLEMENTED
runtime_tests = NOT_RUN
scientific_validation = NOT_RUN
production_publication = OUT_OF_SCOPE_P0
```