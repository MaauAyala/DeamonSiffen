# domain/repositories/evento_repo.py
from datetime import datetime
from sqlalchemy.orm import joinedload
from domain.models.models import Evento
from config.setting import limite
from config.logger import get_logger

logger = get_logger(__name__)

class EventoRepository:
    def __init__(self, db):
        self.db = db
    
    def get_pendientes(self):
        """Obtiene eventos pendientes de procesar"""
        try:
            eventos = (
                self.db.query(Evento)
                .filter(
                    Evento.estado_actual == "PENDIENTE_ENVIO"
                )
                .order_by(Evento.id.asc())
                .limit(limite)
                .all()
            )
            
            logger.info(f"Se encontraron {len(eventos)} eventos pendientes")
            return eventos
            
        except Exception as e:
            logger.error(f"Error al obtener eventos pendientes: {str(e)}")
            return []
    
    def get_by_id(self, evento_id: int):
        """Obtiene un evento por su ID"""
        try:
            return self.db.query(Evento).filter(Evento.id == evento_id).first()
        except Exception as e:
            logger.error(f"Error al obtener evento {evento_id}: {str(e)}")
            return None
    
    def get_by_cdc(self, cdc: str):
        """Obtiene eventos por CDC del documento"""
        try:
            return self.db.query(Evento).filter(Evento.cdc_dte == cdc).all()
        except Exception as e:
            logger.error(f"Error al obtener eventos por CDC {cdc}: {str(e)}")
            return []
    
    def create(self, evento_data: dict):
        """Crea un nuevo evento"""
        try:
            evento = Evento(**evento_data)
            self.db.add(evento)
            self.db.commit()
            self.db.refresh(evento)
            logger.info(f"Evento creado exitosamente con ID: {evento.id}")
            return evento
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear evento: {str(e)}")
            raise
    
    def update_estado(self, evento_id: int, nuevo_estado: str):
        """Actualiza el estado de un evento"""
        try:
            evento = self.db.query(Evento).filter(Evento.id == evento_id).first()
            if not evento:
                logger.warning(f"No se encontró evento con ID: {evento_id}")
                return None
            
            evento.estado_actual = nuevo_estado
            self.db.commit()
            logger.info(f"Estado del evento {evento_id} actualizado a: {nuevo_estado}")
            return evento
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar estado del evento {evento_id}: {str(e)}")
            raise
    
    def LoadFecFirma(self, evento_id: int, fec: datetime):
        """Actualiza el estado de un evento"""
        try:
            evento = self.db.query(Evento).filter(Evento.id == evento_id).first()
            if not evento:
                logger.warning(f"No se encontró evento con ID: {evento_id}")
                return None
            
            evento.dfecfirma = fec
            self.db.commit()
            logger.info(f"Fecha Firma del evento {evento_id} actualizado a: {fec}")
            return evento
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar estado del evento {evento_id}: {str(e)}")
            raise

    def update_respuesta(self, evento_id: int, update_data: dict):
        """Actualiza datos de un evento"""
        try:
            evento = self.db.query(Evento).filter(Evento.id == evento_id).first()
            if not evento:
                logger.warning(f"No se encontró evento con ID: {evento_id}")
                return None
            
            for key, value in update_data.items():
                if hasattr(evento, key):
                    setattr(evento, key, value)
            
            self.db.commit()
            self.db.refresh(evento)
            logger.info(f"Evento {evento_id} actualizado exitosamente")
            return evento
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar evento {evento_id}: {str(e)}")
            raise
    
    def delete(self, evento_id: int):
        """Elimina un evento"""
        try:
            evento = self.db.query(Evento).filter(Evento.id == evento_id).first()
            if not evento:
                logger.warning(f"No se encontró evento con ID: {evento_id}")
                return False
            
            self.db.delete(evento)
            self.db.commit()
            logger.info(f"Evento {evento_id} eliminado exitosamente")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar evento {evento_id}: {str(e)}")
            raise
    
    def get_all(self, limit: int = None):
        """Obtiene todos los eventos con límite opcional"""
        try:
            query = self.db.query(Evento).order_by(Evento.id.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            logger.error(f"Error al obtener todos los eventos: {str(e)}")
            return []
    
    def get_by_tipo_evento(self, tipo_evento: int):
        """Obtiene eventos por tipo de evento"""
        try:
            return self.db.query(Evento).filter(Evento.tipeve == tipo_evento).all()
        except Exception as e:
            logger.error(f"Error al obtener eventos por tipo {tipo_evento}: {str(e)}")
            return []
    
    def get_by_rango_fechas(self, fecha_inicio, fecha_fin):
        """Obtiene eventos en un rango de fechas"""
        try:
            return (
                self.db.query(Evento)
                .filter(
                    Evento.dfecfirma >= fecha_inicio,
                    Evento.dfecfirma <= fecha_fin
                )
                .order_by(Evento.dfecfirma.desc())
                .all()
            )
        except Exception as e:
            logger.error(f"Error al obtener eventos por rango de fechas: {str(e)}")
            return []