import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

router = APIRouter()


# Secret key and algorithm
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=15
        )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/oauth2/token", tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    correct_username = "user"
    correct_password = "password"
    if form_data.username != correct_username or form_data.password != correct_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=datetime.timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}
