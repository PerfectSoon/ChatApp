from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import httpx

from settings import settings

AUTH_SERVICE_URL = "http://localhost:8000/auth"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_SERVICE_URL}/login")

def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=settings.algorithm
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(401, "Invalid token")

async def check_user_exists(user_id: int) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/profile/{user_id}"
            )
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                raise HTTPException(status_code=500, detail="Error checking user existence")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")