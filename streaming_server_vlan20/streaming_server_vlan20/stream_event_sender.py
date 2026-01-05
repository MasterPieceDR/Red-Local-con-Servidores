import asyncio
import httpx
import logging
import time
from src.persistence import setup_database, log_stream_event

# --- CONFIGURACIÓN DE RED Y SERVICIO ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# IP del CoreAPI en VLAN 10 (10.10.0.130:8080)
FASTAPI_CORE_URL = "http://10.10.0.130:8080/server/event"
STREAMER_NAME = "VLC_Server_VLAN20"

def simulate_start_stream():
    """Genera datos simulados para el inicio de una transmisión."""
    return {
        "source": "STREAMING",
        "details": f"{STREAMER_NAME} ha comenzado a transmitir en vivo: 'Gaming Session 2025'",
        "winner": None # Este campo es irrelevante para streaming
    }

async def send_event(event_data: dict):
    """Envía la información del evento de streaming al CoreAPI."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(FASTAPI_CORE_URL, json=event_data)
            response.raise_for_status() # Lanza error si la respuesta es 4xx o 5xx
            
            logging.info(f"Evento enviado a FastAPI: {response.json().get('message')}")
            
            # Registrar localmente solo después de asegurar el éxito del envío
            log_stream_event(STREAMER_NAME, "LIVE")

    except httpx.ConnectError:
        logging.error(f"ERROR: No se pudo conectar al CoreAPI en {FASTAPI_CORE_URL}. ¿Está encendido y ruteando el Raspberry Pi?")
    except httpx.HTTPStatusError as e:
        logging.error(f"ERROR HTTP: El CoreAPI devolvió {e.response.status_code}. Mensaje: {e.response.text}")
    except Exception as e:
        logging.error(f"Error inesperado al enviar evento: {e}")

async def main():
    setup_database()
    logging.info("Streaming Server: Listo para simular eventos...")
    
    # Simular un inicio de transmisión 5 segundos después de iniciar
    await asyncio.sleep(5) 
    
    stream_data = simulate_start_stream()
    logging.info(f"SIMULANDO EVENTO: Inicio de Transmisión por -> {STREAMER_NAME}")
    
    await send_event(stream_data)
    
    # Mantener el script corriendo para observar los logs y simular que el stream está activo
    logging.info("El Stream está 'en vivo'. Presiona Ctrl+C para finalizar la simulación.")
    while True:
        await asyncio.sleep(60) 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Streaming Server Simulation detenido por el usuario.")

