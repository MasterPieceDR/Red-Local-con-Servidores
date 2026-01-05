from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import httpx

# Docker (actual)
AUTH_SERVICE_URL = "http://auth_service:8001"
NOTIFIER_SERVICE_URL = "http://notifier_service:8002"
# Producción sin Docker (todos en mismo servidor VLAN 10):
# AUTH_SERVICE_URL = "http://localhost:8001"
# NOTIFIER_SERVICE_URL = "http://localhost:8002"

app = FastAPI(title="CoreAPI")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class UserRegister(BaseModel):
    name: str
    last_name: str
    born_date: str
    email: str
    nickname: str
    password: str

class UserLogin(BaseModel):
    nickname: str
    password: str

class ChangePassword(BaseModel):
    nickname: str
    last_password: str
    new_password: str

class RecoverPassword(BaseModel):
    nickname: str
    email: str

class ServerEvent(BaseModel):
    source: str
    details: str
    winner: str | None = None

def calculate_age(born_date: str) -> int:
    from datetime import datetime
    born = datetime.strptime(born_date, "%Y-%m-%d")
    today = datetime.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

@app.post("/client/register")
async def client_register(user: UserRegister):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{AUTH_SERVICE_URL}/register", json=user.model_dump())
        if r.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=r.status_code, detail=r.json().get("detail"))
        age = calculate_age(user.born_date)
        await client.post(f"{NOTIFIER_SERVICE_URL}/register_email", json={
            "nickname": user.nickname,
            "age": age,
            "recipient": "registration_log@mail.com"
        })
        await client.post(f"{NOTIFIER_SERVICE_URL}/notify/external", json={
            "recipient": user.email,
            "subject": "Registro Exitoso",
            "body": f"Bienvenido {user.name}, tu registro fue exitoso"
        })
    return {"status": "success", "message": "Usuario registrado"}

@app.post("/client/login")
async def client_login(user: UserLogin):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{AUTH_SERVICE_URL}/login", json=user.model_dump())
        if r.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=r.status_code, detail=r.json().get("detail"))
    return {"status": "success", "message": "Login exitoso"}

@app.post("/client/change_password")
async def client_change_password(data: ChangePassword):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{AUTH_SERVICE_URL}/change_password", json=data.model_dump())
        if r.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=r.status_code, detail=r.json().get("detail"))
    return {"status": "success", "message": "Password actualizado"}

@app.post("/client/recover_password")
async def client_recover_password(data: RecoverPassword):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{NOTIFIER_SERVICE_URL}/recover_password", json=data.model_dump())
        if r.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=r.status_code, detail=r.json().get("detail"))
        temp_password = r.json().get("temp_password")
    return {"status": "success", "message": "Password temporal enviado a tu email", "temp_password": temp_password}

@app.post("/server/event")
async def handle_event(event: ServerEvent):
    if event.source == "CS 1.6":
        subject = f"Resultado CS: {event.winner}"
        body = f"{event.details} Resultado: {event.winner}"
    else:
        subject = "Streaming"
        body = event.details
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(f"{NOTIFIER_SERVICE_URL}/notify/internal", json={
                "recipient": "events_log@mail.com",
                "subject": subject,
                "body": body
            })
    except:
        pass
    return {"status": "success", "message": "Evento registrado"}
