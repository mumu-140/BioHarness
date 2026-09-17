# BioHarness P0 Genome-web TF Vertical Slice

Date: 2026-09-18
Status: Authoritative P0 design record
Runtime status: NOT_IMPLEMENTED
Scenario status: NOT_RUN

## 1. Purpose

P0 proves one real BioHarness control loop around an existing scientific workflow. It must exercise actual provider constraints rather than a hypothetical generic workflow service.

Reference implementation:

- `mumu-140/genome-web-backend/pipeline/nextflow/run.sh`
- `mumu-140/genome-web-backend/pipeline/nextflow/scripts/run.py`
- `mumu-140/genome-web-backend/pipeline/nextflow/scripts/validate_genomes.py`
- `mumu-140/genome-web-backend/pipeline/nextflow/main.nf`
- `mumu-140/genome-web-backend/pipeline/nextflow/nextflow.config`
- `mumu-140/genome-web-backend/pipeline/nextflow/README.md`

BioHarness wraps and governs this workflow. It does not rewrite its biological logic.

## 2. Scientific Task

Task intent:

> Build transcription-factor family protein phylogenies for one or more explicitly registered genomes, preserve exact species/UID/assembly/annotation identity, produce auditable candidate artifacts, and stop before production publication.

Output intent:

```text
candidate
```

not:

```text
canonical / production-published
```

The scientific TaskSpec does **not** hard-code ordinary workflow defaults such as `min_seqs`, IQ-TREE model, bootstrap values, seed, or thread count unless the request explicitly makes those part of the scientific question.

## 3. Source-Observed Provider Behavior

The current Genome-web pilot is a synchronous launcher around a local Nextflow executor.

Observed launcher sequence:

```text
run.sh
  -> load existing Genome-web config
  -> exec Python run.py
      -> validate arguments and protected paths
      -> require Nextflow 25.10.4
      -> fingerprint Python/Biopython, MAFFT, IQ-TREE, source files
      -> acquire RUN_ROOT/.launch.lock
      -> create unique attempts/<attempt>
      -> validate/resolve genome manifest
      -> write invocation.json
      -> subprocess.run(nextflow ..., check=True)
      -> require output/candidate/manifest.json
```

Current `nextflow.config` uses:

```text
process.executor = local
executor.cpus = 4
executor.memory = 8 GB
cache = deep
```

Therefore P0 validates a **local synchronous WorkflowExecutor adapter**. It does not validate Slurm, SSH, Kubernetes, generic WES/TES, or distributed submission semantics.

## 4. Existing Workflow Stages

The scientific workflow remains:

```text
registry/preflight
    -> PREPARE per genome
    -> MAFFT per eligible TF family
    -> IQTREE per family
    -> BUNDLE whole-batch candidate verification
```

Existing provider rules that BioHarness must preserve include:

- no implicit species/UID/assembly/annotation/output defaults;
- gene -> transcript -> protein joins by explicit tables, not guessed suffixes;
- one representative protein per gene/family according to provider logic;
- only explicitly threshold-ineligible families may be skipped;
- identity, missing-file, and tool failures fail the batch;
- leading-zero UID identity is preserved;
- candidate outputs remain separate from production publication.

## 5. ScientificTaskSpec

Conceptual P0 TaskSpec:

```yaml
scientific_task_spec:
  question: build TF-family protein phylogenies for registered genomes
  requested_inference: family-level protein phylogeny
  analysis_class: tf_phylogeny
  biological_scope:
    genomes: [explicitly_resolved_registered_genomes]
  output_intent: candidate
  unresolved_fields: []
```

If required biological identity is unresolved, governed execution does not begin.

## 6. ScientificAssessment

P0 pre-execution assessment checks include:

- required source tables/files exist and are non-empty;
- manifest/table species and UID identity are consistent;
- protein/TF inputs belong to the registered genome;
- five-digit UID identity is preserved as a string;
- cross-UID collisions are handled by the provider contract rather than auto-renaming;
- the requested task does not imply unsupported rooting or downstream biological claims.

Possible outcomes:

```text
ANALYSIS_SUPPORTED
ANALYSIS_SUPPORTED_WITH_LIMITATIONS
UNRESOLVED
INCOMPATIBLE
```

This assessment means the analysis is supportable; it is not evidence that a biological hypothesis is true.

