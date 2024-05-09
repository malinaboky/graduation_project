import mimetypes

import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette import status
from fastapi_utilities import repeat_every
from starlette.responses import JSONResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

from src.api.dependencies import job_manager
from src.middlewares.exception_middleware import ExceptionHandlerMiddleware
from src.middlewares.validation_middleware import ValidateContentTypeMiddleware, ValidateContentLenMiddleware
from src.api.routers import all_routers
from src.auth.auth_service import auth_backend, fastapi_users
from src.schemas.user_schema import UserRead, UserCreate


app = FastAPI()
background_tasks = set()
job_manager = job_manager()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
for router in all_routers:
    app.include_router(router)

app.mount("/src/static", StaticFiles(directory="src/static"), name="static")

app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(ValidateContentTypeMiddleware)
app.add_middleware(ValidateContentLenMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = [{"type": x["type"], "msg": x["msg"], "loc": x["loc"]} for x in exc.errors()][0]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": response}),
    )


@app.exception_handler(HTTPException)
def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url='/auth/login')
    response = {"type": "http_error", "msg": str(exc.detail)}
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": response},
    )


@app.on_event('startup')
@repeat_every(seconds=180)
async def run_pipelines():
    await job_manager.check_pipelines(background_tasks)


if __name__ == "__main__":
    uvicorn.run(app="src.main:app", reload=True)
