import json
from typing import Any

import typer

app = typer.Typer(help="BioHarness research control plane; runtime composition is supplied by deployment/reference integration")
task_app = typer.Typer(help="Scientific task operations")
run_app = typer.Typer(help="Run attempt operations")
artifact_app = typer.Typer(help="Artifact inspection operations")
memory_app = typer.Typer(help="Research memory operations")
app.add_typer(task_app, name="task")
app.add_typer(run_app, name="run")
app.add_typer(artifact_app, name="artifact")
app.add_typer(memory_app, name="memory")


class RuntimeNotConfigured(RuntimeError):
    pass


def _runtime(ctx: typer.Context):
    if ctx.obj is None:
        raise RuntimeNotConfigured(
            "No BioHarness runtime composition is attached to this CLI invocation"
        )
    return ctx.obj


def _emit(value: Any) -> None:
    typer.echo(json.dumps(value, default=str, sort_keys=True))


@task_app.command("create")
def task_create(
    ctx: typer.Context,
    question: str = typer.Option(..., "--question"),
    inference: str = typer.Option(..., "--inference"),
    analysis_class: str = typer.Option(..., "--analysis-class"),
    resource: list[str] | None = typer.Option(None, "--resource"),
    output_intent: str = typer.Option("candidate", "--output-intent"),
):
    payload = {
        "question": question,
        "requested_inference": inference,
        "analysis_class": analysis_class,
        "resources": tuple(resource or ()),
        "output_intent": output_intent,
    }
    _emit(_runtime(ctx).task_create(payload))


@task_app.command("show")
def task_show(ctx: typer.Context, task_id: str):
    _emit(_runtime(ctx).task_show(task_id))


@app.command("plan")
def plan(ctx: typer.Context, task_id: str):
    _emit(_runtime(ctx).plan(task_id))


@run_app.command("start")
def run_start(ctx: typer.Context, run_spec_id: str, actor: str = typer.Option(..., "--actor")):
    _emit(_runtime(ctx).run_start(run_spec_id, actor))


@run_app.command("show")
def run_show(ctx: typer.Context, attempt_id: str):
    _emit(_runtime(ctx).run_show(attempt_id))


@run_app.command("reconcile")
def run_reconcile(ctx: typer.Context, attempt_id: str, actor: str = typer.Option(..., "--actor")):
    _emit(_runtime(ctx).run_reconcile(attempt_id, actor))


@artifact_app.command("list")
def artifact_list(ctx: typer.Context, attempt_id: str):
    _emit(_runtime(ctx).artifact_list(attempt_id))


@app.command("validate")
def validate(ctx: typer.Context, attempt_id: str):
    _emit(_runtime(ctx).validate(attempt_id))


@memory_app.command("list")
def memory_list(
    ctx: typer.Context,
    scope: str = typer.Option(..., "--scope"),
    tag: list[str] | None = typer.Option(None, "--tag"),
):
    _emit(_runtime(ctx).memory_list(scope, tuple(tag or ())))