## 7. ResolvedConfiguration

P0 configuration freezes result-affecting executable choices, including:

- exact workflow/provider revision;
- representative-sequence provider rule;
- `min_seqs`;
- MAFFT parameters;
- IQ-TREE model/bootstrap/aLRT/seed parameters;
- thread/resource settings;
- Python/Biopython identity;
- MAFFT and IQ-TREE executable/version fingerprints;
- Nextflow/runtime identity;
- input bindings;
- validation profile;
- reproducibility expectations.

Current provider defaults are configuration, not scientific intent.

## 8. Resolved Input Provenance

Genome-web remains authoritative for source biological registration.

P0 records both the original request/manifest identity and the actual resolved inputs consumed by Nextflow.

Target provenance chain:

```text
registered biological resource
    -> original manifest identity
        -> resolved manifest Artifact/digest
            -> per-genome ResolvedDataRef
                -> six resolved scientific input files
```

Per genome, these include at least:

- gene TSV;
- transcript TSV;
- protein TSV;
- protein FASTA;
- TF TSV;
- TF-gene TSV;
- species ID;
- five-digit UID;
- genome build;
- annotation release;
- release ID.

The current provider records a digest of the original manifest and uses Nextflow deep caching, but BioHarness provenance must independently register/check the resolved manifest/member identity actually consumed.

## 9. WorkflowExecutor Capability Snapshot

P0 adapter declares capabilities for the concrete provider revision.

Expected current shape:

```yaml
workflow_executor_capabilities:
  provider: genome-web-tf-nextflow-pilot
  provider_revision: exact-source-revision
  submission:
    mode: synchronous_process
    native_idempotency_key: false
    durable_external_execution_id: limited
  observation:
    poll: limited
    reconcile_after_disconnect: limited
    logs: true
    trace: true
  retry_resume:
    engine_resume: true
    explicit_resume_identity: supported_if_session_captured
  cancellation:
    supported: provider_specific
  compute:
    backend: local
    remote_scheduler: false
  provenance:
    invocation_record: true
    source_hashes: true
    tool_fingerprints: true
    resolved_manifest_digest: adapter_required
```

The adapter must not claim generic Nextflow capabilities that this integration does not expose.

## 10. RunSpec and RunAttempt

One immutable `RunSpec` identifies intended scientific/computational work.

Examples:

```text
same inputs + same result-affecting configuration + new execution retry
    -> same RunSpec, new RunAttempt

same alignments + changed IQ-TREE model/bootstrap
    -> new RunSpec

changed proteome/member identity
    -> new RunSpec
```

Each BioHarness external launch/binding is a new `RunAttempt`.

The provider's `attempts/<attempt>` directory maps naturally to attempt identity, but filesystem naming alone is not the global BioHarness identity.

Nextflow process retries within one bound launch remain internal execution provenance, not new BioHarness RunAttempts.

A new `--resume` launch issued by BioHarness is a new RunAttempt even if it reuses prior Nextflow work/cache.

## 11. Current Authorization Before Side Effects

Historical ContextSnapshot/PolicyDecision is stored for reproducibility.

Before P0 launches a workflow or performs any later publication/canonical mutation, BioHarness checks current actor/policy authorization again.

P0 allows, subject to current policy:

- reading registered Genome-web source data;
- creating TaskSpec/assessment/configuration/RunSpec;
- launching the candidate workflow;
- registering candidate Artifacts;
- recording typed ValidationReports and MemoryCandidates.

P0 does not automatically allow:

- production loader execution;
- production DB/path mutation;
- canonical pointer update;
- historical artifact overwrite;
- relaxation of provider identity/validation rules.

## 12. Failure, Retry, and Uncertain Execution

### Provider failure after partial work

Expected:

- current RunAttempt becomes failed;
- historical attempt remains immutable;
- compatible Nextflow cache may be reused by a later RunAttempt when RunSpec identity is unchanged.

### Lost/uncertain launcher outcome

Because the current provider is synchronous/local and lacks a generic durable submit/poll API, BioHarness must not fabricate exactly-once semantics.

Possible evidence for reconciliation includes:

- attempt directory;
- `invocation.json`;
- Nextflow log/trace/session metadata;
- candidate manifest;
- launcher/run-root lock/process state when observable.

If available evidence cannot establish the prior execution outcome safely:

