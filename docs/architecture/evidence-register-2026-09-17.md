# BioHarness Architecture Evidence Register

Date: 2026-09-17
Status: Evidence/reference record for architecture review
Purpose: Record the external papers, standards, mature projects, and internal systems used to justify or constrain BioHarness architecture decisions.

This file is not a dependency lockfile and does not make any external system authoritative for BioHarness scientific decisions.

## 1. Evidence Handling Rule

For each source, BioHarness records:

- the capability or observation being borrowed;
- the architectural decision it informs;
- what is deliberately **not** inferred from the source;
- whether the source is a protocol, implementation, paper, benchmark, or internal asset.

A mature project can justify reuse of an implementation pattern without proving that the same design is optimal for BioHarness.

## 2. Scientific Workflow, Provenance, and Recovery

### AiiDA

Source:

- Huber SP et al. *AiiDA 1.0, a scalable computational infrastructure for automated reproducible workflows and data provenance*. Scientific Data 7, 300 (2020).
- https://doi.org/10.1038/s41597-020-00638-4
- https://github.com/aiidateam/aiida-core

Relevant evidence/patterns:

- persistent provenance as a first-class part of computational science;
- explicit process state and recoverable execution;
- separation between computation and the provenance graph describing it;
- reproducible links among input data, calculation processes, and output data.

BioHarness adoption:

- use AiiDA as a strong reference for process/provenance semantics and failure recovery;
- keep BioHarness `RunSpec`/`RunAttempt`/`Artifact`/`ValidationReport` semantics independent of any single engine;
- AiiDA may later be an execution/provenance provider if that reduces implementation burden.

Do not infer:

- that BioHarness must migrate all Nextflow/Snakemake pipelines to AiiDA;
- that generic provenance automatically establishes scientific validity.

### Nextflow and nf-core

Sources:

- https://www.nextflow.io/
- https://github.com/nextflow-io/nextflow
- https://nf-co.re/
- https://github.com/nf-core

Relevant evidence/patterns:

- reproducible workflow execution;
- process-level caching/resume;
- portable executors and container integration;
- community workflow/module metadata and testing practices.

BioHarness adoption:

- retain Nextflow as an external `WorkflowExecutor`;
- bind exact workflow revision, inputs, parameters, environment identity, and executor state to BioHarness Run records;
- do not duplicate DAG execution semantics inside the control plane.

Do not infer:

- that Nextflow cache identity is sufficient as BioHarness scientific identity;
- that workflow completion means validation passed.

### Snakemake

Sources:

- Köster J, Rahmann S. *Snakemake—a scalable bioinformatics workflow engine*. Bioinformatics 28, 2520-2522 (2012).
- https://github.com/snakemake/snakemake

BioHarness adoption:

- retain Snakemake as an alternative workflow provider, especially for existing laboratory and paper-derived workflows;
- normalize heterogeneous engines through BioHarness Run/Artifact contracts rather than forcing one engine.

### OpenLineage

Sources:

- https://openlineage.io/
- https://github.com/OpenLineage/OpenLineage

Relevant pattern:

- Job/Run/Dataset lineage event vocabulary and event-oriented integration.

BioHarness adoption:

- reuse compatible vocabulary/patterns where possible;
- add scientific context, validation, Decision, and memory semantics above generic lineage.

### RO-Crate and Workflow Run RO-Crate

Sources:

- https://www.researchobject.org/ro-crate/
- https://www.researchobject.org/workflow-run-crate/

Relevant pattern:

- portable packaging of research objects, workflow runs, inputs, outputs, software, and metadata.

BioHarness adoption:

- prefer standards-compatible export/archive packages over a proprietary bundle format when practical.

Do not infer:

- that metadata packaging guarantees future availability of every external input or execution environment.

## 3. Data and Execution Abstraction Standards

### GA4GH DRS

Source:

- https://www.ga4gh.org/product/data-repository-service-drs/

Relevant pattern:

- stable logical data identity separated from access mechanisms/locations.

BioHarness adoption:

- use the logical-identity versus resolved-access distinction when designing `ResolvedDataRef`;
- supplement generic resource identity with biological release semantics such as assembly, annotation release, and identifier namespace.

Do not infer:

- that DRS alone captures all plant/genome-specific version meaning.

### GA4GH WES / TES / TRS

Sources:

- https://www.ga4gh.org/product/workflow-execution-service-wes/
- https://www.ga4gh.org/product/task-execution-service-tes/
- https://www.ga4gh.org/product/tool-registry-service-trs/

Relevant pattern:

- clean boundaries among workflow discovery, workflow submission, and heterogeneous execution backends.

BioHarness adoption:

- avoid provider APIs that make future standards alignment impossible;
- no full standards-compliance requirement for P0.

## 4. Policy and Authorization

### Open Policy Agent

Sources:

