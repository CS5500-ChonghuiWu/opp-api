from fastapi import FastAPI

from models import models
from db.database import engine
from routers import auth, todos, admin

# application
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# sets up database defined in engine
models.Base.metadata.create_all(bind=engine)

# Set API endpoints on router
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)

from routers.generics import router as generics_router
app.include_router(generics_router)