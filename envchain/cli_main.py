"""Main CLI entry point aggregating all command groups."""

import click
from envchain.cli import cli, new_vault, set_var, get_var, list_all
from envchain.cli_lock import unlock_cmd, lock_cmd, status_cmd
from envchain.cli_rotate import rotate_cmd, verify_cmd


@click.group()
def main():
    """envchain — manage and inject environment variables from encrypted vaults."""
    pass


# Vault management
main.add_command(new_vault, name="new")
main.add_command(set_var, name="set")
main.add_command(get_var, name="get")
main.add_command(list_all, name="list")

# Lock management
main.add_command(unlock_cmd, name="unlock")
main.add_command(lock_cmd, name="lock")
main.add_command(status_cmd, name="status")

# Password rotation
main.add_command(rotate_cmd, name="rotate")
main.add_command(verify_cmd, name="verify")


if __name__ == "__main__":
    main()
