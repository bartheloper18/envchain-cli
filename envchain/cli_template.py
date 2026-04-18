"""CLI commands for template rendering with vault variables."""

import click
from envchain.vault import load_vault
from envchain.crypto import derive_key, generate_salt
from envchain.template import render_template, find_placeholders, render_file


@click.command("render")
@click.argument("vault_name")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
@click.option("--strict", is_flag=True, help="Fail on missing variables")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def render_cmd(vault_name: str, template_file: str, output, strict: bool, password: str) -> None:
    """Render a template file using variables from a vault."""
    try:
        vault = load_vault(vault_name, password)
    except Exception as e:
        raise click.ClickException(str(e))

    try:
        if output:
            render_file(template_file, output, vault, strict=strict)
            click.echo(f"Rendered to {output}")
        else:
            with open(template_file, "r") as f:
                content = f.read()
            click.echo(render_template(content, vault, strict=strict), nl=False)
    except KeyError as e:
        raise click.ClickException(str(e))


@click.command("placeholders")
@click.argument("template_file", type=click.Path(exists=True))
def placeholders_cmd(template_file: str) -> None:
    """List all variable placeholders found in a template file."""
    with open(template_file, "r") as f:
        content = f.read()
    names = find_placeholders(content)
    if not names:
        click.echo("No placeholders found.")
    else:
        for name in names:
            click.echo(name)
