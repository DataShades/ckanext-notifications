import click


@click.group(short_help="notifications CLI.")
def notifications():
    """notifications CLI.
    """


@notifications.command()
@click.argument("name", default="notifications")
def command(name):
    """Docs.
    """
    click.echo(f"Hello, {name}!")


def get_commands():
    return [notifications]
