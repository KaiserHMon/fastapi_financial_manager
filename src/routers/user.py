from fastapi import APIRouter, Depends, Security
from models.user_model import UserModel
from schemas.user_schema import UserIn, UserOut
from exceptions.http_errors import USER_CREATION_FAILED, USER_ALREADY_EXISTS, USER_NOT_FOUND

from passlib.context import CryptContext
