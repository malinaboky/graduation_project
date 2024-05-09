from src.api.pipeline_controller import router as pipeline_router
from src.api.auth_controller import router as auth_router

all_routers = [
    pipeline_router,
    auth_router
]
