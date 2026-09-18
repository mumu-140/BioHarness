# BioHarness Architecture Evidence Register

Updated: 2026-09-18
Status: Evidence/reference record; non-authoritative
Purpose: Record which papers, standards, mature projects, and internal systems informed BioHarness architecture, what was inspected, and what is **not** inferred from each source.

External evidence may justify a pattern or constrain a design decision. Citation alone does not create BioHarness Policy, scientific truth, or an implementation dependency.

## 1. Evidence Record Contract

For material architecture evidence, record when practical:

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

1. what pattern/observation is borrowed;
2. which BioHarness contract it informs;
3. what is deliberately **not** inferred.

Rolling docs/repositories are not immutable evidence; pin revision/date where the architecture depends on concrete behavior.

## 2. Workflow, Provenance, and Recovery

### AiiDA

- Source: Huber SP et al. *AiiDA 1.0, a scalable computational infrastructure for automated reproducible workflows and data provenance*. Scientific Data 7, 300 (2020). https://doi.org/10.1038/s41597-020-00638-4
- Project: https://github.com/aiidateam/aiida-core
- checked_at: 2026-09-17
- inspection_depth: primary paper + official project material
- claim_scope: persistent process state, provenance graph, recoverable scientific execution

Adopt: process/provenance separation and persistent execution-state patterns inform RunSpec/RunAttempt/Artifact provenance.

Do not infer: BioHarness must migrate pipelines to AiiDA, or provenance alone establishes scientific validity.

### Nextflow / nf-core

- https://www.nextflow.io/
- https://github.com/nextflow-io/nextflow
- https://nf-co.re/
- https://github.com/nf-core
- checked_at: 2026-09-17/18
- inspection_depth: official docs/repository patterns; concrete Genome-web integration audited separately at source-code level
- claim_scope: workflow execution, cache/resume, portable executors, reusable workflow/module practice

Adopt: keep Nextflow external as WorkflowExecutor; bind provider/workflow/input/configuration identity and explicit capabilities in BioHarness.

Do not infer: Nextflow cache identity equals BioHarness analysis identity; workflow completion equals universal validation; every integration provides async polling/idempotency/cancellation.

### Snakemake

- Köster J, Rahmann S. *Snakemake—a scalable bioinformatics workflow engine*. Bioinformatics 28, 2520-2522 (2012).
- https://github.com/snakemake/snakemake
- checked_at: 2026-09-17
- inspection_depth: primary paper + repository reference
- claim_scope: alternative mature workflow engine/reproducible composition

Adopt: normalize heterogeneous engines behind BioHarness contracts instead of forcing one executor.

### OpenLineage

- https://openlineage.io/
- https://github.com/OpenLineage/OpenLineage
- checked_at: 2026-09-17
- inspection_depth: official docs/repository overview
- claim_scope: Run/Job/Dataset lineage vocabulary/event patterns

Adopt: reuse compatible lineage vocabulary while retaining BioHarness scientific/validation/Finding/Decision/memory semantics.

### RO-Crate / Workflow Run RO-Crate

- https://www.researchobject.org/ro-crate/
- https://www.researchobject.org/workflow-run-crate/
- checked_at: 2026-09-17
- inspection_depth: official specification/documentation
- claim_scope: portable research/workflow-run metadata packaging

Adopt: prefer standards-compatible export/archive when practical.

Do not infer: metadata packaging guarantees replayability or long-term availability of all external inputs/environments.

## 3. Data and Execution Interface Standards

### GA4GH DRS

- https://www.ga4gh.org/product/data-repository-service-drs/
- checked_at: 2026-09-17
- inspection_depth: official product/spec documentation
- claim_scope: logical data identity separated from access location/mechanism

Adopt: reference pattern for `ResolvedDataRef`, supplemented by biological release and collection-member identity.

### GA4GH WES / TES / TRS

- https://www.ga4gh.org/product/workflow-execution-service-wes/
- https://www.ga4gh.org/product/task-execution-service-tes/
- https://www.ga4gh.org/product/tool-registry-service-trs/
- checked_at: 2026-09-17
- inspection_depth: official product/spec documentation
- claim_scope: workflow registry/execution/task boundary patterns

Adopt: avoid provider interfaces that unnecessarily prevent future standards alignment.

