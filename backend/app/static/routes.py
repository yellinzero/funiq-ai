import os

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from app.errors.common import CommonErrorCode

static_router = APIRouter(prefix="/static", tags=["Static"])


@static_router.get("/providers/{provider}/icon/{size}")
async def get_provider_icon(request: Request, provider: str, size: str):
    """
    Get the icon for a specific provider

    Args:
        provider: The provider name
        size: Icon size ('small' or 'large')
    """
    icon_filename = f"icon_{size}.svg"

    # Build the icon file path
    icon_path = os.path.join(
        "/app",  # according to Dockerfile working directory
        "providers",
        "models",
        provider,
        "_assets",
        icon_filename,
    )

    if not os.path.exists(icon_path):
        raise CommonErrorCode.FILE_NOT_FOUND.exception(status_code=404, data={"path": icon_path})

    return FileResponse(icon_path, media_type="image/svg+xml")
