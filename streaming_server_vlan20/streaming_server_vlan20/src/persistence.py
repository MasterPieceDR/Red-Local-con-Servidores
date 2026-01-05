import sqlite3
import datetime
import logging
import os

DB_DIR = 'db'
DB_FILE = os.path.join(DB_DIR, 'StreamDB.sqlite')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_database():
    """Crea la tabla de registro de transmisiones si no existe."""
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stream_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                streamer_name TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()
        logging.info(f"Base de datos de streaming '{DB_FILE}' inicializada.")
    except Exception as e:
        logging.critical(f"Error fatal al inicializar la BDD: {e}")
        raise

def log_stream_event(streamer: str, status: str):
    """Registra el inicio/fin de la transmisión en la BDD local."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stream_logs (streamer_name, status, timestamp) VALUES (?, ?, ?)",
            (streamer, status, datetime.datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        logging.info(f"Evento de streaming registrado localmente. Streamer: {streamer}, Estado: {status}")
    except Exception as e:
        logging.error(f"Error al registrar evento de streaming en SQLite: {e}")
