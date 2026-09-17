# BioHarness Architecture Design

Date: 2026-09-17
Status: Draft for review
Scope: Architecture only; no implementation choices below should be treated as irreversible unless marked as an invariant.

## 1. Purpose

BioHarness is an internal research platform centered on the laboratory's study species, datasets, projects, and reproducible computational workflows.

Its primary goal is not to re-implement bioinformatics algorithms. It provides the governance and integration layer that makes existing tools, workflows, environments, models, compute resources, and research outputs understandable, reusable, reproducible, auditable, and easy to present.

The platform should answer, for every analysis:

- What data were used?
- Which software/workflow was used, at which version?
- Which parameters and environment were used?
- Why was this approach selected?
- What was produced?
- Which output is exploratory, candidate, validated, or canonical?
- Can another person or agent reproduce the same result?
- Can the workflow be reused with a different dataset or species?

## 2. Architectural Position

BioHarness is a **research control plane**, not a monolithic bioinformatics suite.

The system adopts the following mature engineering patterns:

- Modular monolith for the control plane
- Hexagonal architecture / ports and adapters for external capabilities
- Immutable runs and artifacts inspired by Git/Bazel/Nix-style content-addressed systems
- Reconciliation between desired and observed execution state, inspired by Kubernetes controllers
- CQRS-lite for separating scientific write models from presentation read models
- Registry patterns for datasets, tools, workflows, models, environments, and compute resources
- Provenance/lineage concepts compatible with OpenLineage and research-object standards
- GA4GH-like abstractions for data, tool/workflow, and execution interfaces
- External workflow engines such as Nextflow or Snakemake instead of a custom workflow language
- MCP/API/RPC/CLI integration instead of reimplementing existing tools

Scientific implementations remain external whenever practical.

## 3. Core Invariants

These rules are architectural invariants and should be difficult to bypass.

### I1. Core does not implement scientific algorithms

BioHarness manages scientific assets and lifecycle. Existing software is connected through adapters.

### I2. Analysis modules do not write canonical database state directly

A module writes outputs to its execution workspace. Outputs are validated and ingested by BioHarness.

### I3. Dataset, Run, and Artifact records are immutable by default

A rerun creates a new Run and new Artifacts. Existing scientific history is never overwritten in place.

### I4. Canonical state is a pointer, not a destructive overwrite

A new validated result can replace the current canonical pointer while older artifacts remain addressable.

### I5. Agents operate through the control plane for governed work

Agents may explore freely in designated scratch contexts, but official execution, publication, promotion, and state-changing actions use BioHarness APIs/contracts.

### I6. Frontend reads presentation models

The frontend does not need to understand Nextflow work directories, DESeq2 output layouts, EvoPM internals, or raw analysis filesystem structure.

### I7. Authoritative facts are not stored only in AI memory

Canonical references, policies, versions, decisions, datasets, and run metadata live in explicit registries/databases/Git-backed definitions.

## 4. High-Level Architecture

```text
                         Users / Agents
                              |
                    +---------+---------+
                    |                   |
                  Web UI          Agent Gateway
                    |            MCP / API / SDK
                    +---------+---------+
                              |
                 +------------v-------------+
                 |       CONTROL PLANE       |
                 |                          |
                 | Species / Projects       |
                 | Datasets / Resources     |
                 | Modules / Workflows      |
                 | Runs / Artifacts         |
                 | Policies / Decisions     |
                 | Validation / Promotion   |
                 | Search / Read Models     |
                 +------+----------+--------+
                        |          |
              +---------v--+   +---v----------------+
              | DATA PLANE |   | EXECUTION PLANE    |
              |            |   |                    |
              | PostgreSQL |   | Runner abstraction |
              | S3 / MinIO |   | Nextflow           |
              | Parquet    |   | Snakemake           |
              | Zarr/h5ad  |   | Docker/Apptainer   |
              | filesystem |   | SSH / Slurm         |
              +------------+   +----------+---------+
                                         |
                          +--------------v-------------+
                          |   CAPABILITY PROVIDERS      |
                          |                            |
                          | TBtools RPC/API            |
                          | nf-core                    |
                          | Galaxy                     |
                          | R / Bioconductor           |
                          | Python tools               |
                          | EvoPM / EGT / lab tools    |
                          | external APIs / MCP        |
                          | models / databases         |
                          +----------------------------+
```

