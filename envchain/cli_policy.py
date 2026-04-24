"""CLI commands for vault access policy management."""

import click
from envchain.policy import (
    add_rule, remove_rule, is_allowed, load_policy,
    set_default, VALID_ACTIONS
)


@click.group("policy")
def policy_cmd():
    """Manage access policies for a vault."""
    pass


@policy_cmd.command("add")
@click.argument("vault")
@click.argument("action", type=click.Choice(list(VALID_ACTIONS)))
@click.argument("key_pattern")
@click.option("--effect", type=click.Choice(["allow", "deny"]), default="deny", show_default=True)
def policy_add(vault, action, key_pattern, effect):
    """Add an access rule to a vault policy."""
    add_rule(vault, action, key_pattern, effect)
    click.echo(f"Rule added: {effect} {action} on '{key_pattern}' for vault '{vault}'.")


@policy_cmd.command("remove")
@click.argument("vault")
@click.argument("action", type=click.Choice(list(VALID_ACTIONS)))
@click.argument("key_pattern")
def policy_remove(vault, action, key_pattern):
    """Remove an access rule from a vault policy."""
    removed = remove_rule(vault, action, key_pattern)
    if removed:
        click.echo(f"Rule removed for action '{action}' on '{key_pattern}'.")
    else:
        click.echo("No matching rule found.", err=True)


@policy_cmd.command("list")
@click.argument("vault")
def policy_list(vault):
    """List all rules in a vault policy."""
    policy = load_policy(vault)
    click.echo(f"Default: {policy.get('default', 'allow')}")
    rules = policy.get("rules", [])
    if not rules:
        click.echo("No rules defined.")
    for rule in rules:
        click.echo(f"  [{rule['effect'].upper()}] {rule['action']} on '{rule['key_pattern']}'")


@policy_cmd.command("check")
@click.argument("vault")
@click.argument("action", type=click.Choice(list(VALID_ACTIONS)))
@click.argument("key")
def policy_check(vault, action, key):
    """Check if an action on a key is allowed by policy."""
    allowed = is_allowed(vault, action, key)
    status = "ALLOWED" if allowed else "DENIED"
    click.echo(f"{status}: {action} on '{key}' in vault '{vault}'.")


@policy_cmd.command("default")
@click.argument("vault")
@click.argument("effect", type=click.Choice(["allow", "deny"]))
def policy_default(vault, effect):
    """Set the default policy effect for a vault."""
    set_default(vault, effect)
    click.echo(f"Default policy for vault '{vault}' set to '{effect}'.")
