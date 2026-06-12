import click


@click.group(short_help="notifications CLI.")
def notifications():
    """notifications CLI.
    """
    pass


@notifications.command()
@click.argument("name", default="notifications")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [notifications]