## 5. Primary Domain Objects

The control plane should remain centered on a small stable domain model.

### 5.1 Species

Represents a long-lived biological research object.

Examples:
- Populus trichocarpa
- Arabidopsis thaliana
- Populus alba

Species owns or references canonical biological resources but does not own project-specific results.

### 5.2 Dataset

Represents a versioned input or reusable data product.

Examples:
- GenomeAssembly
- GeneAnnotation
- ProteinSet
- ReadSet
- ExpressionMatrix
- VariantSet
- PhenotypeTable
- PeakSet
- StructureSet

Datasets should have stable logical identifiers independent of physical storage path.

### 5.3 Project

Represents a research question or work context.

Projects reference Species and Datasets and contribute project-specific policies, decisions, runs, and results.

### 5.4 Module

Represents one reusable computational capability.

A module may be backed by:
- CLI
- Python/R package
- container
- REST API
- MCP server
- TBtools RPC
- remote service

The module contract describes capability, not implementation details.

### 5.5 Workflow

Represents a versioned DAG/composition of Modules.

Workflow definitions may be provided by:
- Nextflow
- Snakemake
- Galaxy
- CWL/WDL-compatible upstream systems
- a lightweight BioHarness orchestration definition when no external engine is required

BioHarness must not become another general-purpose workflow language unless a future requirement proves unavoidable.

### 5.6 Run

Represents one immutable execution of a module or workflow.

A Run freezes:
- workflow/module revision
- input dataset versions
- parameters
- resolved policy/context
- runtime environment
- model versions
- compute backend
- user/agent identity
- code commit/container digest where applicable
- timestamps and execution state

### 5.7 Artifact

Represents any produced output.

Examples:
- BAM
- VCF
- DEG table
- MotifSet
- network
- tree
- embedding
- figure
- HTML report
- model

Artifacts are versioned/immutable and may be promoted to higher trust states.

### 5.8 Decision

Represents scientific or operational choices that should remain inspectable.

Examples:
- why one genome became canonical
- why one parameter set became the default
- why one workflow was chosen over alternatives
- why a candidate result was promoted
- why a sample was excluded

Decision is intentionally first-class because reproducibility requires preserving rationale, not only commands.

### 5.9 Resource

Represents reusable infrastructure or external capability.

Resource subtypes include:
- reference resource
- software/tool
- runtime/environment
- model
- external database
- API/MCP endpoint
- compute node/cluster

## 6. Species-Centered and Project-Centered Axes

BioHarness uses a two-axis model.

### Species Hub

Stores long-lived shared assets:
- reference genomes
- annotations
- proteomes
- gene-ID namespaces/mappings
- functional annotations
- orthology
- expression atlases
- variants
- phenotypes
- structures
- tracks

### Project Workspace

Stores research context:
- project-specific dataset selections
- project policies
- analysis runs
- experimental comparisons
- decisions
- reports
- candidate/validated results

Projects reference Species assets; they do not duplicate canonical files unnecessarily.

## 7. Registries

BioHarness uses registries instead of implicit filesystem conventions.

### 7.1 Dataset Registry

Stable logical IDs resolve to one or more physical locations.

Example:

```text
poptr/genome/v4.1
   -> s3://bioharness/species/poptr/genome/v4.1.fa.gz
```

Workflows reference logical IDs rather than `/data3/...` paths.

### 7.2 Module Registry

Records capability metadata:
- identifier
- version
- provider
- input/output types
- parameter schema
- runtime requirements
- references
- validation hooks
- documentation/rationale

### 7.3 Workflow Registry

Records:
- workflow ID and version
- source repository
- revision/tag/commit
- engine
- input/output contracts
- parameter schema
- reference publication if relevant
- validation status

### 7.4 Resource Registry

Tracks reusable environments, tools, models, references, APIs, MCP servers, and compute infrastructure.

### 7.5 Presentation Registry

Optional registry describing how artifact types may be rendered.

Examples:
- ExpressionMatrix -> heatmap/PCA/expression viewer
- VariantSet -> table/genome track
- Network -> graph viewer
- Tree -> phylogeny viewer
- MotifSet -> motif/logo/evolution viewer

This avoids hard-wiring every scientific type into frontend code.

## 8. Ports and Adapters

