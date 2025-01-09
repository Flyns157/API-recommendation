from pydantic import BaseModel, EmailStr, constr


class User(BaseModel):
    username: constr(min_length=1)  # NotBlank equivalent
    mail: EmailStr  # Email and NotBlank equivalent
    name: constr(min_length=1)


class UserInDB(User):
    password: constr(min_length=1)
