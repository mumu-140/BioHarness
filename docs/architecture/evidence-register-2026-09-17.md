# BioHarness Architecture Evidence Register

Updated: 2026-09-18
Status: Evidence/reference record; non-authoritative
Purpose: Record which papers, standards, mature projects, and internal systems informed BioHarness architecture, what was actually inspected, and the boundary of each inference.

External evidence can justify a pattern or constrain a design choice. It does not become BioHarness Policy or scientific truth by citation alone.

## 1. Evidence Record Contract

Each material source should record when practical:

```yaml
source:
  title: ...
  url: ...
  source_type: paper | official_spec | official_docs | repository | internal_asset
  version_or_revision: ...
  publication_or_release_date: ...
  checked_at: ...
  inspection_depth: full_text | methods | official_docs | repository_code | repo_readme | abstract
  claim_scope: ...
```

Every adoption statement should answer:

1. what capability/observation is being borrowed;
2. which BioHarness contract it informs;
3. what BioHarness deliberately does **not** infer.

Rolling documentation/repository pages should never be treated as immutable evidence without revision/check context.

## 2. Workflow, Provenance, and Recovery

### AiiDA

Source:

- Huber SP et al. *AiiDA 1.0, a scalable computational infrastructure for automated reproducible workflows and data provenance*. Scientific Data 7, 300 (2020).
- https://doi.org/10.1038/s41597-020-00638-4
- https://github.com/aiidateam/aiida-core
- checked_at: 2026-09-17
- inspection_depth: paper/official-project material used for architecture review
- claim_scope: process provenance, persistent scientific execution, recoverable workflow state

Adopt:

- provenance is a first-class scientific object;
- computation and provenance graph are distinct;
- persistent process state/recovery is a useful reference for Run/Attempt semantics.

Do not infer: BioHarness should migrate all pipelines to AiiDA or that provenance alone establishes scientific validity.

### Nextflow / nf-core

Sources:

- https://www.nextflow.io/
- https://github.com/nextflow-io/nextflow
- https://nf-co.re/
- https://github.com/nf-core
- checked_at: 2026-09-17/18
- inspection_depth: official docs/repository patterns; concrete Genome-web integration separately audited at source-code level
- claim_scope: workflow execution, cache/resume, portable executors, module/workflow reuse

Adopt: keep Nextflow external as WorkflowExecutor; bind exact workflow/config/input/environment identity; reuse engine cache/resume.

Do not infer: Nextflow cache identity equals BioHarness scientific identity, workflow completion equals validation PASS, or every integration exposes async/idempotent remote submission.

### Snakemake

Source:

- Köster J, Rahmann S. *Snakemake—a scalable bioinformatics workflow engine*. Bioinformatics 28, 2520-2522 (2012).
- https://github.com/snakemake/snakemake
- checked_at: 2026-09-17
- inspection_depth: paper/repository reference
- claim_scope: alternative mature workflow engine and reproducible composition

Adopt: normalize heterogeneous workflow engines behind BioHarness contracts.

### OpenLineage

Source:

- https://openlineage.io/
- https://github.com/OpenLineage/OpenLineage
- checked_at: 2026-09-17
- inspection_depth: official docs/repository overview
- claim_scope: Job/Run/Dataset lineage vocabulary

Adopt: reuse compatible lineage vocabulary where useful; add BioHarness scientific/validation/Decision/memory semantics above it.

### RO-Crate / Workflow Run RO-Crate

Sources:

- https://www.researchobject.org/ro-crate/
- https://www.researchobject.org/workflow-run-crate/
- checked_at: 2026-09-17
- inspection_depth: official specification/documentation
- claim_scope: portable research/workflow-run metadata packaging

Adopt: prefer standards-compatible export/archive when practical.

Do not infer: metadata packaging guarantees future availability of every external input/environment.

## 3. Data and Execution Interface Standards

### GA4GH DRS

Source:

- https://www.ga4gh.org/product/data-repository-service-drs/
- checked_at: 2026-09-17
- inspection_depth: official product/spec documentation
- claim_scope: stable logical identity separated from access location/mechanism

Adopt: use as a reference for `ResolvedDataRef`, supplemented by biological release and collection-membership identity.

### GA4GH WES / TES / TRS

Sources:

- https://www.ga4gh.org/product/workflow-execution-service-wes/
- https://www.ga4gh.org/product/task-execution-service-tes/
- https://www.ga4gh.org/product/tool-registry-service-trs/
- checked_at: 2026-09-17
- inspection_depth: official product/spec documentation
- claim_scope: workflow registry/execution/task boundary patterns

