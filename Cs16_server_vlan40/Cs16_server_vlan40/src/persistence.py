import sqlite3
import datetime
import logging
import os

DB_DIR = 'db'
DB_FILE = os.path.join(DB_DIR, 'GameDB.sqlite')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_database():
    """Crea la tabla de registro de partidas si no existe."""
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                winner TEXT NOT NULL,
                match_details TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()
        logging.info(f"Base de datos de partidas '{DB_FILE}' inicializada.")
    except Exception as e:
        logging.critical(f"Error fatal al inicializar la BDD: {e}")
        raise

def log_game_result(winner: str, details: str):
    """Registra el resultado de la partida en la BDD local."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO game_logs (winner, match_details, timestamp) VALUES (?, ?, ?)",
            (winner, details, datetime.datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        logging.info(f"Partida registrada localmente. Ganador: {winner}")
    except Exception as e:
        logging.error(f"Error al registrar partida en SQLite: {e}")
