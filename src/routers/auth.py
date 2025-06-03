from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, SecurityScopes
from models.user_model import UserModel
from schemas.user_schema import UserIn, UserOut

from datetime import datetime, timedelta
from typing import Annotated
from dotenv import load_dotenv
import os

from jose import JWTError, jwt
from passlib.context import CryptContext