- https://www.openpolicyagent.org/docs/
- https://github.com/open-policy-agent/opa

Relevant pattern:

- policy decision as an explicit, testable operation separate from application code.

BioHarness adoption:

- keep `PolicyDecision` distinct from `ScientificAssessment`;
- a future OPA adapter is possible, but BioHarness policy semantics remain its own contract.

Do not infer:

- that policy engines can determine whether a biological/statistical inference is scientifically identifiable.

## 5. Scientific Analysis Validity References

### DESeq2

Source:

- Love MI, Huber W, Anders S. *Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2*. Genome Biology 15, 550 (2014).
- https://doi.org/10.1186/s13059-014-0550-8
- Bioconductor vignette: https://bioconductor.org/packages/DESeq2

Relevant evidence:

- RNA-seq differential-expression models rely on explicit count/data semantics and a design matrix;
- confounding/design-rank problems are scientific/statistical constraints, not execution errors;
- method contracts must describe supported input semantics rather than relying on filename or superficial numeric type.

BioHarness adoption:

- `ScientificTaskSpec` and Module scientific contracts must expose design and input assumptions;
- an authorized workflow can still be scientifically `NOT_IDENTIFIABLE` or `INCOMPATIBLE`.

### Gene Ontology enrichment guidance

Source:

- Gene Ontology Consortium enrichment guidance: https://geneontology.org/docs/go-enrichment-analysis/

Relevant evidence:

- enrichment requires an explicit selected gene set and a defensible background/reference universe;
- annotation source and identifier mapping materially affect results.

BioHarness adoption:

- background universe, annotation release, mapping namespace, and multiple-testing behavior belong in the scientific contract/provenance.

### goseq / RNA-seq selection bias

Source:

- Young MD et al. *Gene ontology analysis for RNA-seq: accounting for selection bias*. Genome Biology 11, R14 (2010).
- https://doi.org/10.1186/gb-2010-11-2-r14

Relevant evidence:

- RNA-seq gene-set enrichment can be biased by gene-selection properties such as transcript length.

BioHarness adoption:

- enrichment method/background decisions may depend on how the input gene set was generated;
- downstream enrichment should retain provenance to upstream selection semantics.

### Replicate-aware single-cell differential expression

Source:

- Squair JW et al. *Confronting false discoveries in single-cell differential expression*. Nature Communications 12, 5692 (2021).
- https://doi.org/10.1038/s41467-021-25960-2

Relevant evidence:

- treating cells as independent biological replicates can inflate false discovery rates in multi-sample single-cell studies.

BioHarness adoption:

- bulk-to-single-cell pathway reuse must re-evaluate the experimental unit and statistical assumptions;
- unchanged downstream graph topology does not prove old evidence remains valid.

## 6. Memory and Retrieval Research

### RAPTOR

Source:

- Sarthi P et al. *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval*. arXiv:2401.18059 (2024).
- https://arxiv.org/abs/2401.18059

Relevant pattern:

- hierarchical representations can support retrieval across abstraction levels;
- storage hierarchy and retrieval strategy are separate design choices.

BioHarness adoption:

- keep research-abstraction hierarchy as an organization/expansion mechanism;
- do not require every exact lookup to traverse from domain root to leaf.

### HippoRAG / HippoRAG 2

Sources:

- https://github.com/OSU-NLP-Group/HippoRAG
- relevant papers linked from the project repository.

Relevant pattern:

- graph/associative retrieval can connect distributed evidence beyond flat semantic top-k.

BioHarness adoption:

- graph retrieval is a candidate provider/strategy for multi-hop research context;
- mandatory policy and fatal contradiction context remains deterministic, not probabilistic graph recall.

### Agent Workflow Memory (AWM)

Source:

- *Agent Workflow Memory*. arXiv:2409.07429 (2024).
- https://arxiv.org/abs/2409.07429

Relevant pattern:

- reusable procedural routines can be induced from historical trajectories and reused in later tasks.

BioHarness adoption:

- supports the Memory Pathway concept;
- pathway induction remains evidence- and scope-gated in scientific settings.

Do not infer:

- that frequency/reward in generic agent tasks equals scientific reliability.

### TiMEM

Sources:

- https://github.com/TiMEM-AI/TiMEM

Relevant pattern:

- temporal/hierarchical memory organization, consolidation, and long-horizon retrieval.

BioHarness adoption:

- candidate Memory Provider/reference;
- BioHarness retains evidence, scope, validity, and Decision/Policy semantics.

### Graphiti

Sources:

- https://github.com/getzep/graphiti

Relevant pattern:

- temporal graph edges, validity intervals, evolving relations, and multi-hop retrieval.

BioHarness adoption:

- candidate graph provider when real workloads justify it;
- graph infrastructure remains optional for P0.

## 7. Research-Agent and Literature Systems

### BioMedAgent

