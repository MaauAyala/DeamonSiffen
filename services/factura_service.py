from core.soap_client import SOAPClient
from core.xml_builder import XMLBuilder
from core.xml_builder_lote import XMLBuilderLote
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
        """
        Procesa documentos pendientes agrupándolos en lotes
        """
        logger.info("Iniciando procesamiento de documentos pendientes")
        
        # Obtener documentos pendientes
        documentos = self.repo_doc.getPendiente()
        total_documentos = len(documentos)
        
        logger.info(f"Documentos pendientes encontrados: {total_documentos}")
        
        if total_documentos == 0:
            logger.info("No hay documentos pendientes para procesar")
            return {"total_procesados": 0, "lotes": []}
        
        respuestas = {}
        lotes_procesados = []
        
        # Procesar en lotes
        for i in range(0, total_documentos, batch_size):
            batch = documentos[i:i + batch_size]
            logger.info(f"Procesando lote {len(lotes_procesados) + 1} con {len(batch)} documentos")
            
            try:
                # Procesar el lote
                resultado = self._procesar_lote(batch, len(lotes_procesados) + 1)
                lotes_procesados.append(resultado)
                
            except Exception as e:
                logger.error(f"Error procesando lote {len(lotes_procesados) + 1}: {str(e)}")
                respuestas[f"lote_error_{len(lotes_procesados) + 1}"] = str(e)
        
        logger.info(f"Procesamiento completado. Lotes procesados: {len(lotes_procesados)}")
        
        return {
            "total_procesados": total_documentos,
            "lotes": lotes_procesados,
            "errores": respuestas
        }
    
    def _procesar_lote(self, documentos: list, numero_lote: int) -> dict:
        """
        Procesa un lote de documentos
        """
        logger.info(f"Iniciando procesamiento del lote {numero_lote}")
        
        # 1. Crear el registro del lote en la base de datos
        lote_data = {
            "estado": "PENDIENTE_ENVIO",
            "xml_request": None,  # Se actualizará después
            "xml_response": None
        }
        
        lote = self.lote_repo.crear_lote(lote_data)
        logger.info(f"Lote creado en BD con ID: {lote.id}")
        
        # 2. Generar XMLs de documentos y preparar datos para el lote
        documentos_procesados = []
        xmls_documentos = []
        
        for doc in documentos:
            try:
                # Generar XML del documento
                xml_de = XMLBuilder().build(doc)
                
                # Preparar datos para agregar al lote
                doc_data = {
                    "documento_id": doc.id,
                    "cdc": doc.cdc_de,  # Asumiendo que el modelo tiene este campo
                    "xml": xml_de
                }
                
                documentos_procesados.append(doc_data)
                xmls_documentos.append(xml_de)
                
                # Agregar documento al lote en BD
                self.lote_doc_repo.agregar_documento_a_lote(
                    lote_id=lote.id,
                    documento_id=doc.id,
                    cdc=doc.cdc_de
                )
                
                logger.debug(f"Documento {doc.id} preparado para lote {lote.id}")
                
            except Exception as e:
                logger.error(f"Error procesando documento {doc.id}: {str(e)}")
                # Marcar documento como error
                if hasattr(doc, 'id'):
                    self.repo_doc.actualizar_estado(doc.id, "ERROR_XML")
        
        # 3. Generar XML del lote
        try:
            xml_lote = XMLBuilderLote().build_lote(xmls_documentos)
            
            # Actualizar lote con el XML de request
            lote_actualizado = self.lote_repo.actualizar_lote(
                lote_id=lote.id,
                update_data={"xml_request": xml_lote}
            )
            
            logger.info(f"XML de lote generado para lote {lote.id}")
            
        except Exception as e:
            logger.error(f"Error generando XML del lote {lote.id}: {str(e)}")
            # Actualizar estado del lote a error
            self.lote_repo.actualizar_lote(
                lote_id=lote.id,
                update_data={"estado": "ERROR_XML"}
            )
            raise
        
        # 4. Enviar lote a SIFEN
        try:
            soap_client = SOAPClient(self.cert_path, self.key_path, True)
            response = soap_client.send(xml_lote)
            
            # 5. Procesar respuesta y actualizar estados
            self._procesar_respuesta_lote(lote.id, response, documentos_procesados)
            
            logger.info(f"Lote {lote.id} enviado exitosamente a SIFEN")
            
            return {
                "lote_id": lote.id,
                "estado": "ENVIADO",
                "documentos": len(documentos_procesados),
                "respuesta": response[:500] if response else None  # Solo primeros 500 chars
            }
            
        except Exception as e:
            logger.error(f"Error enviando lote {lote.id}: {str(e)}")
            
            # Actualizar estado del lote a error
            self.lote_repo.actualizar_lote(
                lote_id=lote.id,
                update_data={
                    "estado": "ERROR_ENVIO",
                    "xml_response": str(e)
                }
            )
            
            # Actualizar estados de documentos
            for doc_data in documentos_procesados:
                self.lote_doc_repo.actualizar_estado_documento(
                    lote_documento_id=doc_data.get("lote_documento_id"),
                    estado_resultado="ERROR_ENVIO",
                    mensaje_error=str(e)
                )
            
            raise
    
    def _procesar_respuesta_lote(self, lote_id: int, respuesta: str, documentos: list):
        """
        Procesa la respuesta del lote y actualiza estados
        """
        try:
            # Actualizar respuesta del lote
            self.lote_repo.actualizar_respuesta_lote(
                lote_id=lote_id,
                xml_response=respuesta,
                estado="ENVIADO"
            )
            
            # TODO: Parsear la respuesta XML para obtener estado de cada documento
            # Por ahora, marcar todos como "ENVIADO" hasta consulta posterior
            for doc_data in documentos:
                # Obtener el LoteDocumento por CDC
                lote_doc = self.lote_doc_repo.obtener_lote_documento_por_cdc(doc_data["cdc"])
                
                if lote_doc:
                    self.lote_doc_repo.actualizar_estado_documento(
                        lote_documento_id=lote_doc.id,
                        estado_resultado="ENVIADO",
                        codigo_error=None,
                        mensaje_error="Lote enviado exitosamente"
                    )
            
            logger.info(f"Respuesta del lote {lote_id} procesada")
            
        except Exception as e:
            logger.error(f"Error procesando respuesta del lote {lote_id}: {str(e)}")
            raise
    
    def consultar_estado_lote(self, lote_id: int):
        """
        Consulta el estado de un lote específico
        """
        try:
            lote = self.lote_repo.obtener_lote_por_id(lote_id)
            
            if not lote:
                logger.error(f"Lote {lote_id} no encontrado")
                return None
            
            # Aquí iría la lógica para consultar el estado en SIFEN
            # usando el número de lote (lote.nro_lote_sifen)
            
            logger.info(f"Consultando estado del lote {lote_id}")
            
            return {
                "lote_id": lote.id,
                "nro_lote_sifen": lote.nro_lote_sifen,
                "estado": lote.estado,
                "fecha_envio": lote.fecha_envio,
                "documentos": self.lote_doc_repo.obtener_documentos_por_lote(lote_id)
            }
            
        except Exception as e:
            logger.error(f"Error consultando estado del lote {lote_id}: {str(e)}")
            raise