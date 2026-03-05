from core.infraestructure.soap.soap_client import SOAPClient
from core.infraestructure.xml.xml_builder import XMLBuilder
from core.infraestructure.xml.xml_builder_lote import XMLBuilderLote
from domain.models.models import Emisor
from services.lote_service import LoteService
from domain.repositories.doc_repo import DocumentoRepo
from domain.repositories.lote_repo import LoteRepository, LoteDocumentoRepository
from config.logger import get_logger

logger = get_logger(__name__)

class FacturaService:
    def __init__(self, db):
        self.db = db
        self.repo_doc = DocumentoRepo(db)
        self.lote_repo = LoteRepository(db)
        self.lote_doc_repo = LoteDocumentoRepository(db)
        self.cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
        self.key_path = r"C:\Users\mauri\clave_privada_desenc.pem"
        
    def procesar_pendientes(self, batch_size: int = 50):
        logger.info("Iniciando procesamiento de documentos pendientes")

        documentos = self.repo_doc.getPendiente()  # ESTADO de la factura = PENDIENTE_ENVIO
        if not documentos:
            return {"total_procesados": 0, "lotes": []}

        
        documentos = sorted(
            documentos,
            key=lambda d: (
                d.emisor.id if d.emisor else 0,
                int(d.tipo_doc) if d.tipo_doc else 1
            )
        )

        resultados = []

        
        grupos = {}
        for doc in documentos:
            if not doc.emisor:
                logger.warning(f"Documento {doc.id} sin emisor. Se omite.")
                continue

            clave = (doc.emisor.id, int(doc.tipo_doc))
            grupos.setdefault(clave, []).append(doc)

       
        for (emisor_id, tipo_doc), docs_grupo in grupos.items():

            emisor = docs_grupo[0].emisor

            logger.info(
                f"Procesando {len(docs_grupo)} docs | Emisor {emisor_id} | Tipo {tipo_doc}"
            )

            for i in range(0, len(docs_grupo), batch_size):
                batch = docs_grupo[i:i + batch_size]

                resultado = self._procesar_lote(
                    documentos=batch,
                    tipo_documento=str(tipo_doc),
                    emisor=emisor
                )

                resultados.append(resultado)

        return {
            "total_procesados": len(documentos),
            "lotes": resultados
        }

    
    def _procesar_lote(self, documentos: list, tipo_documento: str,emisor:Emisor) -> dict: 
    
        """
        Procesa un lote de documentos
        """

        
       
        lote_data = {
            "estado": "PENDIENTE_ENVIO",    #Primer ESTADO del lote PENDIENTE_ENVIO
            "xml_request": None,
            "xml_response": None,
            "tipo_documento": tipo_documento,
            "emisor":emisor,
        }
        
        lote = self.lote_repo.crear_lote(lote_data)
        logger.info(f"Lote creado en BD con ID: {lote.id}")
        
    
        documentos_procesados = []
        xmls_documentos = []
        
        for doc in documentos:
            try:
                
                xml_de = XMLBuilder(self.db).build(doc)
                
                
                doc_data = {
                    "documento_id": doc.id,
                    "cdc": doc.cdc_de,  
                    "xml": xml_de
                }
                
                documentos_procesados.append(doc_data)
                self.repo_doc.loadXML(xml_de.decode('utf-8'),doc.cdc_de)
                xmls_documentos.append(xml_de)
                
                
                self.lote_doc_repo.agregar_documento_a_lote(
                    lote_id=lote.id,
                    documento_id=doc.id
                )
                
                logger.debug(f"Documento {doc.id} preparado para lote {lote.id}")
                
            except Exception as e:
                logger.error(f"Error procesando documento {doc.id}: {str(e)}")
                
                if hasattr(doc, 'id'):
                    self.repo_doc.newEstado(doc.id, "ERROR_XML")  #ERROR_XML para el estado del documento
        
        
        try:
            xml_lote = XMLBuilderLote().build_lote(xmls_documentos)
            
            
            self.lote_repo.actualizar_lote(    #ACA  actualizar el estado de lote a "LOTE_ARMADO"
                lote_id=lote.id,
                update_data={
                    "xml_request": xml_lote.decode('utf-8'),
                    "estado":"LOTE_ARMADO"
                    }
                
            )
            
            logger.info(f"Request{lote.id}")
            
        except Exception as e:
            logger.error(f"Error generando XML del lote {lote.id}: {str(e)}")
            self.lote_repo.actualizar_lote(
                lote_id=lote.id,
                update_data={"estado": "ERROR_XML"}    #ACA ESTADO = ERROR_XML si es que no se puede armar los lotes
            )
            raise
        
        
        try:
            soap_client = SOAPClient(emisor.cert_path, emisor.key_path, True)
            response = LoteService.rEnvioLote(soap_client,xml=xml_lote,id=lote.id)
            
            self._procesar_respuesta_lote(lote.id, response, documentos_procesados) 
            logger.info(f"Lote {lote.id} enviado exitosamente a SIFEN")
            
            return {
                "lote_id": lote.id,
                "estado": "ENVIADO_SIFEN",   # si todo sale bien se marca nuevo estado de lote como ENVIADO_SIFEN
                "documentos": len(documentos_procesados),
                "respuesta": response[:500] if response else None 
            }
            
        except Exception as e:
            logger.error(f"Error enviando lote {lote.id}: {str(e)}")
            
            
            self.lote_repo.actualizar_lote(
                lote_id=lote.id,
                update_data={
                    "estado": "ERROR_ENVIO", #SI hay error de envio de marca estado como ERROR_ENVIO
                    "xml_response": str(e)
                }
            )
            
            # Actualizar estados de documentos
            self.repo_doc.masiveSetState(doc_data,state="ERROR_ENVIO")
            
            raise
    
    def _procesar_respuesta_lote(self, lote_id: int, respuesta: str, documentos: list):
        """
        Procesa la respuesta del lote y actualiza estados
        """
        try:
            import xml.etree.ElementTree as ET
            
            # Extraer dProtConsLote del XML de respuesta
            nro_lote_sifen = None
            try:
                if not respuesta:
                    raise ValueError("Respuesta SOAP vacía")
                root = ET.fromstring(respuesta)
                ns = {'ns2': 'http://ekuatia.set.gov.py/sifen/xsd'}
                prot_cons_lote = root.find('.//ns2:dProtConsLote', ns)
                if prot_cons_lote is not None and prot_cons_lote.text:
                    nro_lote_sifen = prot_cons_lote.text.strip()
                    logger.info(f"Protocolo SIFEN {nro_lote_sifen} extraído para lote {lote_id}")
                    update_data = {
                        "xml_response": respuesta,
                        "estado": "RECIBIDO_SIFEN"   #ACA CREO QUE DEBERIA DE SER ESTADO : RECIBIDO_SIFEN
                    }
                else:
                    update_data = {
                        "xml_response": respuesta,
                        "estado": "LOTE_RECHAZADO"  # estado si sifen rechaza el lote 
                    }
                    
            except Exception as e:
                logger.error(f"Error extrayendo protocolo del lote {lote_id}: {str(e)}")
            


            
            if nro_lote_sifen:
                update_data["nro_lote_sifen"] = nro_lote_sifen
            
            self.lote_repo.actualizar_lote(lote_id, update_data)  
            
            # 
            # Aca se deberia de marcar como RECIBIDO_SIFEN por cada documento
            self.repo_doc.masiveSetState(documentos,state="RECIBIDO_SIFEN")
                
            
            logger.info(f"Respuesta del lote {lote_id} procesada")
            
        except Exception as e:
            logger.error(f"Error procesando respuesta del lote {lote_id}: {str(e)}")
            raise
    
