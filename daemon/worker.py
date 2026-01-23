import time
from venv import logger
from core.database import get_session
from services.factura_service import FacturaService
from config.setting import SOAP_ENDPOINT, INTERVAL

class SifenWorker:
    def start(self):
        while True:
            with get_session() as db:
                try:
                    FacturaService(db, SOAP_ENDPOINT)
                    respuesta = FacturaService.procesar_pendientes()
                    logger.info(respuesta)
                except Exception as e:
                    logger.error(f"Error al procesar documentos: {str(e)}")
            time.sleep(INTERVAL)

    
