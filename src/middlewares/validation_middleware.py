import re

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.middlewares.dependencies import ContentLenChecker, ContentTypeChecker


def get_content_type_from_body(body):
    content_type_match = re.search(rb'Content-Type: ([^\r\n]+)', body)
    content_type = None
    if content_type_match:
        content_type = content_type_match.group(1).decode("utf-8")
    return content_type


class ValidateContentTypeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        content_type = request.headers.get("Content-Type", "")
        file_content_type = ''

        if content_type.startswith("multipart/form-data"):
            bd = await request.body()
            file_content_type = get_content_type_from_body(bd)

        if file_content_type:
            for route in request.app.routes:
                try:
                    for dependency in route.dependant.dependencies:
                        if not isinstance(dependency.cache_key[0], ContentTypeChecker):
                            continue

                        valid_content_type = dependency.call(content_type=file_content_type)

                        if not valid_content_type:
                            exc = HTTPException(
                                detail=f'Invalid file extension {file_content_type}',
                                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
                            return JSONResponse(
                                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                                content={'detail': {'type': 'http_error', "msg": str(exc.detail)}})

                except AttributeError as e:
                    if e.name == 'dependant':
                        pass

        response = await call_next(request)
        return response


class ValidateContentLenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        content_type = request.headers.get("Content-Type", "")
        content_len = request.headers.get("Content-Length", "")
        size = 0

        if content_len and content_type.startswith("multipart/form-data"):
            size = int(content_len)

        if size > 0:
            for route in request.app.routes:
                try:
                    for dependency in route.dependant.dependencies:
                        if not isinstance(dependency.cache_key[0], ContentLenChecker):
                            continue

                        valid_content_len = dependency.call(content_len=size)

                        if not valid_content_len:
                            exc = HTTPException(
                                detail=f'File is too large',
                                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

                            return JSONResponse(
                                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                content={'detail': {'type': 'http_error', "msg": str(exc.detail)}})

                except AttributeError as e:
                    if e.name == 'dependant':
                        pass

        response = await call_next(request)
        return response
