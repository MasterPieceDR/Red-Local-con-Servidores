from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from email.mime.text import MIMEText
import smtplib
import secrets

app = FastAPI(title="NotifierService")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class NotifyRequest(BaseModel):
    recipient: str
    subject: str
    body: str

class RegisterEmailRequest(BaseModel):
    nickname: str
    age: int
    recipient: str

class RecoverPasswordRequest(BaseModel):
    nickname: str
    email: str

# Mail Server VLAN 30
MAIL_SERVER_INTERNAL = "10.10.0.2"  # IP del Mail Server en VLAN 30
MAIL_PORT_INTERNAL = 25
# Gmail para correos externos
MAIL_SERVER_EXTERNAL = "smtp.gmail.com"
MAIL_PORT_EXTERNAL = 587
USER = "diegosantillan625@gmail.com"
PASS = "bdaj hsql dwkk hcfc"

@app.post("/notify/internal")
async def notify_internal(data: NotifyRequest):
    sender = "fastapi@vlan10.com"
    msg = MIMEText(data.body)
    msg["Subject"] = data.subject
    msg["From"] = sender
    msg["To"] = data.recipient
    try:
        with smtplib.SMTP(MAIL_SERVER_INTERNAL, MAIL_PORT_INTERNAL) as s:
            s.sendmail(sender, data.recipient, msg.as_string())
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/notify/external")
async def notify_external(data: NotifyRequest):
    msg = MIMEText(data.body)
    msg["Subject"] = data.subject
    msg["From"] = USER
    msg["To"] = data.recipient
    try:
        with smtplib.SMTP(MAIL_SERVER_EXTERNAL, MAIL_PORT_EXTERNAL) as s:
            s.starttls()
            s.login(USER, PASS)
            s.sendmail(USER, data.recipient, msg.as_string())
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error externo: {str(e)}")

@app.post("/register_email")
async def register_email(data: RegisterEmailRequest):
    sender = "fastapi@vlan10.com"
    body = f"Nuevo registro - Nickname: {data.nickname}, Edad: {data.age}"
    msg = MIMEText(body)
    msg["Subject"] = "Nuevo Registro de Usuario"
    msg["From"] = sender
    msg["To"] = data.recipient
    try:
        with smtplib.SMTP(MAIL_SERVER_INTERNAL, MAIL_PORT_INTERNAL) as s:
            s.sendmail(sender, data.recipient, msg.as_string())
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/recover_password")
async def recover_password(data: RecoverPasswordRequest):
    temp_password = secrets.token_urlsafe(8)
    body = f"Usuario: {data.nickname}\nPassword temporal: {temp_password}\nCambia tu password en: /client/change_password"
    msg = MIMEText(body)
    msg["Subject"] = "Recuperacion de Password"
    msg["From"] = USER
    msg["To"] = data.email
    try:
        with smtplib.SMTP(MAIL_SERVER_EXTERNAL, MAIL_PORT_EXTERNAL) as s:
            s.starttls()
            s.login(USER, PASS)
            s.sendmail(USER, data.email, msg.as_string())
        return {"status": "success", "temp_password": temp_password}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
