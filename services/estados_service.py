from typing import List
import logging
from venv import logger
from pytest import Session
from domain.repositories.lote_repo import LoteRepository
from domain.repositories.doc_repo import DocumentoRepo
from core.infraestructure.soap.soap_client import SOAPClient
from domain.models.models import Lote
from services.consulta_lote_service import consultaLote
from utils.parseResponseLote import parse_lote_response

class EstadosService:
    def __init__(self, db: Session,limit):
        self.db = db
        self.db = db
        self.limit = limit
        self.lote_repo = LoteRepository(db)
        self.doc_repo = DocumentoRepo(db)
        self.cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
        self.key_path = r"C:\Users\mauri\clave_privada_desenc.pem"
        
    def processLotes(self,estado:str):
        
       """Procesa facturas por lote para consultar su estado luego del envio """
       logger.info(f"🔍 Buscando lotes con estado: {estado}")
       
       # Depuración: mostrar todos los lotes existentes
       logger.info("🔍 DEPURACIÓN - Todos los lotes en BD:")
       self.lote_repo.listar_todos_los_lotes(10)
       
       LotesPending:List[Lote]=self.lote_repo.listar_lotes_por_estado(estado,self.limit)
       logger.info(f"📊 Lotes encontrados con estado '{estado}': {len(LotesPending)}")
       
       # Mostrar detalles de los lotes encontrados para depuración
       for lote in LotesPending:
           logger.info(f"   - Lote ID: {lote.id}, Estado: {lote.estado}, Nro SIFEN: {lote.nro_lote_sifen}")
       
       total_procesados = 0
       
       for lote in LotesPending:
            try:
                soap_client = SOAPClient(lote.emisor.cert_path, lote.emisor.key_path, True)
                response = consultaLote(soap_client,lote.id,lote.nro_lote_sifen)
                dataDE = parse_lote_response(response.content)
                self.doc_repo.loadEstRes(dataDE)
                
                # ACTUALIZAR ESTADO DEL LOTE PARA EVITAR BUCLE
                self.lote_repo.actualizar_lote(lote.id, {"estado": "PROCESADO"})
                
                logger.info(f"Lote N* {lote.id} consultado correctamente")
                total_procesados += 1
                
            except Exception as e:
                logger.error(f"Error procesando respuesta del lote {lote.id}: {str(e)}")
                # No elevar la excepción, continuar con el siguiente lote
                continue
       
       return {"total_procesados": total_procesados}