# daemon/event_worker.py
import time
import logging
from typing import Optional
from dataclasses import dataclass

from core.infraestructure.database.database import get_db_session
from services.estados_service import EstadosService 

logger = logging.getLogger(__name__)

@dataclass
class EstadosWorkerConfig:
    """Configuración del worker de estados de factura"""
    interval: int = 30  # Intervalo más corto para eventos
    batch_size: int = 20
    max_retries: int = 3
    debug: bool = False
    estados: str = "RECIBIDO_SIFEN"

class EstadosWorker:
    """Worker para consultas automáticas de estados de factura SIFEN"""
    
    def __init__(self, config: Optional[EstadosWorkerConfig] = None):
        self.config = config or EstadosWorkerConfig()
        self.running = False
        
    def setup(self):
        """Configura el worker de estados"""
        logger.info("🔧 Configurando EstadosWorker...")
        self._validate_config()
        
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
        
        logger.info(f"✅ EstadosWorker configurado - Intervalo: {self.config.interval}s")
    
    def _validate_config(self):
        """Valida configuración"""
        if self.config.interval <= 0:
            raise ValueError("El intervalo debe ser mayor a 0")
    
    def start(self):
        """Inicia el bucle de procesamiento de facturas"""
        self.running = True
        logger.info("🚀 Iniciando EstadosWorker...")
        
        try:
            while self.running:
                self._process_lotes_cycle()
                
                if not self.running:
                    break
                    
                logger.info(f"⏳ Esperando {self.config.interval} segundos...")
                time.sleep(self.config.interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Interrupción recibida")
        except Exception as e:
            logger.error(f"❌ Error fatal en EventWorker: {e}")
            raise
        finally:
            self.stop()
    
    def _process_lotes_cycle(self):
        """Ejecuta un ciclo de procesamiento de facturas por lote"""
        logger.info("📋 Iniciando ciclo de procesamiento de lotes...")
        
        with get_db_session() as db:
            try:
                service = EstadosService(db,self.config.batch_size)
                result = service.processLotes(self.config.estados)
                self._log_results(result)
                
            except Exception as e:
                logger.error(f"❌ Error en ciclo de estados: {e}")
    
    def _log_results(self, result):
        """Loggea resultados del procesamiento de estados"""
        if not result:
            logger.info("📭 No hay estados pendientes")
            return
        
        total_procesados = result.get("total_procesados", 0)
        logger.info(f"✅ Documentos procesados: {total_procesados}")
    
    def stop(self):
        """Detiene el worker de Estados"""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo EstadosWorker...")
        self.running = False
        logger.info("✅ EstadosWorker detenido")
    
    def process_once(self):
        """Ejecuta un solo ciclo de procesamiento de estados"""
        logger.info("⚡ Ejecutando procesamiento único de estados...")
        try:
            self._process_lotes_cycle()
            logger.info("✅ Procesamiento único de estados completado")
        except Exception as e:
            logger.error(f"❌ Error en procesamiento único de estados: {e}")
            raise