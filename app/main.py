from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import Base, engine, Item
from app.crud import get_items, create_item
from app.models import SessionLocal
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthCredentials, SimpleUser, AuthenticationBackend
from jinja2 import Environment, FileSystemLoader
from contextlib import asynccontextmanager
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
import os
import time
import random
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
import structlog

class SimpleAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        # Example: Always authenticate as "user"
        return AuthCredentials(["authenticated"]), SimpleUser("user")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    templates.env.cache.clear()
    yield
    # Shutdown logic (if needed, add here)
app = FastAPI(lifespan=lifespan)

# Load environment variables from .env file
load_dotenv()

# Update middleware to use SECRET_KEY from environment variables
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# Update database URL to use environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Set up Jinja2 templates with caching disabled
templates = Jinja2Templates(directory="app/templates")
templates.env = Environment(loader=FileSystemLoader("app/templates"), auto_reload=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a Prometheus Counter metric
REQUEST_COUNT = Counter("app_requests_total", "Total number of requests", ["method", "endpoint"])

# Middleware to count requests
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    return response

# Define logger using structlog
logger = structlog.get_logger()

# Middleware to log incoming requests and outgoing responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("request_received", method=request.method, path=request.url.path)
    response = await call_next(request)
    logger.info("response_sent", status_code=response.status_code)
    return response

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    items = get_items(db)
    return templates.TemplateResponse("home.html", {"request": request, "items": items})

@app.get("/add-item", response_class=HTMLResponse)
async def add_item_page(request: Request):
    return templates.TemplateResponse("add_item.html", {"request": request})

@app.get("/edit-item/{item_id}", response_class=HTMLResponse)
async def edit_item_page(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    return templates.TemplateResponse("edit_item.html", {"request": request, "item": item})

@app.post("/edit-item/{item_id}")
async def edit_item(item_id: int, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    item.name = name
    item.description = description
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/items/")
async def read_items(db: Session = Depends(get_db)):
    return get_items(db)

@app.post("/items/")
async def add_item(name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    create_item(db, name, description)
    return RedirectResponse(url="/", status_code=303)

@app.get("/items-json")
async def get_items_json(db: Session = Depends(get_db)):
    return get_items(db)

# Health Check Endpoints
@app.get("/healthz")
async def healthz():
    """Liveness probe to check if the app is running."""
    return {"status": "ok"}

@app.get("/readyz")
async def readyz():
    """Readiness probe to check if the app is ready to serve traffic."""
    # Add any necessary checks here (e.g., database connection, external services)
    return {"status": "ready"}

# CPU & Memory Load Generator
@app.get("/load")
async def load():
    """Simulate CPU and memory stress."""
    result = 0
    for _ in range(10**7):
        result += random.randint(1, 100)
    return {"status": "load generated", "result": result}

# Crash Simulation
@app.get("/crash")
async def crash():
    """Simulate application crash."""
    raise RuntimeError("Simulated application crash")

# Slow Response Simulation
@app.get("/slow")
async def slow(delay: int = 5):
    """Simulate a slow response with configurable delay."""
    time.sleep(delay)
    return {"status": "response delayed", "delay": delay}

# Random Failures
@app.get("/random-failure")
async def random_failure():
    """Simulate random failures with a 50% chance."""
    if random.random() < 0.5:
        raise RuntimeError("Simulated random failure")
    return {"status": "success"}

# Metrics Endpoint
@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