Core business logic uses ports. External systems implement adapters.

### 8.1 Tool Port

Conceptual operations:
- describe capability
- health/version
- validate request
- execute/invoke
- collect result metadata

Adapters may include:
- MCPAdapter
- RESTAdapter
- CLIAdapter
- TBtoolsRPCAdapter
- PythonAdapter
- RAdapter

### 8.2 Workflow Port

Adapters:
- NextflowAdapter
- SnakemakeAdapter
- GalaxyAdapter

### 8.3 Compute Port

Adapters:
- LocalRunner
- DockerRunner
- ApptainerRunner
- SSHRunner
- SlurmRunner

### 8.4 Storage Port

Adapters:
- LocalFilesystem
- S3/MinIO
- PostgreSQL metadata
- optional graph/vector stores when justified by real use cases

The initial system should not require every adapter to exist.

## 9. Module Contract

A module is a typed capability declaration, not an arbitrary script path.

Illustrative manifest:

```yaml
id: transcriptomics.deseq2
version: 1.0.0

inputs:
  counts:
    type: ExpressionCounts
  samples:
    type: SampleSheet

outputs:
  deg:
    type: DifferentialExpressionTable
  qc:
    type: QCReport

parameters:
  design:
    type: string
    required: true
  alpha:
    type: number
    default: 0.05

provider:
  kind: container
  image: example/deseq2@sha256:...

resources:
  cpu: 4
  memory: 16Gi

knowledge:
  purpose: Differential expression analysis from count matrices
  references: []
  parameter_notes: {}
  interpretation_notes: {}
```

The knowledge section is important for teaching and transparent AI use. A beginner should be able to inspect what a module does and why.

## 10. Analysis Lifecycle

The platform recognizes five research behaviors.

### Explore

Free-form or semi-structured exploratory analysis.

Outputs are EXPERIMENTAL by default.

### Reproduce

Reconstruct a published or external method using publication, supplementary material, code, environment, reference data, expected outputs, and validation checks.

Once verified, the reconstructed method becomes a reusable lab workflow.

### Build

Develop a new lab module/workflow.

New methods must declare inputs, outputs, runtime, parameters, provenance requirements, and validation rules before becoming reusable shared assets.

### Optimize

Treat parameter/software comparisons as explicit experiments.

An optimization experiment stores:
- baseline
- candidate runs
- metrics
- constraints
- selection criteria
- final Decision

### Publish/Promote

Validated outputs may become shared/canonical laboratory results.

## 11. Run State Machine

Execution state and scientific trust state are separate.

### Execution state

```text
DRAFT
  -> QUEUED
  -> RUNNING
  -> COLLECTING
  -> VALIDATING
  -> SUCCEEDED

Failures may produce:
FAILED
CANCELLED
```

### Artifact trust state

```text
EXPERIMENTAL
   -> CANDIDATE
   -> VALIDATED
   -> CANONICAL
```

Promotion should create an auditable Decision and update a pointer. It must not rewrite history.

## 12. Canonical Pointer Model

Example:

```text
Species: Populus trichocarpa
Resource: reference-genome

canonical -> dataset:poptr-genome-v4.1
```

Later:

```text
canonical -> dataset:poptr-genome-v5.0
```

v4.1 remains retrievable for reproducibility of historical projects.

The same model applies to:
- species references
- workflow defaults
- validated analysis outputs
- project reports
- expression atlases
- parameter presets

## 13. Provenance Graph

Every official result should be traversable backward.

```text
Artifact
  <- Run
      <- Workflow/Module revision
      <- Parameters
      <- Runtime Environment
      <- Model revision
      <- Input Datasets
      <- Resolved Policies
      <- User/Agent
```

The schema should remain compatible with established lineage/research-object approaches rather than inventing a completely isolated vocabulary.

## 14. Reuse and Content-Addressed Execution

BioHarness should compute a reproducibility signature from stable inputs such as:

```text
RunSignature = hash(
  module/workflow revision
  + input artifact hashes
  + normalized parameters
  + runtime/container digest
  + relevant model revisions
)
```

If an identical successful run already exists, BioHarness can offer reuse instead of recomputation.

This mechanism should initially be advisory. Automatic reuse can be enabled only after validation proves signatures sufficiently complete.

## 15. Policy and Context Inheritance

Policies are hierarchical.

