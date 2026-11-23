from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from config import APP_ENV, SECRET_KEY
import templates


APP_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=APP_DIR / "templates")

APP_DIR = Path(__file__).resolve().parent

app = FastAPI(title="3D Fáil API")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    same_site="lax",
    https_only=False,
    max_age=60 * 60 * 8,
)

app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    contexto = {
        "ambiente": APP_ENV,
    }
    return templates.TemplateResponse(request, "home.html", contexto)