```text
UNKNOWN -> NEEDS_OPERATOR_RECONCILIATION
```

Blind duplicate submission is forbidden.

### Resume identity

Automated resume should bind to an explicit prior Nextflow session/run identity when available.

Implicit `-resume` / `last` is not scientific identity and should not be treated as such.

## 13. Artifact Model

Candidate outputs are registered as immutable Artifacts or artifact collections, including where applicable:

- representative-protein bundles;
- alignments;
- tree outputs;
- per-family execution metadata;
- audit tables;
- candidate manifest;
- final candidate TF-tree tables;
- resolved manifest;
- Nextflow invocation/log/trace/session evidence.

Reused cached work retains lineage to the prior content/execution evidence instead of being presented as newly recomputed work.

## 14. Typed Validation

Execution completion and provider `PASS candidate=...` do not mean universal scientific validation.

Illustrative mapping:

```text
provider input/preflight checks
    -> ValidationReport(kind=provider_contract)

BUNDLE candidate verifier
    -> ValidationReport(kind=artifact_integrity/provider_contract)

BioHarness input/provenance audit
    -> ValidationReport(kind=provenance_completeness)

future scientific review
    -> separate method_qc/scientific_assumptions reports

future production release
    -> separate publication_readiness profile
```

P0 candidate ValidationProfile should at minimum require the provider/candidate integrity and provenance dimensions explicitly defined by implementation.

A technically valid candidate remains non-canonical and non-published until a later governed Decision/gate.

## 15. Parameter-Local Reuse

### IQ-TREE-only result-affecting change

Expected:

- new RunSpec;
- scientifically identical MAFFT outputs may be reused through provider content caching;
- IQ-TREE and downstream candidate validation are recomputed/revalidated;
- old tree is never relabelled as generated under the new parameters.

### Protein/member change affecting one family

Expected:

- new RunSpec;
- provider cache may reuse outputs whose content identity proves equivalence;
- affected family alignment/tree and whole-batch candidate validation are recomputed/revalidated;
- reused provenance remains explicit.

## 16. Memory Feedback

P0 exercises only a minimal governed memory loop.

Eligible MemoryCandidate examples:

- repeatable identity/preflight failure pattern;
- tool/version incompatibility;
- explicit resume limitation/success condition;
- reproducible candidate corruption pattern.

Memory links back to RunSpec, RunAttempt, Artifact/log evidence, ValidationReport, and provider/software revision.

Memory can influence a later Context/assessment/configuration proposal. It does not automatically become Method/Lab Policy.

## 17. P0 Acceptance Criteria

Fresh executable evidence is required before P0 can be described as implemented/validated.

Acceptance requires demonstrating:

1. exact registered data and resolved member identity are frozen/checkable;
2. TaskSpec remains scientific intent while method parameters live in ResolvedConfiguration;
3. pre-execution ScientificAssessment uses analysis-feasibility semantics;
4. the existing Genome-web workflow is invoked through an adapter rather than copied into BioHarness Core;
5. the adapter publishes a truthful revision-scoped capability snapshot;
6. RunSpec and RunAttempt identity remain distinct;
7. current authorization is evaluated before each new side effect;
8. provider/engine internal retries are distinguishable from new BioHarness RunAttempts;
9. uncertain execution can remain `UNKNOWN/NEEDS_OPERATOR_RECONCILIATION` without blind resubmission;
10. typed validation prevents provider PASS from becoming universal validation;
11. parameter-local reuse is visible and provenance-preserving;
12. candidate artifacts remain non-production without a later explicit gate;
13. one validated failure/compatibility lesson can become a scoped MemoryCandidate and affect later context without becoming Policy.

## 18. Out of Scope for P0

P0 does not establish correctness of:

- RNA-seq/GO scientific contracts beyond scenario design;
- automatic Memory Pathway mining;
- project closeout consolidation;
- graph-database performance;
- cross-project scope promotion;
- Web UI behavior;
- production publication;
- Slurm/SSH/Kubernetes execution;
- distributed locks;
- generic WES/TES compatibility;
- provider-native exactly-once submission guarantees.

## 19. Current Status

```text
architecture = DESIGNED
provider_adapter = NOT_IMPLEMENTED
runtime_tests = NOT_RUN
scientific_validation = NOT_RUN
production_publication = OUT_OF_SCOPE_P0
```