```text
Lab Policy
   -> Species Policy
      -> Project Policy
         -> Workflow Policy
            -> Run Overrides
```

The resolved context is frozen into each official Run.

Example:

```text
Lab:
  raw data immutable
  official outputs require provenance

Species:
  canonical genome = poptr-v4.1

Project:
  exclude sample X23
  batch variable = project

Workflow:
  minimum replicates = 3
  FDR threshold = 0.05
```

This architecture replaces one oversized global agent instruction file with scoped, composable policy.

## 16. Agent Governance

AI agents are clients of BioHarness, not alternative sources of truth.

### Read path

Low-risk actions:
- search datasets
- inspect metadata
- inspect workflows
- view results
- summarize provenance

These may execute directly.

### Governed write path

State-changing actions:
- register dataset
- create or modify shared workflow
- launch official run
- change canonical resource
- promote artifact
- publish shared result

These pass through validation, authorization, and audit rules.

### Scratch analysis

Agents may use a scratch workspace for exploratory code and ad hoc analysis. Scratch outputs are not shared/canonical until explicitly registered and promoted.

This preserves the productivity of coding agents without turning the shell into the laboratory's source of truth.

## 17. Frontend Read Architecture

The frontend consumes read models produced by the control plane.

It should not parse raw scientific work directories.

Initial top-level navigation:

- Species
- Projects
- Data
- Workflows
- Analyses
- Results
- Ask / Agent

Default views show canonical/validated outputs. Historical, candidate, and experimental outputs are available through advanced/history views.

### Contextual capabilities

Tools should be discovered from object type rather than exposed as a giant flat menu.

Example:

```text
ExpressionMatrix
  -> PCA
  -> DEG
  -> WGCNA
  -> clustering
  -> visualization
```

### CQRS-lite

Write-side scientific state may remain normalized and provenance-rich.

Read-side presentation models can be denormalized/materialized for efficient frontend use.

Example read models:
- species_summary
- project_summary
- canonical_resource
- published_analysis
- published_gene
- published_expression
- published_network
- published_motif

## 18. Storage Responsibilities

### PostgreSQL

Use for:
- domain metadata
- relationships
- policies
- run/job state
- provenance indexes
- decisions
- registry metadata

### S3/MinIO or compatible object storage

Use for:
- FASTQ
- BAM/CRAM
- VCF
- BigWig
- structures
- reports
- large binary outputs

### Scientific matrix formats

Prefer domain-appropriate formats such as:
- Parquet
- Zarr
- HDF5/h5ad

Do not put large matrix/file payloads into relational tables without a specific reason.

### Optional stores

Graph/vector/search databases should be adapters added only when a demonstrated workload benefits from them.

## 19. External Capabilities to Reuse

BioHarness should prefer integration over reimplementation.

Candidate providers include:

- nf-core / Nextflow for standard pipelines
- Snakemake for custom research workflows
- Galaxy when interactive history/workflow functionality is useful
- TBtools through RPC/API where capabilities are exposed
- BioContainers/OCI images for reproducible runtimes
- IGV/JBrowse for genomic visualization
- Cytoscape-compatible approaches for networks
- existing model registries/weights rather than local duplicated model copies
- external databases/APIs via adapters
- MCP servers for agent-facing tool integration

Lab-developed scientific software such as EvoPM remains in its own repository and is registered as a versioned provider/module.

## 20. Lessons Adopted from Existing Biological Systems

### PlantMDCS

Adopt:
- species/multi-omics database orientation
- browser presentation
- decoupling of database management and user-facing analysis
- low-friction access

Do not adopt as a core constraint:
- tight coupling between the platform and every built-in scientific function

### TBtools

Adopt:
- biological usability
- practical tool coverage
- low learning barrier
- RPC/API/plugin direction where available

Do not reproduce:
- mature scientific tools already provided by TBtools

### FlowKit

Adopt:
- explicit task lifecycle
- read-only versus state-changing routing
- evidence-backed review
- validation gates
- context/policy discipline

Translate these concepts into scientific governance rather than copying its coding-agent workflow literally.

### Reproducible research software patterns

The 2026 Schultz et al. chromosome-evolution study is representative of modern computational biology: multiple purpose-specific tools and repositories are coordinated through reproducible workflows rather than merged into one giant executable. BioHarness should make such ecosystems easier to register, reproduce, inspect, and reuse instead of forcing them into one codebase.

