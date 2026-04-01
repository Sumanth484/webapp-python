from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
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

app.add_middleware(SessionMiddleware, secret_key="abcdefgh")
app.add_middleware(AuthenticationMiddleware, backend=SimpleAuthBackend())
# Mount static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

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
