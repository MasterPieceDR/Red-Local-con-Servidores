import sqlite3
import datetime
import logging
import os

# --- CONFIGURACIÓN DE LA BDD ---
DB_DIR = 'db'
DB_FILE = os.path.join(DB_DIR, 'MailDB.sqlite')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_database():
    """Crea la tabla si no existe. Debe ser llamada al inicio del servidor."""
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS received_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                recipient TEXT,
                subject TEXT,
                body TEXT,
                received_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        logging.info(f"Base de datos SQLite '{DB_FILE}' inicializada.")
    except Exception as e:
        logging.critical(f"ERROR FATAL al inicializar la base de datos: {e}")
        raise

def save_email_to_db(source: str, recipient: str, subject: str, body: str):
    """Guarda los datos del correo en la tabla received_emails."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Uso de parámetros (?) para prevenir inyección SQL
        cursor.execute(
            "INSERT INTO received_emails (source, recipient, subject, body, received_at) VALUES (?, ?, ?, ?, ?)",
            (source, recipient, subject, body, datetime.datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        logging.info("Mensaje guardado exitosamente en la BDD.")
    except Exception as e:
        logging.error(f"Error al guardar mensaje en SQLite: {e}")