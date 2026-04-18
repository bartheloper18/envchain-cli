"""CLI commands for searching environment variables across vaults."""

from __future__ import annotations

import click

from envchain.search import format_results, search_all_vaults, search_vars
from envchain.vault import _get_vault_path


@click.command("search")
@click.argument("pattern")
@click.option("--vault", "-v", default=None, help="Limit search to a specific vault.")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password.")
@click.option("--keys-only", is_flag=True, default=False, help="Match keys only, hide values.")
@click.option("--vaults", multiple=True, help="List of vault names to search (ignored if --vault given).")
def search_cmd(pattern: str, vault: str | None, password: str, keys_only: bool, vaults: tuple) -> None:
    """Search for PATTERN in vault variable keys and values."""
    try:
        if vault:
            results = search_vars(vault, password, pattern, keys_only)
        else:
            if not vaults:
                raise click.UsageError("Provide --vault or one or more --vaults.")
            results = search_all_vaults(list(vaults), password, pattern, keys_only)

        output = format_results(results, show_values=not keys_only)
        click.echo(output)
    except click.UsageError:
        raise
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
