from tests.fakes.providers import FakePolicyEvaluator, FakeWorkflowExecutor


def test_fake_executor_declares_no_unearned_guarantees():
    caps = FakeWorkflowExecutor().capabilities()
    assert caps.native_idempotency_key is False
    assert caps.durable_external_execution_id is False
    assert caps.poll is False


def test_policy_is_action_scoped():
    policy = FakePolicyEvaluator(denied_actions={"publish"})
    assert policy.evaluate("alice", "launch", "runspec:1", {}).outcome.value == "ALLOW"
    assert policy.evaluate("alice", "publish", "artifact:1", {}).outcome.value == "DENY"
