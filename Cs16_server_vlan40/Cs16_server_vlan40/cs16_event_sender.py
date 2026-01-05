import asyncio
import httpx
import random
import logging
from src.persistence import setup_database, log_game_result

# --- CONFIGURACIÓN DE RED Y SERVICIO ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# IP del CoreAPI (Gateway de la VLAN 10)
FASTAPI_CORE_URL = "http://10.10.0.130:8080/server/event" 

def simulate_cs16_match():
    """Genera datos simulados para una partida de CS 1.6."""
    # Simulación de jugadores y equipos típicos
    players = ["Terrrorist_X", "Counter_Y", "Jugador_Z"]
    teams = ["Terrorists", "Counter-Terrorists"]
    
    # Asignamos un ganador y un mapa
    winner = random.choice(teams)
    map_name = random.choice(["de_dust2", "cs_assault", "de_inferno"])
    score = f"{random.randint(10, 16)}-{random.randint(5, 15)}"
    
    details = f"Mapa {map_name}, Marcador {score}"
    
    return {
        "source": "CS 1.6",  # Identificador claro para la FastAPI
        "winner": winner,
        "details": details
    }

async def send_event(match_data: dict):
    """Envía la información de la partida al CoreAPI."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # La llamada al mismo endpoint /server/event es la clave de la orquestación.
            response = await client.post(FASTAPI_CORE_URL, json=match_data)
            response.raise_for_status() 
            
            logging.info(f"Evento enviado a FastAPI: {response.json().get('message')}")
            log_game_result(match_data['winner'], match_data['details'])

    except httpx.ConnectError:
        logging.error(f"ERROR: No se pudo conectar al CoreAPI en {FASTAPI_CORE_URL}. ¿Está encendido el CoreAPI/Router?")
    except httpx.HTTPStatusError as e:
        logging.error(f"ERROR HTTP: El CoreAPI devolvió {e.response.status_code}. Mensaje: {e.response.text}")
    except Exception as e:
        logging.error(f"Error inesperado al enviar evento: {e}")

async def main():
    setup_database()
    logging.info("CS 1.6 Server: Iniciando simulación de eventos...")
    
    while True:
        match_data = simulate_cs16_match()
        logging.info(f"SIMULANDO PARTIDA: Ganador -> {match_data['winner']}")
        
        await send_event(match_data)
        
        # Simular una partida cada 15 segundos
        await asyncio.sleep(15) 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("CS 1.6 Server Simulation detenido por el usuario.")
