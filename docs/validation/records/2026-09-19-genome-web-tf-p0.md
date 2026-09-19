# Genome-web TF P0 Reference Acceptance Evidence — 2026-09-19

Status: **fresh executable acceptance evidence** for the explicitly listed P0 reference scenarios only.  
BioHarness implementation revision: `5e9b52c99c8c9e09494d5aed1394a5368d4a09a5`  
Audited Genome-web revision: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`  
P0.1H base merged in `main`: `25313eff0df22db3f543768051f19c3aff994adc`

This record supports only **TF-01, TF-02, EXEC-01, EXEC-06, and DATA-01**. It does not promote any other scenario from `NOT_RUN`.

## 1. Execution Environment and Isolation

The acceptance run executed on `fwq10ys` (Anolis OS 7.9, Linux 3.10, host glibc 2.17) without replacing host glibc, Python, Java, or system packages.

All writable acceptance state was constrained to:

`/home/yangs/software/BioHarness-P0-Acceptance`

The fresh current-head run used the isolated session:

`/home/yangs/software/BioHarness-P0-Acceptance/sessions/20260919-live3`

The existing Genome-web production tree was not mounted into the acceptance container. The exact audited provider checkout under the acceptance workspace and the two-genome fixture were mounted read-only. The existing HGT runtime tool directory was mounted read-only.

Observed isolated runtime:

- acceptance image: `sha256:c29437bd8fc6b5055d5334f873ba9bf54431e67d5a7c9dc14a2b1b7a344fa23a`
- image / BioHarness checkout HEAD: `5e9b52c99c8c9e09494d5aed1394a5368d4a09a5`
- provider checkout HEAD: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`
- provider checkout dirty files: `0`
- container Python: 3.12.13
- OpenJDK: 21.0.12.1
- Nextflow: 25.10.4 build 11173
- provider Python: 3.10.12
- Biopython: 1.78
- MAFFT: 7.526
- IQ-TREE: 3.1.2
- `ps`: present in the isolated container
- production path visible inside acceptance container: **no**
- acceptance root writable inside acceptance container: **yes**
- provider checkout / biological fixture / `/data/miniconda3`: mounted read-only

The audited launcher sets a run-root-scoped `NXF_HOME` with `NXF_OFFLINE=true`. The exact Nextflow 25.10.4 one-jar was therefore staged only inside the isolated run root before launch:

`sessions/20260919-live3/runs/runtime/framework/25.10.4/nextflow-25.10.4-one.jar`

SHA-256: `9897f09ee7116bdf3c6beb202210380e2daead237af07078e8b0bf97c29b7a66`.

Post-run read-only checksum verification of the existing production Genome-web tree matched the pre-run baseline for all ten inspected TF/runtime files:

| Production file | SHA-256 |
| --- | --- |
| `pipeline/config.sh` | `76fb20c7e754443714dbf0abb0a4fc50eb7cc4fa1293bea7c05a572221d27b39` |
| `pipeline/nextflow/run.sh` | `ae0361e90b103719fd345f70cd07ec54d61d43a6969030bc056307c4afe858f1` |
| `pipeline/nextflow/scripts/run.py` | `33f497e46c6f35efa0f0ab61ab82831789f772181d0f817b29c1affdc7674cab` |
| `pipeline/nextflow/main.nf` | `cf99b2b67fea5f2398b255d17ba89183ca5f7a602591077b9722d4ddf9cfc278` |
| `pipeline/nextflow/nextflow.config` | `167591f2b3037acbafd2fa38875403524af70a6515ac5ef64f8cedb41e7610e3` |
| `pipeline/nextflow/scripts/validate_genomes.py` | `cdde71c4e37988906eda3b0e91774b8382c75d819da4434b5d379bdeb5454814` |
| `pipeline/nextflow/scripts/assemble_tf_bundle.py` | `1248b6f684bfc5107e6c5d1b145ab41400a96d3aeb1846b258e62903c63881c4` |
| `pipeline/scripts/build_tf_trees.py` | `1c02af33cd6a38f0cc1fce0b4f51ea4c88ad2472657a866844a5a596dbdcb95f` |
| `pipeline/scripts/build_tf_tree_summary.py` | `5edacf117dcf0f194209bb15da976a42ae37dbc4ef675a5a4bf90f5560211bc3` |
| `pipeline/scripts/verify_tf_tree_summary.py` | `49a3639c6c12b55db6818ba9d457f3f0e4d16cccd4656dc73752e7288d0278e0` |

