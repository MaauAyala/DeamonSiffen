from sqlalchemy import String, cast
from domain.models.models import Documento, Emisor 

from sqlalchemy.orm import joinedload
from config.setting import limite

class DocumentoRepo:
    def __init__(self, db,):
        self.db = db
        

    def getPendiente(self):
        docs = (
            self.db.query(Documento)
            .options(
                joinedload(Documento.emisor).joinedload(Emisor.actividades),  # Corregido
                joinedload(Documento.operacion),
                joinedload(Documento.timbrado),
                joinedload(Documento.items),
                joinedload(Documento.totales),
                joinedload(Documento.operacion_comercial),
                joinedload(Documento.eventos),
                joinedload(Documento.estados),
                joinedload(Documento.receptor),
            )
            .filter(
                Documento.estado_actual == "PENDIENTE_ENVIO",
                
            )
            .order_by(Documento.id.asc())
            .limit(limite)  
            .all()
        )

        for doc in docs:
            if doc.timbrado and doc.timbrado.itide == 5: 
                _ = doc.nota_credito_debito  
        
        return docs

            
    
    def newEstado(self, id_doc,estado_nuevo):
        doc = self.db.query(Documento).filter(Documento.id == id_doc).first()
        if not doc:
            return None
        doc.estado_actual = estado_nuevo
        self.db.commit()
        return f'Success'
    
    def loteNro(self,id_doc,nro_lote):
        doc =self.db.query(Documento).filter(Documento.id == id_doc).firts()
        if not doc:
            return None
        doc.nro_lote = nro_lote
        self.db.commit()
        return f'Success'
    

    def getDE(self,id):
        docs = (
            self.db.query(Documento)
            .options(
                joinedload(Documento.emisor).joinedload(Emisor.actividades),
                joinedload(Documento.operacion),
                joinedload(Documento.timbrado),
                joinedload(Documento.items),
                joinedload(Documento.totales),
                joinedload(Documento.operacion_comercial),
                joinedload(Documento.eventos),
                joinedload(Documento.estados),
                joinedload(Documento.receptor),
            )
            .filter(Documento.id == id).first()
        )
        
        return docs

        
        