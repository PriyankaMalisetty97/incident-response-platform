"""One place that decides what clients see when something goes wrong inside the server."""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

logger = logging.getLogger("app.errors")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(OperationalError)
    async def db_unavailable(request: Request, exc: OperationalError):
        # Database is down / unreachable: tell the client to retry later.
        logger.error("Database unavailable on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=503,
            content={"detail": "Database is temporarily unavailable. Please try again later."},
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_error(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "A database error occurred."})

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        # Full details go to the log for us; the client only gets a safe, generic message.
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
