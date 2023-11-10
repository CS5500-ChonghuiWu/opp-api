from fastapi import FastAPI

from models import models
from db.database import engine
from routers import auth, todos, admin
from routers.payment import router as payment_router
from routers.generics import router as generics_router
import sqlite3



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
app.include_router(generics_router)
app.include_router(payment_router)