from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import bcrypt
from crud import create_user, get_user_by_nickname, update_password, init_db

app = FastAPI(title="AuthService")

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

init_db()

@app.post("/register")
async def register_user(user: UserRegister):
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    if create_user(user.name, user.last_name, user.born_date, user.email, user.nickname, password_hash):
        return {"status": "success", "message": "Usuario registrado"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email o nickname ya registrado")

@app.post("/login")
async def login_user(user: UserLogin):
    db_user = get_user_by_nickname(user.nickname)
    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    if bcrypt.checkpw(user.password.encode(), db_user[1].encode()):
        return {"status": "success", "message": "Login exitoso"}
    raise HTTPException(status_code=401, detail="Credenciales invalidas")

@app.post("/change_password")
async def change_password(data: ChangePassword):
    db_user = get_user_by_nickname(data.nickname)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not bcrypt.checkpw(data.last_password.encode(), db_user[1].encode()):
        raise HTTPException(status_code=401, detail="Password actual incorrecto")
    new_hash = bcrypt.hashpw(data.new_password.encode(), bcrypt.gensalt()).decode()
    if update_password(data.nickname, new_hash):
        return {"status": "success", "message": "Password actualizado"}
    raise HTTPException(status_code=500, detail="Error al actualizar password")
