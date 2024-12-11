from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from ..util import hash_password, verify_password
from ..model.user import User

# fake user database for testing purposes
fake_users_db = {}

router = APIRouter(tags=["auth"])


@router.post('/register')
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(user.password)
    fake_users_db[user.username] = hashed_password
    return {"msg": "User registered successfully"}


@router.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username not in fake_users_db:
        raise HTTPException(status_code=401, detail="Bad username or password")
    
    hashed_password = fake_users_db[user.username]
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Bad username or password")
    
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


@router.get('/protected')
def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}