Do not infer: P0 must implement GA4GH compliance.

## 4. Policy and Authorization

### Open Policy Agent

- https://www.openpolicyagent.org/docs/
- https://github.com/open-policy-agent/opa
- checked_at: 2026-09-17
- inspection_depth: official docs/repository overview
- claim_scope: explicit policy decision separated from application/scientific logic

Adopt: keep PolicyDecision explicit/action-scoped and separate from ScientificAssessment/execution state.

Do not infer: a policy engine determines scientific identifiability or evidence strength.

## 5. Scientific-Validity References

### DESeq2

- Love MI, Huber W, Anders S. *Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2*. Genome Biology 15, 550 (2014).
- https://doi.org/10.1186/s13059-014-0550-8
- https://bioconductor.org/packages/DESeq2
- checked_at: 2026-09-17
- inspection_depth: primary paper + official Bioconductor guidance
- claim_scope: count semantics, design matrix, confounding/identifiability

Adopt: TaskSpec/Module contracts expose design/input assumptions; authorized execution can still be `NOT_IDENTIFIABLE` or `INCOMPATIBLE`.

### Gene Ontology enrichment guidance

- https://geneontology.org/docs/go-enrichment-analysis/
- checked_at: 2026-09-17
- inspection_depth: official guidance
- claim_scope: selected set, reference/background universe, mapping/annotation provenance

Adopt: tested/background universe, annotation release, identifier mapping, and multiple testing are scientific provenance/configuration.

### goseq / RNA-seq selection bias

- Young MD et al. *Gene ontology analysis for RNA-seq: accounting for selection bias*. Genome Biology 11, R14 (2010).
- https://doi.org/10.1186/gb-2010-11-2-r14
- checked_at: 2026-09-17
- inspection_depth: primary paper
- claim_scope: gene-selection bias including transcript-length effects

Adopt: enrichment method/background applicability may depend on how the gene set was generated.

### Replicate-aware single-cell DE

- Squair JW et al. *Confronting false discoveries in single-cell differential expression*. Nature Communications 12, 5692 (2021).
- https://doi.org/10.1038/s41467-021-25960-2
- checked_at: 2026-09-17
- inspection_depth: primary paper
- claim_scope: experimental-unit/biological-replicate handling in multi-sample scRNA-seq DE

Adopt: bulk -> single-cell pathway reuse must re-evaluate experimental unit/statistical assumptions and downstream evidence applicability.

## 6. Memory and Retrieval Research

### RAPTOR

- Sarthi P et al. *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval*. arXiv:2401.18059 (2024).
- https://arxiv.org/abs/2401.18059
- checked_at: 2026-09-17
- inspection_depth: paper
- claim_scope: multi-level hierarchical representation/retrieval

Adopt: hierarchy can organize/expand retrieval; exact lookup need not traverse root-to-leaf.

### HippoRAG / HippoRAG 2

- https://github.com/OSU-NLP-Group/HippoRAG
- checked_at: 2026-09-17
- inspection_depth: repository/project material
- claim_scope: graph/associative multi-hop retrieval

Adopt: candidate strategy for distributed research context.

Do not infer: hard policy/fatal contradictions should be probabilistic top-k retrieval.

### Agent Workflow Memory (AWM)

- *Agent Workflow Memory*. arXiv:2409.07429 (2024).
- https://arxiv.org/abs/2409.07429
- checked_at: 2026-09-17
- inspection_depth: paper
- claim_scope: reusable procedural routines from historical trajectories

Adopt: supports MemoryPathway concept.

Do not infer: generic task frequency/reward equals scientific reliability.

### TiMEM

- https://github.com/TiMEM-AI/TiMEM
- checked_at: 2026-09-17
- inspection_depth: repository/project material
- claim_scope: temporal/hierarchical long-horizon memory infrastructure

Adopt: candidate Memory Provider; BioHarness retains evidence/scope/lifecycle/Decision semantics.

### Graphiti

- https://github.com/getzep/graphiti
- checked_at: 2026-09-17
- inspection_depth: repository/project material
- claim_scope: temporal graph relations and multi-hop retrieval

Adopt: optional graph provider if workload justifies it; not mandatory P0 infrastructure.

## 7. Research-Agent and Literature Systems

### BioMedAgent

