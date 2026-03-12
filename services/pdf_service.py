"""
Servicio para generar PDFs de documentos aprobados por SIFEN
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from xml.etree.ElementTree import ParseError

from domain.repositories.doc_repo import DocumentoRepo
from utils.parseXML import parse_sifen_xml
from utils.buildReport import generar_pdf_factura
from config.logger import get_logger

logger = get_logger(__name__)

class PDFService:
    """Servicio para generar y guardar PDFs de documentos aprobados"""
    
    def __init__(self, db):
        self.db = db
        self.repo_doc = DocumentoRepo(db)
        self.pdf_output_dir = self._setup_pdf_directory()
    
    def _setup_pdf_directory(self) -> Path:
        """Configura y crea el directorio para guardar PDFs si no existe"""
        pdf_dir = Path("logs/pdf_generados")
        try:
            pdf_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Directorio de PDFs: {pdf_dir.absolute()}")
            return pdf_dir
        except Exception as e:
            logger.error(f"❌ Error creando directorio de PDFs: {e}")
            raise
    
    def generar_pdfs_aprobados(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Genera PDFs para documentos aprobados
        
        Args:
            batch_size: Cantidad de documentos a procesar por ciclo
            
        Returns:
            Dict con estadísticas del procesamiento
        """
        logger.info("📋 Iniciando generación de PDFs para documentos aprobados...")
        
        # Obtener documentos aprobados
        documentos = self.repo_doc.getAprobados(batch_size=batch_size)
        
        if not documentos:
            logger.info("📭 No hay documentos aprobados pendientes de PDF")
            return {"total_procesados": 0, "exitosos": 0, "errores": 0}
        
        logger.info(f"🔄 Encontrados {len(documentos)} documentos aprobados")
        
        estadisticas = {
            "total_procesados": len(documentos),
            "exitosos": 0,
            "errores": 0,
            "detalles_errores": []
        }
        
        for doc in documentos:
            try:
                # Parsear XML del documento
                if not doc.xml_de:
                    logger.warning(f"⚠️ Documento {doc.id} sin XML. Se omite.")
                    estadisticas["errores"] += 1
                    estadisticas["detalles_errores"].append({
                        "doc_id": doc.id,
                        "cdc": doc.cdc_de,
                        "error": "XML vacío"
                    })
                    continue
                
                # Parsear XML a diccionario con datos de factura
                data_factura = parse_sifen_xml(doc.xml_de)
                
                # Generar nombre de archivo con el número de documento
                num_doc = doc.dnumdoc
                establecimiento = doc.timbrado.dest if doc.timbrado else "000"
                punto_expedicion = doc.timbrado.dpunexp if doc.timbrado else "000"
                
                nombre_archivo = f"{establecimiento}-{punto_expedicion}-{num_doc}.pdf"
                ruta_pdf = self.pdf_output_dir / nombre_archivo
                
                logger.info(f"📄 Generando PDF: {nombre_archivo}")
                
                # Generar PDF
                generar_pdf_factura(data_factura, str(ruta_pdf))
                
                logger.info(f"✅ PDF generado exitosamente: {ruta_pdf}")
                estadisticas["exitosos"] += 1
                
                # Marcar documento como procesado
                self.repo_doc.marcarPDFGenerado(doc.id)
                
            except ParseError as e:
                logger.error(f"❌ Error parseando XML para documento {doc.id}: {e}")
                estadisticas["errores"] += 1
                estadisticas["detalles_errores"].append({
                    "doc_id": doc.id,
                    "cdc": doc.cdc_de,
                    "error": f"Error parseando XML: {str(e)}"
                })
                
            except Exception as e:
                logger.error(f"❌ Error generando PDF para documento {doc.id}: {e}")
                estadisticas["errores"] += 1
                estadisticas["detalles_errores"].append({
                    "doc_id": doc.id,
                    "cdc": doc.cdc_de,
                    "error": str(e)
                })
        
        logger.info(f"📊 Procesamiento completado - Exitosos: {estadisticas['exitosos']}, Errores: {estadisticas['errores']}")
        
        return estadisticas
