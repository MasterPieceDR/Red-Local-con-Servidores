# Proyecto Multi-VLAN Campus Network

## Arquitectura

```
                    INTERNET
                        │
                   Raspberry Pi
                   (Router NAT)
                        │
                   ┌────┴────┐
                   │ Switch0 │ (Core)
                   └────┬────┘
        ┌───────────────┼───────────────┐
        │ PAgP          │ Trunk         │
   ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
   │ Switch1 │     │ Switch3 │     │         │
   └────┬────┘     └────┬────┘     │         │
        │ LACP          │          │         │
   ┌────┴────┐          │          │         │
   │ Switch2 │          │          │         │
   └────┬────┘          │          │         │
        │               │          │         │
   Streaming       FastAPI      Mail     CS 1.6
   VLAN 20         VLAN 10    VLAN 30   VLAN 40
```

## IPs de Servidores

| VLAN | Nombre | Subnet | Gateway | Servidor |
|------|--------|--------|---------|----------|
| 10 | Microservices | 10.10.0.128/27 | 10.10.0.129 | 10.10.0.130 |
| 20 | Streaming | 10.10.0.64/26 | 10.10.0.65 | 10.10.0.66 |
| 30 | Mail Server | 10.10.0.0/26 | 10.10.0.1 | 10.10.0.2 |
| 40 | Counter Strike | 10.10.0.160/27 | 10.10.0.161 | 10.10.0.162 |

---

## VLAN 10 - FastAPI Microservices (10.10.0.130)

### Requisitos
- Docker

### Ejecutar

```powershell
cd fastapi_microservices_vlan10\fastapi_microservices_vlan10
docker compose up -d --build
```

### Probar (desde cualquier VLAN)

```powershell
# Registro
$body = @{name="Juan"; last_name="Perez"; born_date="2000-01-15"; email="test@gmail.com"; nickname="juanp"; password="123456"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://10.10.0.130:8080/client/register" -Method POST -Body $body -ContentType "application/json"

# Login
$body = @{nickname="juanp"; password="123456"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://10.10.0.130:8080/client/login" -Method POST -Body $body -ContentType "application/json"
```

---

## VLAN 20 - Streaming Server (10.10.0.66)

### Requisitos
- VLC Media Player

### Ejecutar (en servidor VLAN 20)

```powershell
vlc video.mp4 --sout "#standard{access=http,mux=ts,dst=:8080}" --loop
```

### Ver stream (desde VLAN 10)

```powershell
vlc http://10.10.0.66:8080
```

---

## VLAN 30 - Mail Server (10.10.0.2)

### Requisitos
- Docker

### Ejecutar

```powershell
cd mail_server_vlan30\mail_server_vlan30
docker compose up -d --build
```

### Probar (desde VLAN 10)

```powershell
$smtp = New-Object System.Net.Mail.SmtpClient("10.10.0.2", 25)
$smtp.Send("test@api.com", "events@mail.com", "Test", "Mensaje de prueba")
```

### Ver correos guardados

```powershell
docker exec mail_server_vlan30 sqlite3 /app/db/MailDB.sqlite "SELECT * FROM received_emails;"
```

---

## VLAN 40 - CS 1.6 Server (10.10.0.162)

### Requisitos
- Python 3
- httpx

### Ejecutar

```powershell
cd Cs16_server_vlan40\Cs16_server_vlan40
pip install httpx
python cs16_event_sender.py
```

### Resultado
Envia eventos cada 15 segundos a FastAPI (VLAN 10).

---

## Comunicaciones

| Desde | Hacia | Puerto | Descripcion |
|-------|-------|--------|-------------|
| VLAN 10 | VLAN 30 | 25 | SMTP interno |
| VLAN 10 | VLAN 20 | 8080 | Ver streaming |
| VLAN 40 | VLAN 10 | 8080 | Enviar resultados CS |
| VLAN 20 | VLAN 10 | 8080 | Notificar stream |
| Todos | Internet | 587 | Gmail SMTP |

---

## Verificacion

1. Ping entre VLANs (debe funcionar via Raspberry Pi)
2. Registro de usuario en FastAPI
3. Ver stream de VLC desde VLAN 10
4. CS envia resultados a FastAPI
5. Mail Server recibe correos de FastAPI
