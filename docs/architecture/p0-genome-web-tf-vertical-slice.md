# BioHarness P0 Genome-web TF Vertical Slice

Date: 2026-09-17
Status: Design record v1 for review
Runtime status: NOT_IMPLEMENTED
Scenario status: NOT_RUN

## 1. Purpose

P0 should prove one complete BioHarness control loop using a real existing scientific workflow rather than synthetic infrastructure.

The selected reference implementation is the existing Genome-web TF Nextflow pilot in:

- `mumu-140/genome-web-backend/pipeline/nextflow/README.md`
- `mumu-140/genome-web-backend/pipeline/nextflow/main.nf`

BioHarness will **wrap and govern** this workflow. It will not rewrite its biological logic.

## 2. Scientific Task

P0 task:

> Build transcription-factor family phylogenies for one or more explicitly registered genomes, preserve exact species/UID/assembly/annotation identity, produce independently validated candidate artifacts, and stop before production publication.

The P0 output intent is therefore:

```text
candidate
```

not:

```text
canonical / production-published
```

## 3. Existing Workflow Stages

The current Genome-web TF pilot already implements:

```text
registry/preflight
    -> PREPARE per genome
    -> MAFFT per eligible TF family
    -> IQTREE per family
    -> BUNDLE whole-batch candidate verification
```

Existing biological rules include:

- no implicit species, UID, assembly, annotation, or output defaults;
- `gene -> transcript -> protein` resolution by explicit tables rather than guessed ID suffixes;
- one representative protein per gene/family using explicit selection rules;
- only families below the explicit sequence threshold may be skipped;
- missing files, identity errors, and tool failures fail the batch;
- candidate outputs remain separate from production publication.

BioHarness P0 must preserve these rules as provider behavior.

## 4. BioHarness Mapping

### 4.1 Data Provider

Genome-web remains authoritative for biological registration and source-data identity.

Each registered genome resolves to `ResolvedDataRef` objects for at least:

- gene table;
- transcript table;
- protein table;
- protein FASTA;
- TF table;
- TF-gene table;
- assembly identity;
- annotation release identity.

### 4.2 ScientificTaskSpec

Conceptual P0 task spec:

```yaml
scientific_task_spec:
  question: build TF-family phylogenies for registered genomes
  requested_inference: family-level protein phylogeny
  analysis_class: tf_phylogeny
  biological_scope:
    genomes: [explicitly_resolved_refs]
  representative_sequence_rule: provider_defined
  min_family_sequences: 4
  output_intent: candidate
  unresolved_fields: []
```

If any required biological identity field is unresolved, the task must not enter governed execution.

### 4.3 ScientificAssessment

P0 assessment checks include:

- required source tables exist and are non-empty;
- IDs are internally consistent according to the provider contract;
- protein FASTA and protein table satisfy the existing Genome-web identity contract;
- TF input belongs to the registered genome rather than a mixed genome table;
- exact UID identity is preserved as a string;
- requested analysis does not imply automatic tree rooting or unsupported biological inference.

Possible outcomes:

```text
SUPPORTED
INCOMPATIBLE
UNRESOLVED
```

### 4.4 PolicyDecision

P0 policy allows:

- reading registered Genome-web source data;
- creating an isolated RunSpec;
- submitting the existing Nextflow candidate workflow;
- registering candidate Artifacts and ValidationReports.

P0 policy does **not** automatically allow:

- production database publication;
- canonical pointer update;
- overwriting historical artifacts;
- silent relaxation of identity or validation rules.

### 4.5 ResolvedConfiguration

The configuration freezes:

- exact workflow revision;
- Nextflow/runtime revision where recorded;
- Python/Biopython identity;
- MAFFT executable/version/fingerprint;
- IQ-TREE executable/version/fingerprint;
- `min_seqs`;
- MAFFT parameters;
- IQ-TREE model/bootstrap/aLRT/seed/thread parameters;
- explicit input references;
- output/candidate location owned by the attempt.

## 5. RunSpec and RunAttempt

A P0 `RunSpec` identifies one intended scientific computation.

A parameter or input change that affects results creates a new RunSpec.

Examples:

```text
same inputs + same scientific parameters + infrastructure retry
    -> same RunSpec, new RunAttempt

same alignments + changed IQ-TREE model/bootstrap
    -> new RunSpec

changed proteome content
    -> new RunSpec
```

A `RunAttempt` binds one RunSpec to one concrete Nextflow launch.

The existing Genome-web `attempt01`, `attempt02 --resume` concept maps naturally to BioHarness RunAttempts, but BioHarness must not assume filesystem attempt naming alone is a globally stable identity.

## 6. Artifact Model

Candidate outputs are registered as immutable Artifacts or artifact collections.

Examples:

- representative-protein input bundles;
- alignments;
- tree outputs;
- per-family execution metadata;
- audit tables;
- candidate manifest;
- final candidate TF-tree tables;
- Nextflow trace/log evidence.

The existing candidate bundle's `NOT_AUTHORIZED` publication marker remains meaningful evidence of publication boundary.

