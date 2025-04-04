import asyncio
import importlib
import importlib.util
import os
import re
from pathlib import Path

import typer

cli = typer.Typer(help="Run utility scripts")

SCRIPT_NAME_ARG = typer.Argument(..., help="Name of the script to run")
SCRIPT_ARGS_ARG = typer.Argument(None, help="Arguments to pass to the script")


@cli.command(context_settings={"ignore_unknown_options": True})
def run(
    script_name: str = SCRIPT_NAME_ARG,
    args: list[str] | None = SCRIPT_ARGS_ARG,
):
    """Run a utility script from the scripts directory."""
    try:
        # First try to import as a module
        try:
            script_module = importlib.import_module(f"scripts.{script_name}")
        except ImportError as e:
            # If module import fails, try to load from file
            script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts"))
            script_path = Path(script_dir) / script_name

            if not script_path.is_file():
                typer.echo(f"Error: Script {script_name} not found in {script_dir}")
                raise typer.Exit(1) from e

            # Validate script name for security
            if not re.match(r"^[\w-]+\.py$", script_name):
                typer.echo(f"Invalid script name: {script_name}")
                raise typer.Exit(1) from e

            # Load the script from file
            module_name = script_name[:-3]  # Remove .py extension
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            script_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(script_module)

        # Execute the script's main function
        if hasattr(script_module, "main"):
            main_func = script_module.main
            if asyncio.iscoroutinefunction(main_func):
                asyncio.run(main_func(args or []))
            else:
                main_func(args or [])
        else:
            typer.echo(f"Error: Script {script_name} has no main() function")
            raise typer.Exit(1)

    except ImportError as e:
        typer.echo(f"Error: Script {script_name} not found")
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error executing script: {e}")
        raise typer.Exit(1) from e
