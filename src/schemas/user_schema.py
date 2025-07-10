from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=128, pattern="^[A-Za-z0-9-_]+$",
                    description="Username of the user")
    full_name: str = Field(min_length=1, max_length=128,
                    description="Full name of the user")
    email: EmailStr
 

class UserIn(UserBase):
    password: str = Field(min_length=8, max_length=128,
                    description="Password of the user, must be at least 8 characters long")


class UserOut(UserBase):
    pass

    class Config:
        from_attributes = True

    
