import logging
from email import message_from_bytes
from src.persistence import save_email_to_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomMailHandler:
    """
    Manejador personalizado para aiosmtpd. 
    Se encarga de recibir, parsear y transferir el mensaje a la capa de persistencia.
    """
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        """Procesa el mensaje SMTP y llama a la función de persistencia."""
        try:
            # Parsear el mensaje desde bytes
            message = message_from_bytes(envelope.content)
            
            # 1. Obtención de Metadatos
            source = envelope.mail_from or 'unknown@api.com'
            recipient = ', '.join(envelope.rcpt_tos) or 'unknown@mail.com'
            subject = message.get('Subject', 'No Subject')
            body = ""
            
            # 2. Parsing del cuerpo del correo (priorizando texto plano)
            if message.is_multipart():
                for part in message.walk():
                    ctype = part.get_content_type()
                    cdisp = part.get_content_disposition()
                    if ctype == 'text/plain' and cdisp is None:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='replace')
                        break
            else:
                payload = message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='replace')
            
            logging.info(f"RECIBIDO: De={source}, Para={recipient}, Asunto='{subject}'")
            
            # 3. Llama a la capa de persistencia para guardar el evento
            save_email_to_db(source, recipient, subject, body)
            
            return '250 Message accepted'

        except Exception as e:
            logging.error(f"Error crítico en el manejador SMTP al procesar: {e}")
            return '500 Error processing message'
