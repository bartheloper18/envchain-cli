"""CLI commands for vault diffing."""

from __future__ import annotations

import click

from envchain.diff import diff_vaults, format_diff
from envchain.vault import load_vault


@click.command("diff")
@click.argument("vault_a")
@click.argument("vault_b")
@click.password_option(
    "--password-a",
    prompt="Password for vault A",
    confirmation_prompt=False,
    help="Master password for vault A.",
)
@click.password_option(
    "--password-b",
    prompt="Password for vault B",
    confirmation_prompt=False,
    help="Master password for vault B (defaults to password A if omitted).",
)
@click.option(
    "--show-values",
    is_flag=True,
    default=False,
    help="Display actual variable values in the diff output.",
)
def diff_cmd(
    vault_a: str,
    vault_b: str,
    password_a: str,
    password_b: str,
    show_values: bool,
) -> None:
    """Show differences between two vaults.

    VAULT_A is the baseline; VAULT_B is compared against it.
    """
    try:
        data_a = load_vault(vault_a, password_a)
    except FileNotFoundError:
        raise click.ClickException(f"Vault '{vault_a}' not found.")
    except ValueError as exc:
        raise click.ClickException(f"Cannot open vault A: {exc}")

    try:
        data_b = load_vault(vault_b, password_b)
    except FileNotFoundError:
        raise click.ClickException(f"Vault '{vault_b}' not found.")
    except ValueError as exc:
        raise click.ClickException(f"Cannot open vault B: {exc}")

    result = diff_vaults(data_a, data_b, show_values=show_values)
    output = format_diff(result, show_values=show_values)
    click.echo(output)

    if result.has_changes:
        summary = (
            f"+{len(result.added)} added  "
            f"-{len(result.removed)} removed  "
            f"~{len(result.changed)} changed  "
            f"={len(result.unchanged)} unchanged"
        )
        click.echo(f"\n{summary}")
