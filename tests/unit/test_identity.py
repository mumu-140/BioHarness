from bioharness.identity.canonical import sha256_canonical
from bioharness.identity.projections import analysis_projection, run_spec_projection


def test_mapping_order_does_not_change_hash():
    assert sha256_canonical({"b": 2, "a": 1}) == sha256_canonical({"a": 1, "b": 2})


def test_validation_profile_changes_run_spec_not_analysis_identity():
    analysis = analysis_projection(
        task_semantics={"inference": "phylogeny"},
        input_identities=({"sha256": "a" * 64},),
        workflow_identity={"provider": "fake", "revision": "r1"},
        result_affecting_parameters={"seed": 7},
        environment_contract={"python": "3.12"},
        reproducibility={"class": "SEEDED_STOCHASTIC", "seed": 7},
    )
    run_a = run_spec_projection(analysis, {"id": "candidate", "revision": "1"}, {"project": "p1"})
    run_b = run_spec_projection(analysis, {"id": "candidate", "revision": "2"}, {"project": "p1"})
    assert sha256_canonical(run_a) != sha256_canonical(run_b)
    assert sha256_canonical(analysis) == sha256_canonical(analysis)
