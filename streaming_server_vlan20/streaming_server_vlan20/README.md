# Streaming Server VLAN 20

## IP del servidor
- **IP**: 10.10.0.66 (dentro de 10.10.0.64/26)
- **Gateway**: 10.10.0.65

## Iniciar Stream con VLC (en servidor VLAN 20)

```powershell
# Transmitir video por HTTP en puerto 8080
vlc video.mp4 --sout "#standard{access=http,mux=ts,dst=:8080}" --loop

# O transmitir pantalla
vlc screen:// --sout "#standard{access=http,mux=ts,dst=:8080}"
```

## Ver Stream (desde cliente VLAN 10)

```powershell
vlc http://10.10.0.66:8080
```

## Notificar evento a FastAPI (opcional)

```powershell
pip install httpx
python stream_event_sender.py
```

## Flujo

```
VLC Server (VLAN 20)              Clientes (VLAN 10)
10.10.0.66:8080        ────────►  vlc http://10.10.0.66:8080
       │
       └──► stream_event_sender.py ──► FastAPI 10.10.0.130:8080
```