## 21. Source-of-Truth Boundaries

### Git

Authoritative for:
- workflow/module definitions
- scripts
- manifests
- policy definitions intended for code review
- documentation
- architecture decisions

### Database

Authoritative for:
- Species/Dataset/Project metadata
- Run state
- Artifact metadata
- promotion state
- Decisions
- registry indexes

### Object storage

Authoritative for:
- large immutable file content

### AI memory / summaries

Non-authoritative convenience layer only.

## 22. Repository Strategy

Initial development uses one repository:

```text
BioHarness/
```

The control plane remains a modular monolith.

Scientific tools with independent identity remain in their existing repositories.

A future split may introduce a second private laboratory configuration repository if needed:

```text
BioHarness       # platform
BioHarness-Lab   # private lab configuration/policies/resource bindings
```

Do not split frontend/backend/agent/registry into independent repositories at the beginning.

## 23. Intended Repository Boundaries

The implementation may evolve, but the expected top-level organization is:

```text
apps/
  web/
  api/

core/
  species/
  datasets/
  projects/
  modules/
  workflows/
  runs/
  artifacts/
  decisions/
  resources/
  policies/

adapters/
  tools/
  workflow/
  compute/
  storage/

registry/
  modules/
  workflows/
  resources/
  schemas/

policies/
  lab/
  species/
  project-templates/

docs/
  architecture/
  decisions/
  contracts/
  plans/

tests/
infra/
```

This is a logical boundary proposal, not a mandate to create every empty directory immediately.

## 24. Deliberate Non-Goals for V1

BioHarness V1 should not attempt to:

- replace Nextflow/Snakemake
- replace TBtools/Galaxy
- implement Kubernetes-like distributed infrastructure
- build a general LIMS
- implement every omics analysis
- create a universal ontology for all biology
- require Neo4j/vector DB/Kubernetes
- automatically trust AI-generated analysis
- expose every experimental run on the public-facing UI
- solve authentication/authorization for external multi-tenant deployment

The first release is an internal laboratory platform.

## 25. Recommended V1 Vertical Slice

The first implementation should prove the architecture with one species, one shared dataset family, one standard workflow, and one lab-specific workflow.

Suggested slice:

```text
Species: Populus trichocarpa

Shared resources:
  canonical genome
  annotation
  proteome

Standard workflow:
  RNA-seq or a smaller expression analysis workflow

Lab workflow:
  EvoPM or another existing laboratory analysis

Required capabilities:
  Dataset registry
  Resource registry
  Module/workflow registry
  Run lifecycle
  Artifact ingestion
  provenance
  canonical pointer
  basic species/project frontend read model
```

Success means both workflows can be registered and executed through the same control-plane abstractions without embedding their scientific internals into the core.

## 26. Architecture Acceptance Criteria

The architecture is considered successfully implemented when the following statements are true:

1. A new tool can be added through an adapter/manifest without modifying unrelated core domains.
2. A new workflow can consume registered datasets by logical ID and produce registered artifacts.
3. Every official artifact can be traced to exact inputs, parameters, workflow/module version, environment, and executor.
4. Re-running an analysis creates a new immutable Run rather than overwriting the prior result.
5. A validated result can be promoted to canonical without deleting prior versions.
6. The frontend can present canonical scientific results without understanding raw workflow output layout.
7. An agent can discover datasets/workflows and launch governed runs without direct database or uncontrolled filesystem manipulation.
8. Project/species/lab policies resolve deterministically and the resolved context is frozen with the Run.
9. Existing software can be connected through MCP/API/RPC/CLI instead of being reimplemented.
10. A laboratory member can determine which result is official and why it was selected.

## 27. Open Questions Requiring Design Approval Before Implementation

The architecture intentionally leaves the following implementation decisions open until the V1 slice is confirmed:

- primary backend language/framework
- frontend framework
- exact registry manifest schema
- whether workflow definitions live fully in Git or are mirrored into the database
- local filesystem versus MinIO for the first deployment
- exact scheduler/queue implementation for V1
- authentication model for an internal network
- how much existing server inventory should be integrated initially
- first standard workflow used as the architecture test
- first lab-specific workflow used as the architecture test

These are implementation choices within the framework and should not change the invariants above.
