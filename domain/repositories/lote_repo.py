from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from models import Lote, LoteDocumento, Documento

logger = logging.getLogger(__name__)

class LoteRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def crear_lote(self, lote_data: Dict[str, Any]) -> Lote:
        """
        Crea un nuevo lote
        """
        try:
            lote = Lote(**lote_data)
            self.db.add(lote)
            self.db.commit()
            self.db.refresh(lote)
            logger.info(f"Lote creado con ID: {lote.id}")
            return lote
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al crear lote: {str(e)}")
            raise
    
    def obtener_lote_por_id(self, lote_id: int) -> Optional[Lote]:
        """
        Obtiene un lote por su ID
        """
        try:
            return self.db.query(Lote).filter(Lote.id == lote_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener lote {lote_id}: {str(e)}")
            raise
    
    def obtener_lote_por_nro_sifen(self, nro_lote: str) -> Optional[Lote]:
        """
        Obtiene un lote por su número SIFEN
        """
        try:
            return self.db.query(Lote).filter(
                Lote.nro_lote_sifen == nro_lote
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener lote {nro_lote}: {str(e)}")
            raise
    
    def actualizar_lote(self, lote_id: int, update_data: Dict[str, Any]) -> Optional[Lote]:
        """
        Actualiza un lote existente
        """
        try:
            lote = self.obtener_lote_por_id(lote_id)
            if lote:
                for key, value in update_data.items():
                    setattr(lote, key, value)
                lote.fecha_envio = datetime.now()
                self.db.commit()
                self.db.refresh(lote)
                logger.info(f"Lote {lote_id} actualizado")
            return lote
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al actualizar lote {lote_id}: {str(e)}")
            raise
    
    def actualizar_respuesta_lote(self, lote_id: int, xml_response: str, estado: str) -> Optional[Lote]:
        """
        Actualiza la respuesta XML y estado del lote
        """
        try:
            lote = self.obtener_lote_por_id(lote_id)
            if lote:
                lote.xml_response = xml_response
                lote.estado = estado
                self.db.commit()
                self.db.refresh(lote)
                logger.info(f"Respuesta actualizada para lote {lote_id}")
            return lote
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al actualizar respuesta lote {lote_id}: {str(e)}")
            raise
    
    def listar_lotes_por_estado(self, estado: str, limit: int = 100) -> List[Lote]:
        """
        Lista lotes por estado
        """
        try:
            return self.db.query(Lote).filter(
                Lote.estado == estado
            ).order_by(Lote.fecha_envio.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error al listar lotes por estado {estado}: {str(e)}")
            raise
    
    def eliminar_lote(self, lote_id: int) -> bool:
        """
        Elimina un lote (y sus documentos relacionados por cascade)
        """
        try:
            lote = self.obtener_lote_por_id(lote_id)
            if lote:
                self.db.delete(lote)
                self.db.commit()
                logger.info(f"Lote {lote_id} eliminado")
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al eliminar lote {lote_id}: {str(e)}")
            raise


class LoteDocumentoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def agregar_documento_a_lote(self, lote_id: int, documento_id: int, cdc: str) -> LoteDocumento:
        """
        Agrega un documento a un lote
        """
        try:
            lote_documento = LoteDocumento(
                lote_id=lote_id,
                documento_id=documento_id,
                cdc=cdc
            )
            self.db.add(lote_documento)
            self.db.commit()
            self.db.refresh(lote_documento)
            
            # Actualizar estado del documento
            documento = self.db.query(Documento).filter(
                Documento.id == documento_id
            ).first()
            if documento:
                documento.estado_actual = 'EN_PROCESO_LOTE'
                self.db.commit()
            
            logger.info(f"Documento {documento_id} agregado al lote {lote_id}")
            return lote_documento
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al agregar documento al lote: {str(e)}")
            raise
    
    def agregar_documentos_a_lote(self, lote_id: int, documentos: List[Dict[str, Any]]) -> List[LoteDocumento]:
        """
        Agrega múltiples documentos a un lote
        """
        try:
            lote_documentos = []
            for doc_data in documentos:
                lote_doc = LoteDocumento(
                    lote_id=lote_id,
                    documento_id=doc_data['documento_id'],
                    cdc=doc_data['cdc']
                )
                self.db.add(lote_doc)
                lote_documentos.append(lote_doc)
            
            self.db.commit()
            
            # Actualizar estados de los documentos
            doc_ids = [doc['documento_id'] for doc in documentos]
            documentos_db = self.db.query(Documento).filter(
                Documento.id.in_(doc_ids)
            ).all()
            
            for doc in documentos_db:
                doc.estado_actual = 'EN_PROCESO_LOTE'
            
            self.db.commit()
            
            logger.info(f"{len(documentos)} documentos agregados al lote {lote_id}")
            return lote_documentos
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al agregar documentos al lote: {str(e)}")
            raise
    
    def obtener_documentos_por_lote(self, lote_id: int) -> List[LoteDocumento]:
        """
        Obtiene todos los documentos de un lote
        """
        try:
            return self.db.query(LoteDocumento).filter(
                LoteDocumento.lote_id == lote_id
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener documentos del lote {lote_id}: {str(e)}")
            raise
    
    def obtener_documentos_por_estado(self, estado: str) -> List[LoteDocumento]:
        """
        Obtiene documentos de lotes por estado de resultado
        """
        try:
            return self.db.query(LoteDocumento).filter(
                LoteDocumento.estado_resultado == estado
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener documentos por estado {estado}: {str(e)}")
            raise
    
    def actualizar_estado_documento(self, lote_documento_id: int, 
                                   estado_resultado: str, 
                                   codigo_error: Optional[str] = None,
                                   mensaje_error: Optional[str] = None) -> Optional[LoteDocumento]:
        """
        Actualiza el estado de un documento en el lote
        """
        try:
            lote_doc = self.db.query(LoteDocumento).filter(
                LoteDocumento.id == lote_documento_id
            ).first()
            
            if lote_doc:
                lote_doc.estado_resultado = estado_resultado
                lote_doc.codigo_error = codigo_error
                lote_doc.mensaje_error = mensaje_error
                
                # Actualizar estado del documento principal
                documento = self.db.query(Documento).filter(
                    Documento.id == lote_doc.documento_id
                ).first()
                
                if documento:
                    if estado_resultado == 'APROBADO':
                        documento.estado_actual = 'APROBADO'
                    elif estado_resultado == 'RECHAZADO':
                        documento.estado_actual = 'RECHAZADO'
                
                self.db.commit()
                self.db.refresh(lote_doc)
                logger.info(f"Estado actualizado para documento {lote_doc.documento_id} en lote")
            
            return lote_doc
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al actualizar estado documento: {str(e)}")
            raise
    
    def actualizar_estados_documentos_masivo(self, resultados: List[Dict[str, Any]]) -> bool:
        """
        Actualiza estados de múltiples documentos en lote
        """
        try:
            for resultado in resultados:
                lote_doc = self.db.query(LoteDocumento).filter(
                    LoteDocumento.cdc == resultado['cdc']
                ).first()
                
                if lote_doc:
                    lote_doc.estado_resultado = resultado.get('estado_resultado')
                    lote_doc.codigo_error = resultado.get('codigo_error')
                    lote_doc.mensaje_error = resultado.get('mensaje_error')
                    
                    # Actualizar documento principal
                    documento = self.db.query(Documento).filter(
                        Documento.id == lote_doc.documento_id
                    ).first()
                    
                    if documento and resultado.get('estado_resultado'):
                        if resultado['estado_resultado'] == 'APROBADO':
                            documento.estado_actual = 'APROBADO'
                        elif resultado['estado_resultado'] == 'RECHAZADO':
                            documento.estado_actual = 'RECHAZADO'
            
            self.db.commit()
            logger.info(f"Estados actualizados para {len(resultados)} documentos")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al actualizar estados masivo: {str(e)}")
            raise
    
    def obtener_lote_documento_por_cdc(self, cdc: str) -> Optional[LoteDocumento]:
        """
        Obtiene un LoteDocumento por su CDC
        """
        try:
            return self.db.query(LoteDocumento).filter(
                LoteDocumento.cdc == cdc
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener LoteDocumento por CDC {cdc}: {str(e)}")
            raise
    
    def eliminar_documento_del_lote(self, lote_documento_id: int) -> bool:
        """
        Elimina un documento de un lote
        """
        try:
            lote_doc = self.db.query(LoteDocumento).filter(
                LoteDocumento.id == lote_documento_id
            ).first()
            
            if lote_doc:
                self.db.delete(lote_doc)
                self.db.commit()
                logger.info(f"Documento {lote_documento_id} eliminado del lote")
                return True
            
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error al eliminar documento del lote: {str(e)}")
            raise