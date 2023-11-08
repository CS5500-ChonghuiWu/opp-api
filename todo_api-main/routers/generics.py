
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from models.models import GenericObject
from db.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the database session
db_dependency = Depends(get_db)

# GenericObject Pydantic model to define request and response structure
class GenericObjectRequest(BaseModel):
    name: str
    price: float

# Read All GenericObjects
@router.get("/generics", response_model=List[GenericObjectRequest])
def read_all_generics(db: Session = db_dependency):
    generics = db.query(GenericObject).all()
    return generics

# Read a GenericObject by ID
@router.get("/generics/{id}", response_model=GenericObjectRequest)
def read_generic(id: int, db: Session = db_dependency):
    generic = db.query(GenericObject).filter(GenericObject.id == id).first()
    if generic is None:
        raise HTTPException(status_code=404, detail="GenericObject not found")
    return generic

# Create a new GenericObject
@router.post("/generics", response_model=GenericObjectRequest)
def create_generic(generic_request: GenericObjectRequest, db: Session = db_dependency):
    generic = GenericObject(name=generic_request.name, price=generic_request.price)
    db.add(generic)
    db.commit()
    db.refresh(generic)
    return generic

# Update a GenericObject by ID
@router.put("/generics/{id}", response_model=GenericObjectRequest)
def update_generic(id: int, generic_request: GenericObjectRequest, db: Session = db_dependency):
    generic = db.query(GenericObject).filter(GenericObject.id == id).first()
    if generic is None:
        raise HTTPException(status_code=404, detail="GenericObject not found")
    generic.name = generic_request.name
    generic.price = generic_request.price
    db.commit()
    return generic

# Delete a GenericObject by ID
@router.delete("/generics/{id}", status_code=204)
def delete_generic(id: int, db: Session = db_dependency):
    generic = db.query(GenericObject).filter(GenericObject.id == id).first()
    if generic is None:
        raise HTTPException(status_code=404, detail="GenericObject not found")
    db.delete(generic)
    db.commit()
    return {"ok": True}
