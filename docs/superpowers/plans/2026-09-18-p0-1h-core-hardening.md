# P0.1H Core Hardening Implementation Plan

Execution status: **COMPLETED ON IMPLEMENTATION BRANCH; MERGE REVIEW PENDING**

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Close the execution/recovery invariants that are still weaker in the merged P0 Core than in the authoritative BioHarness contracts, before implementing the Genome-web reference adapter.

**Architecture:** Keep the existing provider-agnostic modular-monolith and ports/adapters design. Harden only the generic control-plane seams required by the already-documented P0 semantics: one unresolved/active external launch per RunSpec, crash-recoverable execution evidence, authorization durability before protected provider access, explicit execution materialization, and non-cherry-pickable validation. Do not add Genome-web logic to Core.

**Tech Stack:** Python 3.12+, Pydantic, SQLAlchemy/PostgreSQL, pytest, existing BioHarness ports/adapters.

**Spec:** `docs/superpowers/specs/2026-09-18-p0-runtime-kernel-design.md`

## Global Constraints

- Work only on `fix/p0-1h-core-hardening` until review.
- No Genome-web scripts, schemas, or biological validation logic enter `src/bioharness`.
- No new workflow engine, queue, daemon, graph DB, or distributed lock.
- Preserve provider-agnostic Core tests without a Genome-web checkout.
- Every behavior change follows RED -> GREEN -> full relevant regression.
- One task per commit; do not batch unrelated fixes.
- Do not start the Genome-web reference-adapter implementation until this plan's completion gate passes.

---

### Task 1: Enforce One Active or Unresolved Attempt per RunSpec

**Files:**
- Modify: `src/bioharness/adapters/postgres/repositories.py`
- Modify: `src/bioharness/application/execute_run.py` only if needed for consistent error translation
- Modify: `tests/integration/test_attempt_allocation.py`
- Modify: `tests/contract/test_reconciliation.py` only if needed

**Invariant:** A new external launch must not be allocated while a prior attempt for the same RunSpec is in `SUBMITTING`, `RUNNING`, `COLLECTING`, `UNKNOWN`, or `NEEDS_OPERATOR_RECONCILIATION`. Terminal `FINISHED` or `FAILED` attempts do not block a legitimate later attempt.

- [x] Write a regression test proving a prior `SUBMITTING` attempt blocks a second allocation.
- [x] Run the focused test and verify RED for the intended reason.
- [x] Add `RUNNING` and `COLLECTING` coverage without widening scope.
- [x] Block all active/unresolved states in `ExecutionService` before preflight while retaining the repository row-lock check as the final transactional guard.
- [x] Implement the minimal transactional check under the existing RunSpec row lock.
- [x] Run focused allocation/reconciliation tests and verify GREEN.
- [x] Run the full Core suite.
- [x] Commit only Task 1.

---

### Task 2: Persist Crash-Recovery Execution Evidence and Reconcile Without a DB Binding

**Files:**
- Modify: `src/bioharness/ports/workflow_executor.py`
- Create or modify: a focused generic execution-evidence record helper under `src/bioharness/adapters/local_process/`
- Modify: `src/bioharness/adapters/local_process/runner.py`
- Modify: `src/bioharness/application/reconcile_run.py`
- Modify: `tests/contract/test_reconciliation.py`
- Modify: `tests/unit/test_local_process.py`

**Invariant:** If the control process dies after the external process may have started but before `ExecutionBinding` is durably stored, reconciliation must still be able to inspect attempt-scoped evidence; absence of sufficient evidence remains `NEEDS_OPERATOR_RECONCILIATION`, never blind resubmission.

- [x] Write RED tests for reconciliation of an attempt with `binding=None` but attempt-scoped execution evidence present.
- [x] Write RED test for no binding + insufficient evidence -> `NEEDS_OPERATOR_RECONCILIATION`.
- [x] Introduce the smallest generic evidence contract required to support this path.
- [x] Make local process launch persist attempt-scoped process evidence before returning control.
- [x] Verify that failure to persist recovery evidence after process creation is classified as ambiguous/UNKNOWN rather than a definite no-spawn failure.
- [x] Update reconciliation to call executor inspection even when no DB binding exists.
- [x] Verify focused tests, then full Core suite.
- [x] Commit only Task 2.

---

### Task 3: Make Protected Resolution Authorization Durable Before Provider Access

**Files:**
- Modify: `src/bioharness/application/resolve_task.py`
- Modify: `tests/contract/test_planning_service.py` or add a focused resolution contract test
- Modify fakes only as required for observation ordering

