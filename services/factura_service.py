from core.infraestructure.soap.soap_client import SOAPClient
from core.infraestructure.xml.xml_builder import XMLBuilder
from core.infraestructure.xml.xml_builder_lote import XMLBuilderLote
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

        documentos = self.repo_doc.getPendiente()
        if not documentos:
            return {"total_procesados": 0, "lotes": []}

        # 🔥 Agrupar por tipo de documento (FE, NC, etc.)
        grupos = {}
        for doc in documentos:
            # Usar el campo tipo_doc que agregaste
            tipo_doc = doc.tipo_doc if hasattr(doc, 'tipo_doc') and doc.tipo_doc else 'FE'
            grupos.setdefault(tipo_doc, []).append(doc)

        resultados = []

        for tipo_doc, docs_tipo in grupos.items():
            logger.info(f"Procesando {len(docs_tipo)} documentos tipo {tipo_doc}")

            for i in range(0, len(docs_tipo), batch_size):
                batch = docs_tipo[i:i + batch_size]
                resultado = self._procesar_lote(batch, tipo_doc)
                resultados.append(resultado)

        return {
            "total_procesados": len(documentos),
            "lotes": resultados
        }

    
    def _procesar_lote(self, documentos: list, tipo_documento: str) -> dict:  # Cambiado de numero_lote a tipo_documento
    
        """
        Procesa un lote de documentos
        """

        
        # 1. Crear el registro del lote en la base de datos
        lote_data = {
            "estado": "PENDIENTE_ENVIO",
            "xml_request": None,
            "xml_response": None,
            "tipo_documento": tipo_documento  # Agregar tipo de documento
        }
        
        lote = self.lote_repo.crear_lote(lote_data)
        logger.info(f"Lote creado en BD con ID: {lote.id}")
        
        # 2. Generar XMLs de documentos y preparar datos para el lote
        documentos_procesados = []
        xmls_documentos = []
        
        for doc in documentos:
            try:
                # Generar XML del documento
                xml_de = XMLBuilder(self.db).build(doc)
                
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
            response = LoteService.rEnvioLote(soap_client,xml=xml_lote,id=lote.id)
            
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
            import xml.etree.ElementTree as ET
            
            # Extraer dProtConsLote del XML de respuesta
            nro_lote_sifen = None
            try:
                root = ET.fromstring(respuesta)
                ns = {'ns2': 'http://ekuatia.set.gov.py/sifen/xsd'}
                prot_cons_lote = root.find('.//ns2:dProtConsLote', ns)
                if prot_cons_lote is not None:
                    nro_lote_sifen = prot_cons_lote.text
                    logger.info(f"Protocolo SIFEN {nro_lote_sifen} extraído para lote {lote_id}")
            except Exception as e:
                logger.error(f"Error extrayendo protocolo del lote {lote_id}: {str(e)}")
            
            # Actualizar respuesta del lote con el número de protocolo
            update_data = {
                "xml_response": respuesta,
                "estado": "ENVIADO"
            }
            
            if nro_lote_sifen:
                update_data["nro_lote_sifen"] = nro_lote_sifen
            
            self.lote_repo.actualizar_lote(lote_id, update_data)
            
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