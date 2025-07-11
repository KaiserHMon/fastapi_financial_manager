from fastapi import HTTPException, status

# Errores de autenticación (401)
WRONG_PASSWORD = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect password.",
    headers={"WWW-Authenticate": "Bearer"}
)

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"}
)

INVALID_REFRESH_TOKEN = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired refresh token.",
    headers={"WWW-Authenticate": "Bearer"}
)

# Errores de recursos (404)
USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found."
)

# Errores de conflicto (409)
USER_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Username already registered. Use a different username."
)

EMAIL_ALREADY_EXISTS = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Email already registered. Use a different email.")

# Errores de validación (422)
USER_CREATION_FAILED = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Invalid user data. Check required fields and formats."
)

USER_UPDATE_FAILED = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Invalid update data. Check provided fields."
)

# Errores internos (500) → Solo para fallos inesperados del sistema
SERVER_ERROR = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal server error. Contact support."
)