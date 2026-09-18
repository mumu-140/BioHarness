from typer.testing import CliRunner

from bioharness.cli.main import app

runner = CliRunner()


def test_root_help_exposes_p0_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("task", "plan", "run", "artifact", "validate", "memory"):
        assert command in result.stdout


def test_group_help_exposes_expected_subcommands():
    expected = {
        "task": ("create", "show"),
        "run": ("start", "show", "reconcile"),
        "artifact": ("list",),
        "memory": ("list",),
    }
    for group, commands in expected.items():
        result = runner.invoke(app, [group, "--help"])
        assert result.exit_code == 0
        for command in commands:
            assert command in result.stdout


def test_command_delegates_to_injected_runtime():
    calls=[]

    class Runtime:
        def task_show(self, task_id):
            calls.append(("task_show", task_id))
            return {"id": task_id, "revision": 1}

    result=runner.invoke(app, ["task", "show", "task-1"], obj=Runtime())
    assert result.exit_code == 0
    assert calls == [("task_show", "task-1")]
    assert '"revision": 1' in result.stdout
