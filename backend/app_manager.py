from __future__ import annotations

import dataclasses
from typing import Any, ClassVar

from fastapi import APIRouter, Depends, FastAPI

from utils.jwt_bearer import JWTBearer
from utils.singleton import Singleton


class AppManager(metaclass=Singleton):
    """
    AppManager manages the lifecycle of all application modules.
    """

    def __init__(self):
        self.apps: dict[str, FuniqAIApp] = {}

    def install_app(self, app: FuniqAIApp):
        """
        Install a single application module.
        """
        if app.name in self.apps:
            raise ValueError(f"App {app.name} already installed")
        self.apps[app.name] = app

    def install_apps(self, app_paths: list[str]):
        """
        Install multiple application modules dynamically.
        """
        for app_path in app_paths:
            __import__(f"{app_path}.app")

    def apply_modules_to_fastapi(self, funiq_ai_app: FastAPI):
        """
        Apply all installed modules to the provided FastAPI application, 
        including their routes and middlewares.

        :param funiq_ai_app: The FastAPI instance where modules will be applied.
        """
        # Add each app's router to the FastAPI instance
        
        for app in self.apps.values():
            funiq_ai_app.include_router(app.router)

        # Add middlewares from all installed apps
        for app in self.apps.values():
            for middleware_class, options in app.middlewares:
                funiq_ai_app.add_middleware(middleware_class, **options)

    def list_installed_apps(self) -> list[str]:
        """
        List the names of all installed applications.
        """
        return list(self.apps.keys())


app_manager = AppManager()


@dataclasses.dataclass(kw_only=True)
class _AppBaseMixin:
    """
    Base mixin for applications. Includes reference to the AppManager.
    """
    name: str
    manager: ClassVar[AppManager] = app_manager
    public: bool = False


@dataclasses.dataclass(kw_only=True)
class _RouterMixin(_AppBaseMixin):
    """
    Mixin for route management in an application.
    Provides a dedicated router for each module.
    """
    router: APIRouter = dataclasses.field(init=False)

    def add_route(self, path: str, endpoint: Any, methods: list[str] = ["GET"], **options):
        """
        Add a route to the module's dedicated router.
        """
        self.router.add_api_route(path, endpoint, methods=methods, **options)

    def _init_router(self):
        """
        Initialize the router with appropriate dependencies.
        """
        self.router = APIRouter(
            dependencies=[] if self.public else [Depends(JWTBearer())]
        )


@dataclasses.dataclass(kw_only=True)
class _MiddlewareMixin(_AppBaseMixin):
    """
    Mixin for middleware management in an application.
    """
    middlewares: list = dataclasses.field(default_factory=list, init=False, repr=False)

    def add_middleware(self, middleware_class: Any, **options: Any):
        """
        Add a middleware to the application.
        """
        self.middlewares.append((middleware_class, options))


@dataclasses.dataclass
class FuniqAIApp(_RouterMixin, _MiddlewareMixin):
    """
    Represents a single application/module with routes and middleware support.
    Automatically registers itself with the AppManager upon initialization.
    """

    def __post_init__(self):
        # Initialize the router
        self._init_router()
        # Automatically register the app with the manager
        self.manager.install_app(self)
