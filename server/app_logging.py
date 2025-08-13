import logging
import sys
import traceback
from typing import Callable
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse


def setup_logging(level: int = logging.DEBUG) -> None:
    """Configure root logging with a verbose format suitable for debugging.
    This also bumps uvicorn and fastapi loggers to the same level.
    """
    fmt = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Align common servers' loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging.getLogger(name).setLevel(level)


def install_observability(app: FastAPI) -> None:
    """Install request logging middleware and error handlers."""
    logger = logging.getLogger("app")

    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):
        logger.debug(
            "request start: %s %s - headers=%s",
            request.method,
            request.url.path,
            dict(request.headers),
        )
        try:
            response = await call_next(request)
        except Exception:
            # Error here will be caught by exception handlers too, but we log early context
            logger.exception("unhandled exception during request: %s %s", request.method, request.url.path)
            raise
        logger.debug(
            "request end: %s %s -> %s",
            request.method,
            request.url.path,
            getattr(response, "status_code", "<no status>"),
        )
        return response

    @app.exception_handler(Exception)
    async def catch_all_exceptions(request: Request, exc: Exception):
        logger.exception(
            "uncaught exception: %s %s -> %s\n%s",
            request.method,
            request.url.path,
            exc.__class__.__name__,
            "".join(traceback.format_exception(exc)),
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": exc.__class__.__name__,
            },
        )

    from fastapi.exceptions import HTTPException

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Add guidance for common 404 cause (trailing slash mismatch)
        hint = None
        if exc.status_code == 404:
            path = request.url.path
            if path.endswith("/"):
                hint = "Remove trailing slash and try again (route defined without trailing slash)."
            else:
                hint = "If you tried with trailing slash too, check /_routes for available endpoints."
        logger.warning(
            "HTTPException: %s %s -> %s detail=%s hint=%s",
            request.method,
            request.url.path,
            exc.status_code,
            getattr(exc, "detail", None),
            hint,
        )
        payload = {"detail": exc.detail}
        if hint:
            payload["hint"] = hint
        return JSONResponse(status_code=exc.status_code, content=payload)


def log_registered_routes(app: FastAPI) -> None:
    logger = logging.getLogger("app")
    try:
        routes_info = []
        for r in app.router.routes:
            path = getattr(r, "path", "<unknown>")
            methods = sorted(getattr(r, "methods", set()))
            routes_info.append({"path": path, "methods": methods})
        logger.info("registered routes: %s", routes_info)
    except Exception:
        logger.exception("failed to list routes")
