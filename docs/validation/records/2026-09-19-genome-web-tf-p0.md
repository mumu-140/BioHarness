# Genome-web TF P0 Reference Acceptance Evidence — 2026-09-19

Status: **fresh executable acceptance evidence** for the explicitly listed P0 reference scenarios only.  
BioHarness implementation revision: `952c3c1b71dad8e0e47ef38cd79c471a142fd564`  
Audited Genome-web revision: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`  
P0.1H base merged in `main`: `25313eff0df22db3f543768051f19c3aff994adc`

This record supports only **TF-01, TF-02, EXEC-01, EXEC-06, and DATA-01**. It does not promote any other scenario from `NOT_RUN`.

## 1. Execution Environment and Isolation

The acceptance run executed on `fwq10ys` (Anolis OS 7.9, Linux 3.10, host glibc 2.17) without replacing host glibc, Python, Java, or system packages.

All writable acceptance state was constrained to:

`/home/yangs/software/BioHarness-P0-Acceptance`

The existing Genome-web production tree was not mounted into the acceptance container. The existing HGT tool environment was mounted read-only.

Observed isolated runtime:

- acceptance image: `sha256:234679529cf3c9cbe9136b3e36787eabb812f56b8d9337b3fa7d27f82a39ae5c`
- image BioHarness HEAD: `952c3c1b71dad8e0e47ef38cd79c471a142fd564`
- provider checkout HEAD: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`
- container Python: 3.12.13
- OpenJDK: 21.0.12.1
- Nextflow: 25.10.4 build 11173
- provider Python: 3.10.12
- Biopython: 1.78
- MAFFT: 7.526
- IQ-TREE: 3.1.2
- `ps`: isolated container `/usr/bin/ps`
- production path visible inside acceptance container: **no**
- acceptance root writable inside acceptance container: **yes**
- `/data/miniconda3` writable inside acceptance container: **no**

Acceptance configuration SHA-256:

`f1cdef9b7353ab25161315afb5fb6499947bdf4df2c56baaa764b81aa35554d3`

Original two-genome fixture manifest SHA-256:

`e7e8d144754355ae25b44e9b719aeb8057f6309a235a9862c5acb2cee5da8984`

The fixture contains UIDs `90001` and `00902`.

## 2. Pre-Acceptance Hardening Observation

The first governed live attempt, using pre-hotfix BioHarness revision `d870a4fee66aaa4a9a264a779a337491c0a793eb`, exposed two environment/recovery issues before the final acceptance run:

1. the isolated container lacked `ps`, which Nextflow requires for task metrics, so both PREPARE tasks failed before scientific processing;
2. the exited wrapper remained a Linux zombie and `LocalProcessProbe` incorrectly treated the zombie as active because `kill(pid, 0)` succeeded and the process start token still matched.

The affected RunAttempt was explicitly resolved to `FAILED`; no automatic duplicate launch was issued.

A focused TDD hotfix was then produced:

- RED: `ae1b818ed16deeb4ab42bd8ce84713543217b53c`; CI #98 failed only because the zombie was incorrectly reported active;
- GREEN: `b1aa8b517ad327bd8327e7266df41787a1a8b349`; CI #99 passed with 72 tests;
- the same fix is present in the reference-integration revision `952c3c1b71dad8e0e47ef38cd79c471a142fd564`.

The acceptance-only Docker runtime was rebuilt with `procps`; no host/global package or glibc replacement was performed.

This failed attempt is retained as recovery/debug evidence and is **not** used as PASS evidence for the five scenarios below.

## 3. Final Governed Live Run

The final acceptance flow was created and executed through BioHarness services:

`TaskSpec -> current read authorization -> ResolvedDataRefs -> ScientificAssessment -> ResolvedConfiguration -> RunSpec -> fresh preflight -> current launch authorization -> durable submission intent -> ExecutionDescriptor -> RunAttempt -> external run.sh -> Nextflow/MAFFT/IQ-TREE -> artifact registration -> typed validation -> scoped MemoryCandidate`

Key identities:

- TaskSpec: `a3d6094b-fd83-4f5a-bbbb-9fd617755b5f`
- RunSpec: `6ce6eccb-8727-4d2e-87e9-02e3c3f29e0f`
- analysis hash: `f58c2163756df8a78a38e0ed56e760df5108eec5bd44ee7be17c134bbb027865`
- RunSpec hash: `12b8db1693027b12acae9831da6be3c54cffed7b3cb4afaf5f5012e75c8db4b9`
- RunAttempt: `1f43864d-5939-4b72-809c-5f16f17f0885`
- provider attempt: `bh-6ce6eccb-1`
- final RunAttempt state: `FINISHED`

Policy outcomes observed by the governed acceptance driver:

- `read_resolve = ALLOW`
- `launch = ALLOW`
- `production_publication = DENY`
- `canonical_mutation = DENY`

Provider candidate:

- status: `validated_candidate`
- `production_publication = NOT_AUTHORIZED`
- UIDs: `00902`, `90001`
- completed PREPARE tasks: 2
- completed MAFFT tasks: 4
- completed IQ-TREE tasks: 4
- completed BUNDLE tasks: 1

BioHarness registered 15 artifacts and independently re-hashed them after collection; mismatches: **0**.

Typed validation:

- `provider_contract = PASS`
- `artifact_integrity = PASS`
- `provenance_completeness = PASS`
- candidate profile evaluation: `PASS`
- ValidationEvaluation: `432dd198-20e2-4287-ab94-348b8ce643eb`

A scoped evidence-linked MemoryCandidate was recorded:

`ca20170b-ee10-4da2-8573-94270ddd54b4`

The successful RunAttempt contains 37 ordered RunEvents, including `AttemptCreated`, `AuthorizationChecked`, `SubmissionIntentRecorded`, `ExternalProcessBound`, `ExecutionStarted`, `ReconciliationResolved`, artifact discovery/registration events, and `CollectionFinished`.

## 4. Exact Input Identity

The BioHarness-resolved manifest consumed by the provider has SHA-256:

`1921f4dcc6aa02ffb2eb501e7f5841c5dfa4301d82a4baacc2062c056f9a21fa`

The provider's `invocation.json` independently recorded the same `genomes_sha256`, and the registered `resolved_manifest` artifact has the same digest.

ResolvedDataRef evidence:

| UID | Logical resource | member-manifest SHA-256 |
| --- | --- | --- |
| `00902` | `genomeweb:registered-genome:Beta_assembly:00902` | `5cda16e56435a947f4684dc2898428238a771f6e01b24405546a59f0eaa05d71` |
| `90001` | `genomeweb:registered-genome:Alpha_assembly:90001` | `fc7a672e887fcedada9807a3ea14dfb3e4a80f5491e2f0c2f680bca0bdbfc42` |

The frozen RunSpec points to those exact ResolvedDataRef IDs; the provider invocation consumed the resolved manifest rather than reinterpreting the original logical-resource strings.

## 5. Negative Cross-UID Fixture

A separate fixture was copied inside the isolated acceptance workspace and only the negative copy was changed: the Beta gene table was deliberately given the Alpha gene ID `Alpha_FamilyA_0` while retaining Beta UID `00902`.

The original fixture was not modified.

Observed provider result:

- exit code: `1`
- stderr: `FATAL: cross-uid ID collision: ('gene', 'Alpha_FamilyA_0')`
- provider attempt directories before resolution: unchanged after resolution
- scientific execution started: **false**
- no ID repair, aliasing, or retry was performed

## 6. Scenario Records

### TF-01 — Preserve leading-zero UID