## 7. ValidationReport

The P0 validation step is separate from workflow completion.

A successful Nextflow process graph can still yield a failed candidate validation.

Validation should record at least:

- input identity consistency;
- expected output membership;
- per-family available/skipped status;
- actual tool provenance for available families;
- candidate manifest integrity;
- corruption/missing-output checks;
- whole-batch validation outcome.

Possible outcomes:

```text
PASS
PASS_WITH_LIMITATIONS
FAIL
INCONCLUSIVE
```

Only an explicit `PASS`/accepted candidate may become eligible for a later Decision.

## 8. Publication Boundary

P0 stops at:

```text
validated candidate artifact
```

It does not perform:

- loader execution against production biological tables;
- production path switching;
- API publication;
- canonical release pointer update.

A later publication workflow would require its own PolicyDecision, ValidationReport requirements, and Decision.

## 9. Required Failure and Recovery Cases

### 9.1 Leading-zero UID

Input:

```text
00902
```

Expected:

- preserve exact string identity;
- never coerce to `902`;
- all downstream provider/artifact references retain `00902`.

Forbidden behavior:

- numeric normalization that changes biological/provider identity.

### 9.2 Cross-UID identity conflict

Expected:

- ScientificAssessment = `INCOMPATIBLE` or provider preflight failure;
- no governed submission;
- record a failure lesson candidate only when the evidence is clear and scoped.

Forbidden behavior:

- auto-renaming scientific IDs to force execution.

### 9.3 All families skipped by explicit threshold

Expected:

- workflow may still produce a complete, auditable candidate package describing all-skipped status if the provider contract permits it;
- BioHarness must not mislabel this as an execution disappearance/failure simply because no MAFFT/IQTREE tasks ran.

Scientific interpretation remains distinct from execution validity.

### 9.4 Tool failure after partial progress

Expected:

- current attempt becomes `FAILED`;
- no production publish;
- retained work/cache may be reused in a new attempt if provider semantics support resume and RunSpec identity is unchanged.

### 9.5 Corrupted candidate bundle

Expected:

- external execution may be `FINISHED`;
- ValidationReport = `FAIL`;
- Artifact is retained for audit if policy allows;
- candidate cannot be promoted.

### 9.6 Lost external submission acknowledgement

Expected:

```text
SUBMITTING -> UNKNOWN
```

BioHarness must reconcile provider state before any resubmission.

Forbidden behavior:

- creating duplicate expensive jobs solely because the acknowledgement was lost.

### 9.7 IQ-TREE-only parameter change

Expected:

- new RunSpec because result-affecting parameters changed;
- prior compatible alignments may be reusable through provider caching/content identity;
- phylogeny and downstream candidate bundle are recomputed/revalidated.

Forbidden behavior:

- reusing an old tree under the new parameter identity.

### 9.8 Protein-set change affecting one family

Expected:

- new RunSpec;
- provider-level content caching may reuse scientifically identical family outputs where its cache key proves equivalence;
- affected family alignment/tree and whole candidate bundle are recomputed/revalidated.

BioHarness records the reused provenance rather than pretending the entire Run was newly computed from scratch.

## 10. Memory Feedback

P0 should exercise a minimal evidence-backed memory loop.

Candidate memory examples:

- a particular identity conflict pattern repeatedly causes provider preflight failure;
- a specific tool/version combination is incompatible with the workflow contract;
- a resume strategy succeeds/fails under an explicitly recorded condition;
- a candidate validation failure identifies a reproducible corruption pattern.

Memory must link to:

- RunSpec;
- RunAttempt(s);
- relevant Artifact/log;
- ValidationReport;
- provider/software versions.

P0 does not automatically promote these into Method or Lab policy.

## 11. What P0 Does Not Test Yet

P0 does not establish correctness of:

- RNA-seq differential-expression contracts;
- GO enrichment contracts;
- automatic Memory Pathway mining;
- project closeout consolidation;
- dedicated graph-database performance;
- cross-project method-scope promotion;
- Web UI behavior;
- production publication pipeline.

These remain separate later slices.

## 12. P0 Acceptance Criteria

P0 implementation is acceptable only when fresh executable evidence shows all of the following:

1. exact registered data identity is frozen into a RunSpec;
2. an existing Genome-web Nextflow workflow is invoked through a provider adapter rather than copied into core;
3. RunSpec and RunAttempt identities are distinct;
4. lost acknowledgement can enter reconciliation without blind duplicate submission;
5. an external `FINISHED` execution can still fail ValidationReport;
6. candidate artifacts remain non-production until an explicit later gate;
7. parameter-local invalidation/reuse behavior is observable and provenance-preserving;
8. at least one validated failure/compatibility lesson can become a scoped MemoryCandidate;
9. that MemoryCandidate can affect a later Context without silently becoming Policy.

## 13. Current Status

```text
architecture = DESIGNED
provider_adapter = NOT_IMPLEMENTED
runtime_tests = NOT_RUN
scientific_validation = NOT_RUN
production_publication = OUT_OF_SCOPE_P0
```