The production `config.sh` already differed from the audited repository revision before acceptance. Live acceptance therefore used the clean detached audited checkout under the isolated acceptance workspace rather than the production tree.

Current-head acceptance configuration SHA-256:

`157d43d048d14605f96436c035266a556420ad2df5d0ed702e62c796bc16a7b7`

Original two-genome fixture manifest SHA-256:

`e7e8d144754355ae25b44e9b719aeb8057f6309a235a9862c5acb2cee5da8984`

The fixture contains UIDs `90001` and `00902`.

## 2. Pre-Acceptance Hardening Observations

The first governed live attempt on the earlier reference head `d870a4fee66aaa4a9a264a779a337491c0a793eb` exposed two environment/recovery issues before the final accepted run:

1. the isolated container lacked `ps`, which Nextflow requires for local task metrics;
2. an exited wrapper could remain a Linux zombie and `LocalProcessProbe` originally treated that zombie as active because `kill(pid, 0)` succeeded and the process start token still matched.

The failed attempt was preserved as failure evidence; no automatic duplicate launch was issued.

A focused RED → GREEN fix added zombie-state detection in `LocalProcessProbe` at `952c3c1b71dad8e0e47ef38cd79c471a142fd564`. Subsequent commits pinned the reference runtime executables and hardened launch preflight so Nextflow, provider Python/Biopython, MAFFT, IQ-TREE3, and `ps` are observed and compared with the frozen `ResolvedConfiguration.environment_contract` before external launch.

The current acceptance revision `5e9b52c99c8c9e09494d5aed1394a5368d4a09a5` includes both fixes and was re-run from a fresh isolated database/run session.

## 3. Current-Head Dry Run and Governed Live Run

The current-head dry run produced only a preview; it did not execute the resolver or launcher. It showed:

- `read_resolve = ALLOW`
- `launch = ALLOW`
- `production_publication = DENY`
- `canonical_mutation = DENY`
- audited provider revision `05072cbb...`
- all planning/control/run/artifact paths inside the isolated `live3` session
- invocation through the audited `bash .../pipeline/nextflow/run.sh` boundary

The governed live flow was then executed through BioHarness services:

`TaskSpec -> current read authorization -> ResolvedDataRefs -> ScientificAssessment -> ResolvedConfiguration -> RunSpec -> fresh GenomeWebTFPreflight -> current launch authorization + durable SubmissionIntent -> materialized ExecutionDescriptor -> RunAttempt -> external Genome-web run.sh -> Nextflow/MAFFT/IQ-TREE -> artifact registration -> typed validation -> scoped MemoryCandidate`

Key identities:

- TaskSpec: `bbdd22f1-d38a-456c-af89-b3e816568472`
- RunSpec: `9d0768e6-b78e-4a6e-979b-51fb4453c75c`
- analysis hash: `f58c2163756df8a78a38e0ed56e760df5108eec5bd44ee7be17c134bbb027865`
- RunSpec hash: `d2be293fe2a46c11a0780b0c6007490cf1a154d0fd24bceb27a99923ea486600`
- RunAttempt: `3600c607-fbdb-4ca8-bfa1-928d4cae1cb6`
- provider attempt: `bh-9d0768e6-1`
- final RunAttempt state: `FINISHED`
- executed_at: 2026-09-19 01:44:46 +08:00

The durable `SubmissionIntentRecorded.preflight_evidence` captured:

