"""Main CLI entry point for envchain."""

import click
from envchain.cli import cli
from envchain.cli_lock import unlock_cmd, lock_cmd, status_cmd
from envchain.cli_rotate import rotate_cmd, verify_cmd
from envchain.cli_search import search_cmd
from envchain.cli_backup import backup_cmd, restore_cmd, list_backups_cmd
from envchain.cli_ttl import set_ttl_cmd, remove_ttl_cmd, ttl_status_cmd, purge_expired_cmd
from envchain.cli_template import render_cmd, placeholders_cmd
from envchain.cli_hooks import hook_add_cmd, hook_remove_cmd, hook_list_cmd, hook_run_cmd
from envchain.cli_profile import profile_cmd
from envchain.cli_snapshot import snapshot_create_cmd, snapshot_restore_cmd, snapshot_list_cmd
from envchain.cli_diff import diff_cmd
from envchain.cli_policy import policy_cmd


cli.add_command(unlock_cmd, name="unlock")
cli.add_command(lock_cmd, name="lock")
cli.add_command(status_cmd, name="status")
cli.add_command(rotate_cmd, name="rotate")
cli.add_command(verify_cmd, name="verify")
cli.add_command(search_cmd, name="search")
cli.add_command(backup_cmd, name="backup")
cli.add_command(restore_cmd, name="restore")
cli.add_command(list_backups_cmd, name="list-backups")
cli.add_command(set_ttl_cmd, name="set-ttl")
cli.add_command(remove_ttl_cmd, name="remove-ttl")
cli.add_command(ttl_status_cmd, name="ttl-status")
cli.add_command(purge_expired_cmd, name="purge-expired")
cli.add_command(render_cmd, name="render")
cli.add_command(placeholders_cmd, name="placeholders")
cli.add_command(hook_add_cmd, name="hook-add")
cli.add_command(hook_remove_cmd, name="hook-remove")
cli.add_command(hook_list_cmd, name="hook-list")
cli.add_command(hook_run_cmd, name="hook-run")
cli.add_command(profile_cmd, name="profile")
cli.add_command(snapshot_create_cmd, name="snapshot-create")
cli.add_command(snapshot_restore_cmd, name="snapshot-restore")
cli.add_command(snapshot_list_cmd, name="snapshot-list")
cli.add_command(diff_cmd, name="diff")
cli.add_command(policy_cmd, name="policy")


def main():
    cli()


if __name__ == "__main__":
    main()
