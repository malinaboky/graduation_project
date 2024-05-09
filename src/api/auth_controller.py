from fastapi import APIRouter, Request

from src.api.dependencies import templates

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/login")
async def get_login_form(request: Request):
    return templates.TemplateResponse(request=request, name="auth/login-page.html")


@router.get("/register")
async def get_register_form(request: Request):
    return templates.TemplateResponse(request=request, name="auth/register-page.html")
