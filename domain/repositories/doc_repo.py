from sqlalchemy import String, cast
from domain.models.models import Documento, Emisor, Timbrado # Asegúrate de importar Timbrado
from sqlalchemy.orm import joinedload
from config.setting import limite

class DocumentoRepo:
    def __init__(self, db,):
        self.db = db
        

    def getPendiente(self):
        # 1. Consulta inicial para obtener los documentos sin cargar Emisor y Timbrado
        # Removemos las opciones joinedload para Timbrado y Emisor
        docs = (
            self.db.query(Documento)
            .options(
                joinedload(Documento.operacion),
                joinedload(Documento.items),
                joinedload(Documento.totales),
                joinedload(Documento.operacion_comercial),
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

        # 2. Iterar sobre los documentos para cargar Emisor y Timbrado por ID
        for doc in docs:
            
            # --- Cargar Timbrado por ID ---
            # Asume que Documento tiene un campo 'idtimbrado'
            id_timbrado = doc.idtimbrado 
            if id_timbrado:
                # Consulta para buscar el Timbrado por su ID
                doc.timbrado = self.db.query(Timbrado).filter(Timbrado.id == id_timbrado).first()
            else:
                doc.timbrado = None
                
            # --- Cargar Emisor por ID ---
            # Asume que Documento tiene un campo 'idemisor'
            drucem = doc.drucem 
            if drucem:
                # Consulta para buscar el Emisor por su ID
                # También cargamos sus actividades, ya que eran parte de la carga inicial
                doc.emisor = (
                    self.db.query(Emisor)
                    .options(joinedload(Emisor.actividades))
                    .filter(Emisor.drucem == drucem)
                    .first()
                )
            else:
                doc.emisor = None

            # Lógica original: Acceso a la relación nota_credito_debito si aplica
            if doc.timbrado and doc.timbrado.itide == 5: 
                # Esto fuerza la carga perezosa (lazy load) de la relación si no está joinedload
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
        doc = self.db.query(Documento).filter(Documento.id == id_doc).first()
        if not doc:
            return None
        doc.nro_lote = nro_lote
        self.db.commit()
        return f'Success'
    

    def getDE(self,id):
        doc = (
                    self.db.query(Documento)
                    .options(
                        joinedload(Documento.operacion),
                        joinedload(Documento.items),
                        joinedload(Documento.emisor),
                        joinedload(Documento.timbrado),
                        joinedload(Documento.totales),
                        joinedload(Documento.operacion_comercial),
                        joinedload(Documento.estados),
                        joinedload(Documento.receptor),
                    ).filter(Documento.id == id).first()
                )
        
        # Validar que el documento existe
        if not doc:
            return None
        
        id_timbrado = doc.idtimbrado 
        if id_timbrado:
            # Consulta para buscar el Timbrado por su ID
            doc.timbrado = self.db.query(Timbrado).filter(Timbrado.id == id_timbrado).first()
        else:
            doc.timbrado = None
            
        # --- Cargar Emisor por ID ---
        # Asume que Documento tiene un campo 'idemisor'
        drucem = doc.drucem 
        if drucem:
            # Consulta para buscar el Emisor por su ID
            # También cargamos sus actividades, ya que eran parte de la carga inicial
            doc.emisor = (
                self.db.query(Emisor)
                .options(joinedload(Emisor.actividades))
                .filter(Emisor.drucem == drucem)
                .first()
            )
        else:
            doc.emisor = None

        # Lógica original: Acceso a la relación nota_credito_debito si aplica
        if doc.timbrado and doc.timbrado.itide == 5: 
            # Esto fuerza la carga perezosa (lazy load) de la relación si no está joinedload
            _ = doc.nota_credito_debito 
    
        return doc

    def loadEstRes(self, data: dict):
        for detalle in data["detalles"]:
            doc = self.db.query(Documento).filter(
                Documento.cdc == detalle["cdc"]
            ).first()

            if doc:
                doc.estado_actual = detalle["est_res"]
                doc.prot_aut = detalle["prot_aut"]
                doc.cod_res = detalle["cod_res"]
                doc.msg_res = detalle["msg_res"]

        self.db.commit()
        