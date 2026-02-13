"""
Worker de DemonSiffen - Proceso background para procesamiento de facturas
"""

import time
import logging
from typing import Optional
from dataclasses import dataclass

from core.infraestructure.database.database import get_db_session
from services.factura_service import FacturaService

logger = logging.getLogger(__name__)

@dataclass
class WorkerConfig:
    """Configuración del worker"""
    interval: int = 60
    batch_size: int = 50
    max_retries: int = 3
    debug: bool = False

class SifenWorker:
    """Worker para procesamiento automático de facturas SIFEN"""
    
    def __init__(self, config: Optional[WorkerConfig] = None):
        self.config = config or WorkerConfig()
        self.running = False
        self._service = None
        
    def setup(self):
        """Configura el worker con los servicios necesarios"""
        logger.info("🔧 Configurando SifenWorker...")
        
        # Validar configuración
        self._validate_config()
        
        # Inicializar logger según configuración
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
        
        logger.info(f"✅ Worker configurado - Intervalo: {self.config.interval}s")
    
    def _validate_config(self):
        """Valida que la configuración sea correcta"""
        if self.config.interval <= 0:
            raise ValueError("El intervalo debe ser mayor a 0")
        
        if self.config.batch_size <= 0:
            raise ValueError("El batch_size debe ser mayor a 0")
    
    def start(self):
        """Inicia el bucle de procesamiento"""
        self.running = True
        logger.info("🚀 Iniciando SifenWorker...")
        
        try:
            while self.running:
                self._process_cycle()
                
                if not self.running:
                    break
                    
                logger.info(f"⏳ Esperando {self.config.interval} segundos...")
                time.sleep(self.config.interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Interrupción recibida")
        except Exception as e:
            logger.error(f"❌ Error fatal en worker: {e}")
            raise
        finally:
            self.stop()
    
    def _process_cycle(self):
        """Ejecuta un ciclo completo de procesamiento"""
        logger.info("📋 Iniciando ciclo de procesamiento...")
        
        with get_db_session() as db:
            try:
                # Crear servicio con configuración actual
                service = FacturaService(db)
                
                # Procesar documentos pendientes
                result = service.procesar_pendientes(batch_size=self.config.batch_size)
                
                # Log de resultados
                self._log_results(result)
                
            except Exception as e:
                logger.error(f"❌ Error en ciclo de procesamiento: {e}")
                # Aquí podrías implementar retry logic
    
    def _log_results(self, result):
        """Loggea los resultados del procesamiento"""
        if not result:
            logger.info("📭 No hay documentos pendientes")
            return
        
        total_procesados = result.get("total_procesados", 0)
        lotes = result.get("lotes", [])
        
        logger.info(f"✅ Procesamiento completado:")
        logger.info(f"   📊 Total documentos: {total_procesados}")
        logger.info(f"   📦 Lotes procesados: {len(lotes)}")
        
        for i, lote in enumerate(lotes, 1):
            logger.info(f"   Lote {i}: {lote}")
    
    def stop(self):
        """Detiene el worker de manera graceful"""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo SifenWorker...")
        self.running = False
        
        # Limpiar recursos si es necesario
        if self._service:
            self._service = None
        
        logger.info("✅ Worker detenido")
    
    def process_once(self):
        """Ejecuta un solo ciclo de procesamiento"""
        logger.info("⚡ Ejecutando procesamiento único...")
        
        try:
            self._process_cycle()
            logger.info("✅ Procesamiento único completado")
        except Exception as e:
            logger.error(f"❌ Error en procesamiento único: {e}")
            raise
    
    def get_status(self) -> dict:
        """Retorna el estado actual del worker"""
        return {
            "running": self.running,
            "config": {
                "interval": self.config.interval,
                "batch_size": self.config.batch_size,
                "max_retries": self.config.max_retries,
                "debug": self.config.debug
            }
        }