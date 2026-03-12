# daemon/pdf_worker.py
"""
Worker de DemonSiffen - Generador automático de PDFs para documentos aprobados por SIFEN
"""
import time
import logging
from typing import Optional
from dataclasses import dataclass

from core.infraestructure.database.database import get_db_session
from services.pdf_service import PDFService

logger = logging.getLogger(__name__)

@dataclass
class PDFWorkerConfig:
    """Configuración del worker de PDFs"""
    interval: int = 120  # Intervalo de 2 minutos para generar PDFs
    batch_size: int = 50  # Procesar 50 documentos por ciclo
    max_retries: int = 3
    debug: bool = False

class PDFWorker:
    """Worker para generar automáticamente PDFs de documentos aprobados por SIFEN"""
    
    def __init__(self, config: Optional[PDFWorkerConfig] = None):
        self.config = config or PDFWorkerConfig()
        self.running = False
        
    def setup(self):
        """Configura el worker de PDFs"""
        logger.info("🔧 Configurando PDFWorker...")
        self._validate_config()
        
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
        
        logger.info(f"✅ PDFWorker configurado - Intervalo: {self.config.interval}s - Batch: {self.config.batch_size}")
    
    def _validate_config(self):
        """Valida configuración del worker"""
        if self.config.interval <= 0:
            raise ValueError("El intervalo debe ser mayor a 0")
        
        if self.config.batch_size <= 0:
            raise ValueError("El batch_size debe ser mayor a 0")
    
    def start(self):
        """Inicia el bucle de procesamiento de PDFs"""
        self.running = True
        logger.info("🚀 Iniciando PDFWorker...")
        
        try:
            while self.running:
                self._process_pdf_cycle()
                
                if not self.running:
                    break
                    
                logger.info(f"⏳ Esperando {self.config.interval} segundos para siguiente ciclo de PDFs...")
                time.sleep(self.config.interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Interrupción recibida")
        except Exception as e:
            logger.error(f"❌ Error fatal en PDFWorker: {e}")
            raise
        finally:
            self.stop()
    
    def _process_pdf_cycle(self):
        """Ejecuta un ciclo completo de generación de PDFs"""
        logger.info("📋 Iniciando ciclo de generación de PDFs...")
        
        with get_db_session() as db:
            try:
                service = PDFService(db)
                result = service.generar_pdfs_aprobados(batch_size=self.config.batch_size)
                self._log_results(result)
                
            except Exception as e:
                logger.error(f"❌ Error en ciclo de generación de PDFs: {e}")
    
    def _log_results(self, result):
        """Loggea resultados del procesamiento de PDFs"""
        if not result or result.get("total_procesados", 0) == 0:
            logger.info("📭 No hay documentos aprobados para generar PDFs")
            return
        
        total = result.get("total_procesados", 0)
        exitosos = result.get("exitosos", 0)
        errores = result.get("errores", 0)
        
        logger.info(f"📊 PDFs generados en ciclo:")
        logger.info(f"   ✅ Exitosos: {exitosos}/{total}")
        logger.info(f"   ❌ Errores: {errores}/{total}")
        
        # Log detallado de errores si existen
        if result.get("detalles_errores"):
            logger.warning("⚠️ Detalles de errores:")
            for error in result["detalles_errores"]:
                logger.warning(f"   - Doc ID: {error['doc_id']}, CDC: {error['cdc']}, Error: {error['error']}")
    
    def stop(self):
        """Detiene el worker de PDFs"""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo PDFWorker...")
        self.running = False
        logger.info("✅ PDFWorker detenido")
    
    def process_once(self):
        """Ejecuta un solo ciclo de procesamiento de PDFs sin loop"""
        logger.info("⚡ Ejecutando procesamiento único de PDFs...")
        try:
            self._process_pdf_cycle()
        except Exception as e:
            logger.error(f"❌ Error en procesamiento único: {e}")
            raise
