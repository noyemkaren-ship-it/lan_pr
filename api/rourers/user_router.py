from fastapi import APIRouter, Response, Request, HTTPException
from api.services.user_services import *
import jwt as pyjwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas.users_shemas.user_get import *
from schemas.users_shemas.user_base import UserSchema

limiter = Limiter(key_func=get_remote_address)
user_routers = APIRouter(prefix="/api")

@user_routers.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, response: Response, user: UserGetSchemasByNameAndPassword):
    
    if authenticate(user.name, user.password):
        token = pyjwt.encode({"user": user.name}, "secret", algorithm="HS256")
        
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,     
            samesite="lax"      
        )
        return {"ok": True}
    raise HTTPException(status_code=404, detail="user not found")

@user_routers.get("/user/{user_id}")
@limiter.limit("30/minute")
async def get_user(request: Request, user_id: int):
    token = request.cookies.get("token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Нет токена")
    
    try:
        payload = pyjwt.decode(token, "secret", algorithms=["HS256"])
        user_from_token = payload.get("user")
        
        if user_from_token != "admin":
            raise HTTPException(status_code=403, detail="Ты не админ, иди отсюда!")
        
        user_data = get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="user not found")
        
        return user_data
        
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Плохой токен")

@user_routers.post("/register")
@limiter.limit("5/minute")
async def register_api(request: Request, user: UserSchema, response: Response):
    result = register_user(name=user.name, email=user.email, password=user.password)
    
    if result:
        if authenticate(user.name, user.password):
            token = pyjwt.encode({"user": user.name}, "secret", algorithm="HS256")
            
            response.set_cookie(
                key="token",
                value=token,
                httponly=True,     
                samesite="lax"      
            )
            return {"ok": True}
    
    raise HTTPException(status_code=400, detail="Отказано, и пашёл вон отсюда мамкин хакер!")