- setup / fixture: two-genome fixture with `Beta_assembly / 00902`
- implementation revision: `952c3c1b71dad8e0e47ef38cd79c471a142fd564`
- provider revision: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`
- input identity: manifest digest `e7e8d144...`; consumed resolved digest `1921f4dc...`; Beta member-manifest digest `5cda16e5...`
- action: full governed live run
- observable assertions: `00902` remained in the ResolvedDataRef logical URI/biological identity, resolved manifest, frozen RunSpec input reference, provider-consumed candidate, and final candidate manifest
- forbidden behavior: coercion to `902` or silent aliasing
- expected vs observed: exact five-digit UID preserved
- outcome: **PASS**
- executed_at: 2026-09-18 23:55–23:56 +08:00

### TF-02 — Reject cross-UID identity conflict

- fixture: isolated conflicting copy with `Alpha_FamilyA_0` placed in the Beta/00902 gene table
- implementation revision: `952c3c1b71dad8e0e47ef38cd79c471a142fd564`
- provider revision: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`
- action / injected failure: resolve the deliberately conflicting fixture through BioHarness `ResolutionService` and the external Genome-web resolver
- observable assertions: provider returned exit 1 with explicit cross-UID collision; provider attempt directory set did not change
- forbidden behavior: ID repair/renaming, merging records, or starting scientific execution merely to continue
- expected vs observed: fail-fast before science execution
- outcome: **PASS**
- executed_at: 2026-09-19 00:00 +08:00

### EXEC-01 — Capability honesty

- implementation/provider revisions: as above
- action: capability snapshot recorded on the live RunAttempt
- observed snapshot: `mode=synchronous_process`, `native_idempotency_key=false`, `durable_external_execution_id=false`, `poll=false`, `reconcile_after_disconnect=limited`, `cancellation=unsupported`, `logs=true`, `trace=true`
- expected vs observed: matches the audited provider capability boundary
- outcome: **PASS**

### EXEC-06 — Explicit resume lineage

- implementation/provider revisions: as above
- action: inspect the actual provider invocation for the live RunAttempt
- observable assertion: provider command contains no `-resume`; no implicit `last` or other session identity was introduced by BioHarness
- forbidden behavior: implicit resume identity treated as scientific identity
- expected vs observed: automated resume remained disabled
- outcome: **PASS**

### DATA-01 — Resolved manifest/member provenance

- implementation/provider revisions: as above
- action: compare frozen ResolvedDataRef identities, provider invocation evidence, and registered artifact digest
- observable assertions: BioHarness resolved manifest SHA-256, provider `genomes_sha256`, and registered resolved-manifest artifact SHA-256 all equal `1921f4dc...`; per-genome member-manifest digests are stored independently
- forbidden behavior: treating mutable path strings alone as immutable consumed-data identity
- expected vs observed: exact consumed manifest/member provenance independently checkable
- outcome: **PASS**

## 7. Supporting Evidence

Runtime evidence intentionally remains outside git under the isolated acceptance root. Recorded files and SHA-256:

| Relative evidence path | SHA-256 |
| --- | --- |
| `logs/planning-preflight-952c3c1.json` | `94602a4d38521365e032cd1ea06b4ff58b46daae1636f774685a4a936ef6f46d` |
| `logs/live-acceptance-952c3c1.stdout` | `2b085e46bf43dce5a7141432c672478507a5fc5b42ebcc56f1d36006c4e8ee8d` |
| `logs/cross-uid-negative-952c3c1.json` | `9a7a5c4dcf5976fc984c09af502b6aa7685534008542dce4814e3e03f4f66525` |
| `logs/db-evidence-952c3c1.json` | `3d60d30e197d7cd5ddc52faa3e3b1bf8bc97b26eb3667226d69fc802dd21cf5f` |
| `logs/provider-evidence-952c3c1.json` | `8beca204e298f9a7c7ee1b0d9a580b7524e4f1a8730e8ea2f10ef01b38588442` |
| `logs/environment-952c3c1.txt` | `fab2304d147adedb7e9c0a10b46f181b0e84d1be328ef12ba7b18088d52a1106` |

Reference-integration GitHub CI on implementation revision `952c3c1...`: **95 passed** (CI #100).

A separate remote Core-only run, with no Genome-web checkout required by Core tests, completed:

`72 passed in 31.02s`

## 8. Scope Limits

This record does **not** claim:

- generic async polling, cancellation, exactly-once submission, Slurm/SSH/Kubernetes execution, or WES/TES compliance;
- execution of EXEC-02 through EXEC-05, EXEC-07, cache/reuse scenarios, or the remaining acceptance catalog;
- scientific correctness of unrelated RNA-seq/GO contracts;
- production publication or canonical promotion;
- full validation of every acceptance criterion in the broader P0 vertical-slice design.

Only the five scenarios explicitly recorded above move from `NOT_RUN`.