- exact RunSpec hash;
- exact audited provider checkout revision;
- resolved manifest and per-genome member-manifest digests;
- `launcher_help = PASS`;
- `nextflow = 25.10.4`;
- `provider_python = 3.10.12`;
- `biopython = 1.78`;
- `mafft = 7.526`;
- `iqtree3 = 3.1.2`;
- `ps = PASS`.

Provider candidate:

- status: `validated_candidate`
- `production_publication = NOT_AUTHORIZED`
- UIDs: `00902`, `90001`
- completed PREPARE tasks: 2
- completed MAFFT tasks: 4
- completed IQ-TREE tasks: 4
- completed BUNDLE tasks: 1
- failed/cached tasks: 0

BioHarness registered 15 artifacts. Typed validation produced:

- `provider_contract = PASS`
- `artifact_integrity = PASS`
- `provenance_completeness = PASS`
- candidate profile evaluation: `PASS`
- ValidationEvaluation: `63a764ee-ffb6-4c73-a8de-c5ffe9bcaaa2`

A scoped evidence-linked MemoryCandidate was recorded:

`de3387db-c711-4a86-8778-d5eb071c7954`

with status `candidate`; it was not promoted to policy, finding, canonical state, or production publication.

## 4. Exact Input Identity and UID Lineage

The BioHarness-resolved manifest consumed by the provider has SHA-256:

`1921f4dcc6aa02ffb2eb501e7f5841c5dfa4301d82a4baacc2062c056f9a21fa`

The provider `invocation.json` independently recorded the same `genomes_sha256`, and the registered `resolved_manifest` artifact has the same digest.

ResolvedDataRef evidence:

| UID | Logical resource | member-manifest SHA-256 |
| --- | --- | --- |
| `00902` | `genomeweb:registered-genome:Beta_assembly:00902` | `5cda16e56435a947f4684dc2898428238a771f6e01b24405546a59f0eaa05d71` |
| `90001` | `genomeweb:registered-genome:Alpha_assembly:90001` | `fc7a672e887fcedada9807a3ea14dfb3e4a80f5491e2f0c2f680bca0bdbfc42` |

Fresh lineage comparison confirmed:

- planning resolved-manifest SHA = provider `genomes_sha256` = recorded ResolvedDataRef manifest SHA;
- planning UIDs = `00902`, `90001`;
- candidate UIDs = `00902`, `90001`;
- leading-zero UID preservation = true.

## 5. Negative Cross-UID Fixture

A separate fixture copy was created only inside `sessions/20260919-live3/negative`. The Beta gene table was deliberately given the Alpha gene ID `Alpha_FamilyA_0` while retaining Beta UID `00902`. The original fixture was not modified.

The negative case was passed through BioHarness `ResolutionService` and the external audited Genome-web resolver.

Observed provider result:

- executed_at: 2026-09-19 01:45:56 +08:00
- exit code: `1`
- stderr: `FATAL: cross-uid ID collision: ('gene', 'Alpha_FamilyA_0')`
- scientific execution started: **false**
- provider attempt entries: none
- ID repair/renaming/retry: none

## 6. Capability and Resume Boundaries

The current-head capability snapshot observed against the audited checkout is:

```text
mode = synchronous_process
native_idempotency_key = false
durable_external_execution_id = false
poll = false
reconcile_after_disconnect = limited
cancellation = unsupported
logs = true
trace = true
```

A separate materialization/probe of the actual successful RunSpec/RunAttempt produced:

- resume-related configuration keys: none;
- resume-related invocation args: none;
- implicit `resume last`: false.

This supports only the P0 claim that automated/implicit resume is disabled. It does not claim durable explicit resume lineage for a later separate launch.

## 7. Scenario Records

### TF-01 — Preserve leading-zero UID

