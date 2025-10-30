from core.xml_builder import XMLBuilder
from services.lote_service import LoteService
from services.envio_soap_service import EnvioSOAPService
from domain.repositories.doc_repo import DocumentoRepo

class FacturaService:
    def __init__(self, db,soap_endpoint):
        self.db = db
        self.repo_doc = DocumentoRepo(db)
        self.soap_endpoint = soap_endpoint
        
    def procesar_pendientes(self):
        documentos = self.repo_doc.getPendiente()
        estado_nuevo = "PROCESADO"
        xml_list = []
        for doc in documentos:
            xml_de= XMLBuilder().build(doc)
            self.repo_doc.newEstado(doc.id,estado_nuevo)
            xml_list.append(xml_de)
        
        xml_enviar ,nuevolote =LoteService(self.db).crearLotes(xml_list)
        
        
        envio_service = EnvioSOAPService(self.db,self.soap_endpoint)
        respuesta = envio_service.enviar_lote(xml_enviar)
        
        for doc in documentos:
            
            self.repo_doc.loteNro(doc.id,nuevolote.id)
            
        return respuesta 