Source:

- 2026 Nature Biomedical Engineering publication and associated project resources describing an autonomous biomedical analysis agent.
- https://www.nature.com/articles/s41551-026-01634-6

Relevant pattern:

- biomedical analysis agents can combine tool use, interactive analysis, and memory/retrieval around real scientific tasks.

BioHarness adoption:

- use as a comparison point for research-agent capability;
- BioHarness differentiation should be evaluated around evidence-grounded scientific context, explicit applicability, provenance, version change, and governed promotion rather than the generic claim "agent + memory".

### PaperQA2

Sources:

- https://github.com/Future-House/paper-qa

Relevant pattern:

- literature retrieval and answer generation can retain source-level evidence rather than reducing papers to untraceable model recollection.

BioHarness adoption:

- literature-derived memories should preserve source identity and evidence location;
- literature retrieval remains distinct from provider data and experimental evidence.

## 8. Concrete Research-Software Example: Schultz et al. 2026 EGT

Source:

- Schultz DT et al. *Topological mixing and irreversibility in animal chromosome evolution*. Science Advances 12, eadz5561 (2026).

Relevant architecture observed in the Methods/data-availability description:

- data acquisition/database construction is separated into `chrombase`;
- embargo logic is handled by `genbargo`;
- downstream evolutionary analyses are packaged into `egt` subcommands;
- chromosome-mixing simulation uses `chromsim`;
- inversion analysis uses `breakpointer2`;
- reproducible orchestration uses Snakemake workflows;
- Neo4j is used for a specific orthology/chromosome relationship graph rather than as the universal scientific store.

Relevant scientific design lessons:

- the study explicitly audits homology-detection failure as an alternative explanation for dispersal patterns;
- taxonomic resampling tests sampling imbalance;
- UMAP/sentinel parameter sensitivity is tested rather than treating one visualization as ground truth;
- GO enrichment uses an explicit BCnS family universe and cross-checks results against GOATOOLS.

BioHarness adoption:

- treat research software as a composable ecosystem of independent tools/workflows with explicit provenance rather than forcing every method into one monolith;
- scientific validation should include alternative-explanation and sensitivity checks where the method requires them;
- graph databases should solve a demonstrated graph-shaped problem, not become a default requirement.

Do not infer:

- that EGT's animal-specific BCnS ALG model transfers directly to plant analysis;
- that a Neo4j deployment is required for BioHarness P0.

## 9. Existing Internal Asset: Genome-web TF Nextflow Pilot

Repository:

- https://github.com/mumu-140/genome-web-backend
- relevant files: `pipeline/nextflow/README.md`, `pipeline/nextflow/main.nf`

Existing useful properties:

- explicit species/UID/assembly/annotation registration;
- no implicit default species/build/output path;
- gene -> transcript -> protein joins use tables rather than guessed suffixes;
- leading-zero UID identity is preserved;
- invalid inputs/tool failures fail the batch rather than being silently skipped;
- deep content caching plus tool/parameter fingerprints;
- parameter-local recomputation: IQ-TREE changes do not require MAFFT rerun when alignment identity is unchanged;
- candidate bundle is independently verified and explicitly marked not authorized for production publication;
- attempts preserve invocation/tool/version/log/trace evidence;
- resume behavior depends on retained work/cache identity.

BioHarness adoption:

- use this as P0 because it already exercises real identity, cache, failure, candidate-validation, and publication-boundary semantics;
- wrap it as a provider rather than rewrite its biological rules.

## 10. Evaluation References and Directions

Candidate evaluation systems/directions include:

- BixBench: scientific/data-analysis task benchmarking;
- LongMemEval: long-horizon memory/update evaluation;
- AgentDojo: tool-use safety/adversarial evaluation;
- benchmark-quality work such as BenchGuard-style checks on benchmark contamination/validity.

BioHarness should use these as design references, not copy their headline metrics directly.

A future BioHarness benchmark should compare under matched models/tools/budgets:

```text
no persistent research memory
vs flat hybrid retrieval
vs graph/hierarchical expansion
vs human-authored reviewed pathways
vs automatically proposed pathways
```

Candidate primary outcomes:

- correct scientific task completion;
- correct refusal/blocking when design is not supportable;
- stale-knowledge misuse;
- repeated-error rate;
- provenance completeness;
- recovery from external execution ambiguity;
- contradiction handling;
- independent-evidence accounting;
- context/token/tool-call cost.

This evaluation design remains a hypothesis until executed.

## 11. Maintenance Rule

When a new source materially affects architecture, append:

1. exact source/link/version/date;
2. what capability/evidence was inspected;
3. the BioHarness clause it informs;
4. what BioHarness deliberately does not infer;
5. whether the source is implementation, protocol, paper, benchmark, or internal asset.

This register should favor primary papers, official specifications, and original repositories over secondary summaries.
