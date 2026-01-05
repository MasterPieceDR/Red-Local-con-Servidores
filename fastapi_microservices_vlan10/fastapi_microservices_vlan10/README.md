# FastAPI Microservices VLAN 10

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
# Registro
$body = @{name="Juan"; last_name="Perez"; born_date="2000-01-15"; email="test@gmail.com"; nickname="juanp"; password="123456"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/client/register" -Method POST -Body $body -ContentType "application/json"

# Login
$body = @{nickname="juanp"; password="123456"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/client/login" -Method POST -Body $body -ContentType "application/json"
```

```powershell
docker compose down -v
```