Adopt: keep provider interfaces standards-alignable where reasonable.

Do not infer: P0 must implement GA4GH compliance.

## 4. Policy and Authorization

### Open Policy Agent

Sources:

- https://www.openpolicyagent.org/docs/
- https://github.com/open-policy-agent/opa
- checked_at: 2026-09-17
- inspection_depth: official docs/repository overview
- claim_scope: explicit/testable policy decisions separated from application logic

Adopt: keep `PolicyDecision` separate from scientific feasibility and execution state; OPA may later be an adapter.

Do not infer: policy engines determine whether biological/statistical inference is identifiable.

## 5. Scientific-Validity References

### DESeq2

Source:

- Love MI, Huber W, Anders S. *Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2*. Genome Biology 15, 550 (2014).
- https://doi.org/10.1186/s13059-014-0550-8
- https://bioconductor.org/packages/DESeq2
- checked_at: 2026-09-17
- inspection_depth: primary paper + official Bioconductor guidance
- claim_scope: count semantics, design matrix, confounding/identifiability

Adopt: TaskSpec/Module contracts expose design and input assumptions; authorized execution can still be `NOT_IDENTIFIABLE` or `INCOMPATIBLE`.

### Gene Ontology enrichment guidance

Source:

- https://geneontology.org/docs/go-enrichment-analysis/
- checked_at: 2026-09-17
- inspection_depth: official guidance
- claim_scope: selected gene set, background/reference universe, mapping/annotation provenance

Adopt: background universe, annotation release, identifier mapping, and multiple testing are provenance-bearing scientific configuration.

### goseq / RNA-seq selection bias

Source:

- Young MD et al. *Gene ontology analysis for RNA-seq: accounting for selection bias*. Genome Biology 11, R14 (2010).
- https://doi.org/10.1186/gb-2010-11-2-r14
- checked_at: 2026-09-17
- inspection_depth: primary-paper evidence
- claim_scope: gene-selection bias such as transcript-length effects

Adopt: enrichment method/background decisions may depend on how the tested gene set was generated.

### Replicate-aware single-cell differential expression

Source:

- Squair JW et al. *Confronting false discoveries in single-cell differential expression*. Nature Communications 12, 5692 (2021).
- https://doi.org/10.1038/s41467-021-25960-2
- checked_at: 2026-09-17
- inspection_depth: primary paper
- claim_scope: biological-replicate/experimental-unit handling in multi-sample scRNA-seq DE

Adopt: bulk -> single-cell pathway reuse must re-evaluate experimental unit/statistical assumptions.

## 6. Memory and Retrieval Research

### RAPTOR

Source:

- Sarthi P et al. *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval*. arXiv:2401.18059 (2024).
- https://arxiv.org/abs/2401.18059
- checked_at: 2026-09-17
- inspection_depth: paper
- claim_scope: hierarchical representation/retrieval at multiple abstraction levels

Adopt: hierarchy can organize/expand retrieval; exact lookup need not traverse root-to-leaf.

### HippoRAG / HippoRAG 2

Source:

- https://github.com/OSU-NLP-Group/HippoRAG
- checked_at: 2026-09-17
- inspection_depth: repository/project material
- claim_scope: graph/associative multi-hop retrieval

Adopt: graph retrieval is a candidate strategy for distributed context.

Do not infer: hard policy or fatal contradictions should be probabilistic top-k retrieval.

### Agent Workflow Memory (AWM)

Source:

- *Agent Workflow Memory*. arXiv:2409.07429 (2024).
- https://arxiv.org/abs/2409.07429
- checked_at: 2026-09-17
- inspection_depth: paper
- claim_scope: reusable procedural routines induced from historical trajectories

Adopt: supports Memory Pathway concept.

Do not infer: generic task frequency/reward equals scientific reliability.

### TiMEM

Source:

- https://github.com/TiMEM-AI/TiMEM
- checked_at: 2026-09-17
- inspection_depth: repository/project material
- claim_scope: temporal/hierarchical long-horizon memory infrastructure

Adopt: candidate Memory Provider; BioHarness retains evidence/scope/validity/Decision semantics.

### Graphiti

Source:

- https://github.com/getzep/graphiti
- checked_at: 2026-09-17
- inspection_depth: repository/project material
- claim_scope: temporal graph relations and multi-hop retrieval

Adopt: optional graph provider if real workload justifies it; not mandatory P0 infrastructure.

## 7. Research-Agent and Literature Systems

### BioMedAgent

Source:

- https://www.nature.com/articles/s41551-026-01634-6
- checked_at: 2026-09-17
- inspection_depth: publication metadata/available article material + associated project resources; not a reproduced benchmark
- claim_scope: biomedical agent combining tool use, analysis, and memory/retrieval