- fixture: two-genome fixture with `Beta_assembly / 00902`
- implementation revision: `5e9b52c99c8c9e09494d5aed1394a5368d4a09a5`
- provider revision: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`
- action: full governed live run plus independent UID-lineage check
- observable assertions: `00902` remained exact in resolved identity, planning manifest, provider-consumed manifest, and final candidate
- forbidden behavior: coercion to `902` or silent aliasing
- expected vs observed: exact five-digit UID preserved
- outcome: **PASS**

### TF-02 — Reject cross-UID identity conflict

- fixture: isolated conflicting copy with `Alpha_FamilyA_0` in the Beta/00902 gene table
- implementation revision: current head above
- provider revision: audited revision above
- action: resolve through BioHarness `ResolutionService` and external Genome-web resolver
- observable assertions: provider exit 1 with explicit cross-UID collision; no provider attempt entry; no scientific execution
- forbidden behavior: ID repair/renaming, merging records, retry, or starting science merely to continue
- expected vs observed: fail-fast during provider resolution
- outcome: **PASS**

### EXEC-01 — Capability honesty

- action: query current reference executor capability snapshot against the actual audited checkout
- observed snapshot: synchronous process; no native idempotency key, durable external execution ID, polling, or cancellation; limited reconciliation; logs/trace available
- expected vs observed: matches audited capability boundary
- outcome: **PASS**

### EXEC-06 — Explicit resume lineage

- action: materialize the actual successful live RunSpec/RunAttempt and inspect the current executor invocation
- observable assertions: no resume configuration key and no `-resume` / implicit `last` argument
- forbidden behavior: implicit resume identity treated as scientific identity
- expected vs observed: automated resume remained disabled
- outcome: **PASS**

### DATA-01 — Resolved manifest/member provenance

- action: compare frozen ResolvedDataRefs, provider invocation evidence, registered artifact identity, and UID-lineage record
- observable assertions: BioHarness manifest SHA, provider `genomes_sha256`, and registered resolved-manifest digest agree; per-genome member-manifest digests remain independently stored
- forbidden behavior: mutable path strings alone standing in for immutable consumed-data identity
- expected vs observed: exact consumed manifest/member provenance independently checkable
- outcome: **PASS**

## 8. Supporting Evidence

Runtime evidence remains outside git under the isolated `live3` session. Recorded evidence and SHA-256:

| Relative evidence path | SHA-256 |
| --- | --- |
| `acceptance.toml` | `157d43d048d14605f96436c035266a556420ad2df5d0ed702e62c796bc16a7b7` |
| `logs/dry-run.json` | `82810e1e12c255f831b48a054b6cbc77e5625ffeccf73d77083ab3c5c9e4f364` |
| `logs/governed-live.json` | `65b64ef1a17f09f7e93d9974fba0e9dbd2e382fff5bcd0f0efb788481594d981` |
| `logs/preflight-evidence.json` | `b10254c13f77a2f4bebcbcfe61158d105ff86ddc5a8977a237a4e0ff633b4350` |
| `logs/capabilities.json` | `b3c494e7d14ee971538b6aaec39c7f338dfef0705abf50f4bec15eafbe550c3b` |
| `logs/resume-policy.json` | `119799a2766fd11930845d8dfec8220508e5c56372beb18f6b301f1acc0874c1` |
| `logs/uid-lineage.json` | `03e65ca473cb977dc499085832d2b1f782185c4e8db241ac70d3252bfc51d079` |
| `negative/logs/negative-resolution.json` | `889124d26266703eac015b07c0d98b768d323629759b4c2d4e925d2b5dfc61c3` |

Verification after current-head acceptance:

- GitHub CI #109 on `5e9b52c...`: **97 passed in 15.36s**
- separate remote Core-only suite with no Genome-web checkout mounted: **72 passed in 30.53s**
- production Genome-web checksum baseline: unchanged after acceptance

## 9. Scope Limits

This record does **not** claim:

- generic async polling, cancellation, exactly-once submission, Slurm/SSH/Kubernetes execution, or WES/TES compliance;
- execution of EXEC-02 through EXEC-05, EXEC-07, cache/reuse scenarios, or the remaining acceptance catalog;
- scientific correctness of unrelated RNA-seq/GO contracts;
- production publication or canonical promotion;
- full validation of every acceptance criterion in the broader P0 vertical-slice design.

Only the five scenarios explicitly recorded above move from `NOT_RUN`.
