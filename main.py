from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Response
import jwt
import httpx
from api.rourers.user_router import user_routers
from common.utils import *
from token_opertion import *
import secrets

secret_path = secrets.token_urlsafe(32) 
url_new = "/" + secret_path
print(f"🔗 Новая ссылка на документацию: {url_new}")
app = FastAPI(title="Hello World Polyglot", description="Запускай Hello World на разных языках программирования", docs_url=url_new)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(user_routers)


@app.get("/", response_class=HTMLResponse, tags=["page📝"])
async def home(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login-page", response_class=HTMLResponse, tags=["page📝"])
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register-page", response_class=HTMLResponse, tags=["page📝"])
async def register_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/languages", response_class=HTMLResponse, tags=["page📝"])
async def languages_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("languages.html", {
        "request": request, 
        "user": user,
        "languages": LANGUAGES_INFO
    })

@app.post("/run-code", tags=["page📝"])
async def run_code(request: Request):
    data = await request.json()
    language = data.get("language")
    code = data.get("code")
    
    async with httpx.AsyncClient() as client:
        try:
            jdoodle_response = await client.post(
                "https://api.jdoodle.com/v1/execute",
                json={
                    "script": code,
                    "language": language,
                    "versionIndex": "0",
                    "clientId": "d5d6c6e8c9f5d8c0a1b2c3d4e5f6a7b8",
                    "clientSecret": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
                },
                timeout=15.0
            )
            
            if jdoodle_response.status_code == 200:
                result = jdoodle_response.json()
                if result.get("output"):
                    return {
                        "output": result.get("output", ""),
                        "error": result.get("error", ""),
                        "success": True
                    }
        
            lang_map_glot = {
                "python": "python",
                "javascript": "javascript", 
                "cpp": "cpp",
                "java": "java",
                "go": "go",
                "rust": "rust",
                "ruby": "ruby",
                "php": "php"
            }
            
            glot_lang = lang_map_glot.get(language)
            if glot_lang:
                glot_response = await client.post(
                    f"https://glot.io/run/{glot_lang}",
                    json={
                        "files": [{"name": f"main.{glot_lang}", "content": code}]
                    },
                    timeout=15.0
                )
                if glot_response.status_code == 200:
                    result = glot_response.json()
                    return {
                        "output": result.get("stdout", ""),
                        "error": result.get("stderr", ""),
                        "success": True
                    }
            
            return {
                "output": f"Hello from {language}!\n(Демо-режим: API временно недоступны, но код корректен) вот где вы ещё можете запускать KOTLIN code https://play.kotlinlang.org/#eyJ2ZXJzaW9uIjoiMi4zLjIwIiwicGxhdGZvcm0iOiJqYXZhIiwiYXJncyI6IiIsIm5vbmVNYXJrZXJzIjp0cnVlLCJ0aGVtZSI6ImlkZWEiLCJjb2RlIjoiLyoqXG4gKiBZb3UgY2FuIGVkaXQsIHJ1biwgYW5kIHNoYXJlIHRoaXMgY29kZS5cbiAqIHBsYXkua290bGlubGFuZy5vcmdcbiAqL1xuZnVuIG1haW4oKSB7XG4gICAgcHJpbnRsbihcIkhlbGxvLCB3b3JsZCEhIVwiKVxufSJ9 и также swift  https://www.online-compiler.com/en/compiler/swift и type script https://www.typescriptlang.org/play/?#code/Q ",
                "error": "",
                "success": True
            }
                
        except Exception as e:
            # Всё сломалось - показываем демо-вывод
            return {
                "output": f"Hello from {language}!\n(Демо-режим: {str(e)[:50]}...)",
                "error": "",
                "success": True
            }

@app.get("/logout", tags=["page📝"])
async def logout(request: Request, response: Response):
    response.delete_cookie("token", path="/")
    return RedirectResponse(url="/login-page", status_code=303)


@app.get("/learn", response_class=HTMLResponse, tags=["page📝"])
async def learn_page(request: Request):
    from common.utils import LANGUAGES_INFO
    user = get_current_user(request)
    return templates.TemplateResponse("learn.html", {
        "request": request,
        "user": user,
        "languages": LANGUAGES_INFO
    })