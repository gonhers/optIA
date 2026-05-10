from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .dashboard import get_dashboard_data
from .optimizer import optimize_prompt
from .schemas import AppConfigResponse, DashboardResponse, OptimizeRequest, OptimizeResponse
from .settings import get_llm_runtime_settings
from .translator import LanguageCode

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Prompt Optimizer SaaS", version="0.1.0", openapi_version="3.0.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi() -> dict[str, object]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["openapi"] = "3.0.4"

    components = openapi_schema.setdefault("components", {})
    response_components = components.setdefault("responses", {})
    response_components["UnauthorizedError"] = {
        "description": "Access token is missing or invalid"
    }
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    openapi_schema["security"] = [{"bearerAuth": []}]

    paths = openapi_schema.get("paths", {})
    for path_item in paths.values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            responses = operation.setdefault("responses", {})
            responses["401"] = {"$ref": "#/components/responses/UnauthorizedError"}

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.middleware("http")
async def disable_frontend_cache(request: Request, call_next):
    response = await call_next(request)

    if request.method in {"GET", "HEAD"} and (
        request.url.path == "/" or request.url.path.startswith("/static/")
    ):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
    messages = []
    for error in exc.errors():
        message = error.get("msg", "Invalid request.")
        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")
        messages.append(message)

    detail: str | list[str]
    detail = messages[0] if len(messages) == 1 else messages
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(RuntimeError)
async def runtime_exception_handler(_, exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/app-config", response_model=AppConfigResponse)
def app_config() -> AppConfigResponse:
    settings = get_llm_runtime_settings()
    return AppConfigResponse(
        mode="live" if settings.is_live_mode else "simulation",
        live_ready=settings.is_live_ready,
    )


@app.get("/dashboard", response_model=DashboardResponse)
def dashboard(language: LanguageCode | None = None) -> DashboardResponse:
    return get_dashboard_data(language)


@app.post("/optimize", response_model=OptimizeResponse)
def optimize(payload: OptimizeRequest) -> dict[str, object]:
    return optimize_prompt(payload.prompt, payload.target_language, payload.candidate_count)


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


    @app.get("/", include_in_schema=False)
    def frontend() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")
