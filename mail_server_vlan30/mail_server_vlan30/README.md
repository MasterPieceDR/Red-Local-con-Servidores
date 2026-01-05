# Mail Server VLAN 30

## Ejecutar con Docker (Windows)

```powershell
docker compose up -d --build
```

## Ver logs

```powershell
docker compose logs -f
```

## Detener

```powershell
docker compose down
```

## Probar

```powershell
# Enviar correo de prueba
$smtp = New-Object System.Net.Mail.SmtpClient("localhost", 25)
$smtp.Send("test@api.com", "events@mail.com", "Test", "Mensaje de prueba")

# Ver DB (desde contenedor)
docker exec mail_server_vlan30 sqlite3 /app/db/MailDB.sqlite "SELECT * FROM received_emails;"
```