**Invariant:** For protected resolution, the ALLOW/ALLOW_WITH_WARNING PolicyDecision is committed before `DataProvider.resolve()` is invoked. A provider failure does not erase the historical fact that access was authorized; DENY/REQUIRE_APPROVAL still performs no provider read.

- [x] Write a test that records call order and fails because provider resolution currently occurs before durable decision commit.
- [x] Verify RED.
- [x] Move only the decision persistence boundary; do not change provider semantics.
- [x] Add provider-failure coverage proving the decision remains durable.
- [x] Run focused tests and full Core suite.
- [x] Commit only Task 3.

---

### Task 4: Introduce an Explicit Execution Materialization Contract

**Files:**
- Modify: `src/bioharness/ports/workflow_executor.py`
- Create: `src/bioharness/application/materialize_execution.py` or an equivalently focused module
- Modify: `src/bioharness/application/execute_run.py`
- Modify: planning/repository reads only as required
- Modify: `tests/contract/test_execution_intent.py`
- Modify: `tests/integration/test_p0_vertical_slice.py`

**Invariant:** A WorkflowExecutor receives an explicit provider-agnostic execution descriptor containing the frozen workflow identity, resolved input identities, result-affecting parameters, environment/reproducibility contracts, resource controls, and attempt identity. It must not query BioHarness repositories itself, and Core must not require provider-specific fields.

- [x] Write a RED contract test expressing the descriptor that a real adapter needs.
- [x] Verify RED.
- [x] Add the minimal immutable descriptor type.
- [x] Materialize it from existing RunSpec + ResolvedConfiguration + ResolvedDataRefs + RunAttempt.
- [x] Change `WorkflowExecutor.prepare` to consume the descriptor plus attempt context, updating fakes/tests minimally.
- [x] Verify focused tests and full Core suite.
- [x] Commit only Task 4.

---

### Task 5: Make Validation Evaluation Conflict-Safe

**Files:**
- Modify: `src/bioharness/domain/validation.py` only if the contract needs an explicit error/type
- Modify: `src/bioharness/application/validate_run.py`
- Modify: `tests/contract/test_validation.py`

**Invariant:** For the current P0 profile model, each required validation kind is satisfied by exactly one supplied report for the common evaluation subject. Duplicate reports of a required kind are rejected instead of allowing one PASS to mask another FAIL. PASS/PASS_WITH_LIMITATIONS reports used to open a gate must carry evidence.

- [x] Write RED test for PASS + FAIL of the same required kind being rejected.
- [x] Write RED test for gate-opening PASS report without evidence being rejected.
- [x] Implement the minimal exact-one-per-kind/evidence rule.
- [x] Preserve historical profile revision semantics.
- [x] Recheck evidence at gate time so a legacy/directly stored positive report without evidence cannot open the gate.
- [x] Run focused validation tests and full Core suite.
- [x] Commit only Task 5.

---

### Task 6: Re-Audit Documentation and the Genome-web Reference Plan Against the Hardened Ports

**Files:**
- Modify only relevant status/source-audit/reference-plan docs.
- Do not implement the Genome-web adapter in this task.

**Goals:**
- P0 Core status reflects actual implemented/tested scope.
- Advanced memory/reference integration/live acceptance remain explicitly unimplemented/not run.
- Source-audit inspected-file list includes the Genome-web bundle/summary/verifier/integration-test evidence actually used.
- The reference-integration plan consumes the real hardened Core interfaces, especially execution materialization and attempt-scoped reconciliation evidence.

- [x] Compare final Core ports to `2026-09-18-genome-web-tf-reference-integration.md`.
- [x] Remove stale assumptions such as provider-specific context fields that Core does not supply.
- [x] Update status language without marking live Genome-web scenarios PASS.
- [x] Run documentation/code consistency searches and full Core CI.
- [x] Commit only Task 6.

---

## Completion Gate

P0.1H is complete only when:

1. no second active external attempt can be allocated for a RunSpec with a non-terminal/unresolved prior attempt;
2. an attempt with missing DB binding can be reconciled from attempt-scoped evidence or safely stops at operator reconciliation;
3. protected provider resolution is preceded by a durably recorded current authorization decision;
4. WorkflowExecutor invocation receives explicit frozen execution material rather than relying on provider-specific repository lookups;
5. validation cannot cherry-pick one PASS among conflicting duplicate reports;
6. Core tests pass without Genome-web checked out;
7. the Genome-web reference plan matches the actual Core port signatures;
8. no Genome-web live scenario is marked PASS without fresh executable evidence.
