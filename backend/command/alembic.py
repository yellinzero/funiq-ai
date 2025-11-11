import os

from alembic import command
from alembic.config import Config
from typer import Typer

cli = Typer()

config = Config(os.path.join(os.getcwd(), "alembic.ini"))


@cli.command()
def init():
    """Initialize alembic migrations directory"""
    command.init(config, os.path.join(os.getcwd(), "migrations"))


@cli.command()
def migrate(message: str):
    """Generate a new migration with automatic changes detection"""
    command.revision(config, message=message, autogenerate=True)


@cli.command()
def upgrade(revision: str = "head"):
    """Upgrade database to a later version"""
    command.upgrade(config, revision)


@cli.command()
def downgrade(revision: str = "-1"):
    """Revert database to a previous version"""
    command.downgrade(config, revision)


@cli.command()
def current():
    """Display current database migration version"""
    command.current(config)
