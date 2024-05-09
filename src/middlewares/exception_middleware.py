from fastapi import Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from starlette.middleware.base import BaseHTTPMiddleware


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as http_exception:
            response = {"type": "http_error", "msg": str(http_exception.detail)}
            return JSONResponse(
                status_code=http_exception.status_code,
                content={"detail": response},
            )
        except ValidationError as exc:
            response = [{"type": x["type"], "msg": x["msg"], "loc": x["loc"]} for x in exc.errors()][0]
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({"detail": response}),
            )
        except ValueError as exc:
            response = {"type": "value_error", "msg": str(exc)}
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": response},
            )
        except Exception as exc:
            response = {"type": "internal_error", "msg": str(exc)}
            return JSONResponse(
                status_code=500,
                content={"detail": response},
            )
