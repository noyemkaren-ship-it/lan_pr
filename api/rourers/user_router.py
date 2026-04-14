from fastapi import APIRouter, Response, Request, HTTPException
from api.services.user_services import *
import jwt as pyjwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas.users_shemas.user_get import *
from schemas.users_shemas.user_base import UserSchema
from token_opertion import SECRET_KEY

limiter = Limiter(key_func=get_remote_address)
user_routers = APIRouter(prefix="/api")

@user_routers.post("/login", tags=["🔐 Auth", "user"])
@limiter.limit("5/minute")
async def login(request: Request, response: Response, user: UserGetSchemasByNameAndPassword):
    
    auth_result = authenticate(user.name, user.password)
    
    if auth_result["success"]:
        token = pyjwt.encode({"user": user.name}, SECRET_KEY, algorithm="HS256")
        
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,     
            samesite="lax"      
        )
        return {"ok": True, "message": "Успешный вход"}
    
    # Возвращаем конкретную ошибку
    error_msg = auth_result.get("error", "Неверные учетные данные")
    if "не найден" in error_msg:
        raise HTTPException(status_code=404, detail=error_msg)
    else:
        raise HTTPException(status_code=401, detail=error_msg)

@user_routers.get("/user/{user_id}", tags=["Get user👤", "user"])
@limiter.limit("30/minute")
async def get_user(request: Request, user_id: int):
    token = request.cookies.get("token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Нет токена")
    
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_from_token = payload.get("user")
        
        # Проверка прав (можно сделать более гибкой)
        if user_from_token != "admin":
            # Получаем пользователя по ID из токена для проверки прав
            current_user = get_user_by_name(user_from_token)
            if not current_user or current_user.id != user_id:
                raise HTTPException(status_code=403, detail="У вас нет прав для просмотра этого пользователя")
        
        user_data = get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return user_data
        
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@user_routers.get("/user/name/{user_name}", tags=["Get user👤", "user"])
@limiter.limit("30/minute")
async def get_user_name(request: Request, user_name: str):
    token = request.cookies.get("token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Нет токена")
    
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_from_token = payload.get("user")
        
        # Только админ может просматривать других пользователей
        if user_from_token != "admin" and user_from_token != user_name:
            raise HTTPException(status_code=403, detail="У вас нет прав для просмотра этого пользователя")
        
        user_data = get_user_by_name(user_name)
        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return user_data
        
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@user_routers.post("/register", tags=["🔐 Auth", "user"])
@limiter.limit("5/minute")
async def register_api(request: Request, user: UserSchema, response: Response):
    register_result = register_user(name=user.name, email=user.email, password=user.password)
    
    if register_result["success"]:
        # Автоматически логиним пользователя после регистрации
        auth_result = authenticate(user.name, user.password)
        
        if auth_result["success"]:
            token = pyjwt.encode({"user": user.name}, SECRET_KEY, algorithm="HS256")
            
            response.set_cookie(
                key="token",
                value=token,
                httponly=True,     
                samesite="lax"      
            )
            return {"ok": True, "message": "Регистрация успешна", "user_id": register_result["user"].id}
        else:
            # Регистрация прошла, но авто-логин не удался (маловероятно)
            return {"ok": True, "message": "Регистрация успешна, но войдите самостоятельно"}
    
    # Возвращаем ошибку регистрации
    error_msg = register_result.get("error", "Ошибка регистрации")
    raise HTTPException(status_code=400, detail=error_msg)

@user_routers.post("/logout", tags=["🔐 Auth", "user"])
async def logout(response: Response):
    response.delete_cookie("token")
    return {"ok": True, "message": "Выход выполнен успешно"}

@user_routers.delete("/user/{user_id}", tags=["user"])
@limiter.limit("10/minute")
async def delete_user_endpoint(request: Request, user_id: int):
    token = request.cookies.get("token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Нет токена")
    
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_from_token = payload.get("user")
        
        # Только админ может удалять пользователей
        if user_from_token != "admin":
            raise HTTPException(status_code=403, detail="Только администратор может удалять пользователей")
        
        delete_result = delete_user(user_id)
        
        if delete_result["success"]:
            return {"ok": True, "message": "Пользователь успешно удален"}
        else:
            raise HTTPException(status_code=404, detail=delete_result.get("error", "Пользователь не найден"))
        
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен")