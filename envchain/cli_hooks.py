"""CLI commands for managing vault hooks."""
import click
from envchain.hooks import register_hook, remove_hook, list_hooks, run_hooks, HOOK_EVENTS


@click.command("hook-add")
@click.argument("vault_name")
@click.argument("event")
@click.argument("command")
def hook_add_cmd(vault_name, event, command):
    """Register a shell command to run on a vault event."""
    try:
        register_hook(vault_name, event, command)
        click.echo(f"Hook registered for '{event}' on vault '{vault_name}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@click.command("hook-remove")
@click.argument("vault_name")
@click.argument("event")
@click.argument("command")
def hook_remove_cmd(vault_name, event, command):
    """Remove a registered hook command."""
    removed = remove_hook(vault_name, event, command)
    if removed:
        click.echo(f"Hook removed from '{event}' on vault '{vault_name}'.")
    else:
        click.echo(f"Hook not found.", err=True)
        raise SystemExit(1)


@click.command("hook-list")
@click.argument("vault_name")
def hook_list_cmd(vault_name):
    """List all registered hooks for a vault."""
    hooks = list_hooks(vault_name)
    if not hooks:
        click.echo(f"No hooks registered for '{vault_name}'.")
        return
    for event, cmds in hooks.items():
        for cmd in cmds:
            click.echo(f"{event}: {cmd}")


@click.command("hook-run")
@click.argument("vault_name")
@click.argument("event")
def hook_run_cmd(vault_name, event):
    """Manually trigger hooks for a vault event."""
    results = run_hooks(vault_name, event)
    if not results:
        click.echo("No hooks to run.")
        return
    for r in results:
        status = "OK" if r["returncode"] == 0 else "FAIL"
        click.echo(f"[{status}] {r['command']}")
        if r["stdout"]:
            click.echo(f"  stdout: {r['stdout']}")
        if r["stderr"]:
            click.echo(f"  stderr: {r['stderr']}")
