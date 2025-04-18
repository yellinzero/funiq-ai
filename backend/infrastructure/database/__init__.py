import importlib
import pkgutil

from .core import (
    create_transient_session,
    get_engine,
    get_session,
    get_sync_engine,
    init_database,
    shutdown_database,
    update_database_schema,
    with_session,
)
from .models import (
    # Mixins
    DBAuditFieldsMixin,
    # Base classes
    DBBase,
    DBBaseModelMixin,
    DBIntegerModelMixin,
    DBSoftDeleteMixin,
    DBUUIDModelMixin,
    # Utility functions
    resolve_table_name,
)


# Dynamic model loading
def load_models(package_name: str) -> None:
    """
    Dynamically import all submodules of a package to ensure models are registered.
    :param package_name: The package containing the models (e.g., 'my_app.models').
    """

    package = importlib.import_module(package_name)
    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        importlib.import_module(module_name)


__all__ = [
    "DBAuditFieldsMixin",
    "DBBase",
    "DBBaseModelMixin",
    "DBIntegerModelMixin",
    "DBSoftDeleteMixin",
    "DBUUIDModelMixin",
    "create_transient_session",
    "get_engine",
    "get_session",
    "get_sync_engine",
    "init_database",
    "load_models",
    "resolve_table_name",
    "shutdown_database",
    "update_database_schema",
    "with_session",
]
