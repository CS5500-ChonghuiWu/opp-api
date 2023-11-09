from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, constr
from starlette import status
from schemas import UserCreate, UserOut, UserLogin, Token

from models.models import Users
from passlib.context import CryptContext
from db.database import SessionLocal
from typing import Annotated, Any
from sqlalchemy.orm import Session
from jose import jwt, JWTError

router = APIRouter(prefix='/auth', tags=['auth'])

import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# These are used to create the signature for a JWT
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class UserSignup(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    email: EmailStr
    business_name: str

class UserOut(BaseModel):
    user_id: int
    username: str
    business_name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    surname: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # check if the user already exists
    existing_user = db.query(Users).filter(
        (Users.username == create_user_request.username) | 
        (Users.email == create_user_request.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists."
        )
    
    hashed_password = bcrypt_context.hash(create_user_request.password)

    # create new user
    new_user = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_password=hashed_password,
        is_active=True,
        role=create_user_request.role,
        # added business_name
        business_name=create_user_request.business_name if hasattr(create_user_request, 'business_name') else None
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # return user info
    return {
        "user_id": new_user.id,
        "username": new_user.username,
        "business_name": new_user.business_name
    }


@router.post("/token/", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    # Authenticate the user
    # TODO: check if form_data is validated by FastAPI
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')

    # Create token from the authenticated user
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))

    return {'access_token': token, 'token_type': 'bearer'}


def authenticate_user(username: str, password: str, db: db_dependency) -> Any:
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    claims = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta
    claims.update({'exp': expires})
    token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
