from pathlib import Path


FORBIDDEN = (
    "examples.reference_integrations",
    "genome_web",
    "genome-web",
    "deepseek_harness",
    "deepseek-harness",
    "@earendil-works",
)


def test_core_has_no_reference_or_agent_runtime_dependency():
    offenders=[]
    root=Path("src/bioharness")
    for path in root.rglob("*.py"):
        text=path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN:
            if token.lower() in text:
                offenders.append(f"{path}:{token}")
    assert offenders == []