- https://www.nature.com/articles/s41551-026-01634-6
- checked_at: 2026-09-17
- inspection_depth: publication metadata/available article material + associated project resources; benchmark not reproduced
- claim_scope: biomedical agent combining tool use, analysis, memory/retrieval

Adopt: comparison point for agent capability; evaluate BioHarness on evidence-grounded applicability, provenance, version change, governed reuse/promotion.

### PaperQA2

- https://github.com/Future-House/paper-qa
- checked_at: 2026-09-17
- inspection_depth: repository/project material
- claim_scope: evidence-preserving literature retrieval/answer generation

Adopt: literature-derived memory retains source/evidence identity and remains distinct from provider/experimental evidence.

## 8. Concrete Research-Software Example: Schultz et al. 2026 EGT

- Schultz DT et al. *Topological mixing and irreversibility in animal chromosome evolution*. Science Advances 12, eadz5561 (2026).
- checked_at: 2026-09-17
- inspection_depth: uploaded paper methods/data-availability and architecture-relevant sections
- claim_scope: composable scientific software, Snakemake orchestration, graph use for a graph-shaped problem, sensitivity/alternative-explanation validation

Observed: separate `chrombase`, `genbargo`, `egt`, `chromsim`, `breakpointer2`; Snakemake orchestration; Neo4j used for a specific orthology/chromosome relationship problem; explicit alternative-explanation/sensitivity checks and GO-universe definition.

Adopt: keep scientific tools modular under reproducible orchestration; use graph infrastructure only for demonstrated graph-shaped needs; record method-specific sensitivity/alternative-explanation validation where relevant.

Do not infer: animal-specific BCnS ALG biology transfers directly to plants or BioHarness requires Neo4j.

## 9. Internal Asset: Genome-web TF Nextflow Pilot

- Repository: https://github.com/mumu-140/genome-web-backend
- branch observed: `main`
- **pinned inspected commit:** `05072cbbcd533ca59afa13996d8d0edd8f939c6e`
- checked_at: 2026-09-18
- inspection_depth: repository code + workflow configuration + README
- claim_scope: actual P0 launcher/executor/identity/provenance/validation capability boundary

Files inspected:

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

Observed:

- explicit species/UID/build/annotation registration and leading-zero UID preservation;
- table-based gene -> transcript -> protein resolution;
- fail-fast identity/file/tool validation;
- synchronous Python launcher + local Nextflow executor;
- per-run-root filesystem launch lock and explicit attempt directories;
- deep Nextflow cache/resume;
- tool/source fingerprints and invocation evidence;
- candidate BUNDLE validation and no automatic production publication;
- no provider-native idempotency key;
- no durable async external execution ID/polling/cancellation interface in inspected source;
- reconciliation after disconnect is limited;
- resolved member/manifest identity needs additional BioHarness-adapter provenance.

Adopt: use as P0 because it exercises real identity, reuse, failures, validation boundary, and publication separation. Wrap it rather than rewrite its biological logic.

Do not infer: async remote submission, distributed idempotency, exactly-once execution, Slurm/Kubernetes support, or generic Nextflow capabilities.

## 10. Evaluation References and Directions

Design references include BixBench-style scientific/data-analysis evaluation, LongMemEval-style long-horizon memory evaluation, AgentDojo-style tool/adversarial evaluation, and benchmark-quality auditing such as BenchGuard-style contamination/validity checks.

BioHarness has not reproduced their headline results.

Future matched-budget comparison should include:

```text
no persistent research memory
vs flat hybrid retrieval
vs graph/hierarchical expansion
vs human-authored reviewed pathways
vs automatically proposed pathways
```

Primary outcomes should emphasize scientifically correct completion **or correct blocking**, stale-knowledge misuse, repeated-error rate, provenance completeness, ambiguous-execution recovery, contradiction handling, independent-evidence accounting, and context/tool/token cost.

This benchmark design remains a hypothesis until executed.

## 11. Maintenance Rule

For every source that materially changes architecture, record:

1. exact source/link;
2. source type;
3. version/revision/date when available;
4. `checked_at`;
5. inspection depth;
6. claim scope;
7. BioHarness clause informed;
8. explicit non-inferences.

Prefer primary papers, official specs/docs, original repositories, and directly inspected internal source over secondary summaries.