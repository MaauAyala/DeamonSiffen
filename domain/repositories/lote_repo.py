from sqlalchemy import String, cast
from domain.models.models import LoteDE 

from sqlalchemy.orm import joinedload
from config.setting import limite

class LoteRepo:
    def __init__(self, db):
        self.db = db
        
    def newLote(self,xml_lote,cantidad):
        lote = LoteDE(
        xml_lote=xml_lote,
        cantidad_de=cantidad, 
        )
        self.db.add(lote)
        self.db.commit()
        return lote
    
    
    