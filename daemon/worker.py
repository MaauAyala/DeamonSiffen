import time
from core.database import get_session
from services.factura_service import FacturaService
from config.setting import SOAP_ENDPOINT, INTERVAL

class SifenWorker:
    def start(self):
        ultimo_id = 0
        while True:
            with get_session() as db:
                FacturaService(db, SOAP_ENDPOINT)
                respuesta = FacturaService.procesar_pendientes()
                print(respuesta)
            time.sleep(INTERVAL)





    # avanza el puntero
    
