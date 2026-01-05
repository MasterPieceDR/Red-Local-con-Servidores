import asyncio
import logging
import aiosmtpd.controller

from src.persistence import setup_database
from src.handler import CustomMailHandler

# --- CONFIGURACIÓN DEL SERVIDOR SMTP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#'0.0.0.0' permite escuchar en todas las interfaces de red
LISTEN_IP = '0.0.0.0'
#10.10.0.2 es la IP del servidor en VLAN 30 
#LISTEN_IP = '10.10.0.2'
LISTEN_PORT = 25

async def run_server():
    """Inicializa el controlador SMTP y lo mantiene corriendo."""
    
    # 1. Inicializar la BDD (asegura que la tabla exista)
    setup_database()
    
    # 2. Inicializar el Controlador SMTP
    controller = aiosmtpd.controller.Controller(CustomMailHandler(), 
                                                 hostname=LISTEN_IP, 
                                                 port=LISTEN_PORT)
    
    controller.start()
    logging.info(f"Servidor SMTP (Receptor de Eventos) iniciado en {LISTEN_IP}:{LISTEN_PORT}")
    
    # 3. Bucle para mantener el servidor activo
    try:
        while True:
            await asyncio.sleep(3600)  # Duerme una hora, mantiene el proceso vivo
    except asyncio.CancelledError:
        logging.info("Servidor SMTP detenido.")
    finally:
        controller.stop()

if __name__ == "__main__":
    logging.info("Iniciando la aplicación del Mail Server...")
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logging.info("Proceso terminado por el usuario (KeyboardInterrupt).")
    except Exception as e:
        logging.critical(f"Error inesperado al ejecutar el servidor: {e}")