Adopt: comparison point for research-agent capability; BioHarness differentiation should be tested around evidence-grounded applicability, provenance, version change, governed promotion, and safe scientific reuse.

### PaperQA2

Source:

- https://github.com/Future-House/paper-qa
- checked_at: 2026-09-17
- inspection_depth: repository/project material
- claim_scope: evidence-preserving literature retrieval/answer generation

Adopt: literature-derived memory should retain source identity/evidence location and remain distinct from experimental/provider evidence.

## 8. Concrete Research-Software Example: Schultz et al. 2026 EGT

Source:

- Schultz DT et al. *Topological mixing and irreversibility in animal chromosome evolution*. Science Advances 12, eadz5561 (2026).
- checked_at: 2026-09-17
- inspection_depth: uploaded paper methods/data-availability and architecture-relevant sections
- claim_scope: composable research software, workflow orchestration, graph use, sensitivity/alternative-explanation validation

Observed architecture:

- data/database construction: `chrombase`;
- embargo handling: `genbargo`;
- main analyses: `egt`;
- simulation: `chromsim`;
- inversion analysis: `breakpointer2`;
- orchestration: Snakemake;
- Neo4j for a specifically graph-shaped orthology/chromosome problem rather than universal storage.

Observed scientific design lessons:

- homology-detection failure is audited as an alternative explanation;
- taxonomic resampling tests sampling imbalance;
- UMAP/sentinel sensitivity is tested;
- GO enrichment uses an explicit family universe and is cross-checked with GOATOOLS.

Adopt: research software can remain a modular ecosystem under a reproducible harness; material alternative explanations/sensitivity should be validated where method-specific.

Do not infer: animal BCnS ALG biology transfers directly to plants or that BioHarness needs Neo4j in P0.

## 9. Internal Asset: Genome-web TF Nextflow Pilot

Repository: https://github.com/mumu-140/genome-web-backend
Branch inspected: `main`
Checked: 2026-09-18
Inspection depth: repository code + workflow configuration + README

Files inspected directly:

- `pipeline/nextflow/run.sh`
- `pipeline/nextflow/scripts/run.py`
- `pipeline/nextflow/scripts/validate_genomes.py`
- `pipeline/nextflow/main.nf`
- `pipeline/nextflow/nextflow.config`
- `pipeline/nextflow/README.md`

Observed properties:

- explicit species/UID/assembly/annotation registration;
- leading-zero UID preservation;
- table-based gene -> transcript -> protein resolution;
- fail-fast identity/file/tool validation;
- synchronous Python launcher;
- local Nextflow executor in the inspected config;
- per-run-root filesystem launch lock;
- explicit non-reusable attempt directories;
- deep Nextflow cache/resume;
- tool/source fingerprints and invocation evidence;
- candidate BUNDLE verification;
- no automatic production publication;
- resolved scientific inputs need additional BioHarness-owned member/manifest identity provenance.

Adopt: use this as P0 because it already exercises identity, cache/reuse, failures, candidate validation, and publication boundary. Wrap it rather than rewrite its biological rules.

Do not infer: provider-native async submission, distributed idempotency, exactly-once execution, remote scheduler support, or generic Nextflow capabilities.

## 10. Evaluation References and Directions

Candidate directions:

- BixBench — scientific/data-analysis task evaluation;
- LongMemEval — long-horizon memory/update evaluation;
- AgentDojo — tool-use/adversarial evaluation;
- benchmark-quality auditing such as BenchGuard-style contamination/validity checks.

Inspection status: design references only; BioHarness has not reproduced their headline results.

Future matched-budget comparison should include:

```text
no persistent research memory
vs flat hybrid retrieval
vs graph/hierarchical expansion
vs human-authored reviewed pathways
vs automatically proposed pathways
```

Candidate outcomes:

- correct scientific completion;
- correct blocking/refusal for unsupported design;
- stale-knowledge misuse;
- repeated-error rate;
- provenance completeness;
- ambiguous-execution recovery;
- contradiction handling;
- independent-evidence accounting;
- context/token/tool-call cost.

This benchmark design remains a hypothesis until executed.

## 11. Maintenance Rule

For every new source that materially changes architecture, record:

1. exact source/link;
2. source type;
3. version/revision/date when available;
4. `checked_at`;
5. inspection depth;
6. claim scope;
7. BioHarness clause informed;
8. what is deliberately not inferred.

Prefer primary papers, official specifications/documentation, original repositories, and directly inspected internal source over secondary summaries.
