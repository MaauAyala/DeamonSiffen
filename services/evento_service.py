# services/evento_service.py
from domain.repositories.evento_repo import EventoRepository
from core.infraestructure.soap.soap_client import SOAPClient
from core.infraestructure.use_cases.enviEv import sendEvento
from config.logger import get_logger
from utils.parseResponseEvento import parse_evento_response
logger = get_logger(__name__)

class EventoService:
    def __init__(self, db):
        self.db = db
        self.evento_repo = EventoRepository(db)
        
        # cambiar los certpath de acuerdo al emisor en la bd PD: falta crear los campos etc en la bd
        self.soap_client = SOAPClient(
            cert_path=r"C:\Users\mauri\credenciales\certificado.pem",
            key_path=r"C:\Users\mauri\clave_privada_desenc.pem",
            debug=True
        )
    
    def procesar_eventos_pendientes(self, batch_size: int = 20):
        """Procesa eventos pendientes"""
        logger.info("Iniciando procesamiento de eventos pendientes")
        
        eventos = self.evento_repo.get_pendientes()
        if not eventos:
            return {"total_procesados": 0}
        
        for i in range(0, len(eventos), batch_size):
            batch = eventos[i:i + batch_size]
            self._procesar_lote_eventos(batch)
        
        return {"total_procesados": len(eventos)}
    
    def _procesar_lote_eventos(self, eventos):
        """Procesa un lote de eventos"""
        for evento in eventos:
            try:
                self._procesar_evento_individual(evento)
            except Exception as e:
                logger.error(f"Error procesando evento {evento.id}: {e}")
    
    def _procesar_evento_individual(self, evento):
        """Procesa un evento individual"""
        try:
            logger.info(f"Procesando evento {evento.id}")
            
            # 1. Generar XML del evento
            from core.infraestructure.xml.eventBuilder import eventBuilder
            builder = eventBuilder()
            xml = builder.build(evento)

            if isinstance(xml, str):
                xml_bytes = xml.encode("utf-8")
            elif isinstance(xml, bytes):
                xml_bytes = xml
            else:
                raise TypeError(f"XML inválido, tipo: {type(xml)}")

            response = sendEvento(self.soap_client, xml_bytes, evento.id)

           # Si es requests.Response
            if hasattr(response, "content"):
                response_bytes = response.content
            # Si es httpx.Response
            elif hasattr(response, "read"):
                response_bytes = response.read()
            else:
                response_bytes = response

            res = parse_evento_response(response_bytes)
            

            if not res["dCodRes"]:
                self.evento_repo.update_estado(evento.id, "ERROR")
                logger.error(f"Respuesta inválida para evento {evento.id}")
                return

            # Guardar respuesta completa en BD
            self.evento_repo.update_respuesta(
                evento.id,{
                "dcodres":res["dCodRes"],
                "dmsgres":res["dMsgRes"],
                "dprot_aut":res["dProtAut"],
                "destres":res["dEstRes"],
                "dfecproc":res["dFecProc"],
                }
            )

            if res["dCodRes"] in ("0600", "0300"):
                self.evento_repo.update_estado(evento.id, "PROCESADO")
                logger.info(f"Evento {evento.id} procesado OK")
            else:
                self.evento_repo.update_estado(evento.id, "ERROR")
                logger.error(f"Evento {evento.id} rechazado: {res['dMsgRes']}")
                
        except Exception as e:
            self.evento_repo.update_estado(evento.id, "ERROR")
            logger.error(f"Error procesando evento {evento.id}: {e}")
            raise