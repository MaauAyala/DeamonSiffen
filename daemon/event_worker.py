# daemon/event_worker.py
import time
import logging
from typing import Optional
from dataclasses import dataclass

from core.infraestructure.database.database import get_db_session
from services.evento_service import EventoService  # Necesitarás crear este servicio

logger = logging.getLogger(__name__)

@dataclass
class EventWorkerConfig:
    """Configuración del worker de eventos"""
    interval: int = 30  # Intervalo más corto para eventos
    batch_size: int = 20
    max_retries: int = 3
    debug: bool = False

class EventWorker:
    """Worker para procesamiento automático de eventos SIFEN"""
    
    def __init__(self, config: Optional[EventWorkerConfig] = None):
        self.config = config or EventWorkerConfig()
        self.running = False
        
    def setup(self):
        """Configura el worker de eventos"""
        logger.info("🔧 Configurando EventWorker...")
        self._validate_config()
        
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
        
        logger.info(f"✅ EventWorker configurado - Intervalo: {self.config.interval}s")
    
    def _validate_config(self):
        """Valida configuración"""
        if self.config.interval <= 0:
            raise ValueError("El intervalo debe ser mayor a 0")
    
    def start(self):
        """Inicia el bucle de procesamiento de eventos"""
        self.running = True
        logger.info("🚀 Iniciando EventWorker...")
        
        try:
            while self.running:
                self._process_event_cycle()
                
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
    
    def _process_event_cycle(self):
        """Ejecuta un ciclo de procesamiento de eventos"""
        logger.info("📋 Iniciando ciclo de procesamiento de eventos...")
        
        with get_db_session() as db:
            try:
                service = EventoService(db)
                result = service.procesar_eventos_pendientes(batch_size=self.config.batch_size)
                self._log_results(result)
                
            except Exception as e:
                logger.error(f"❌ Error en ciclo de eventos: {e}")
    
    def _log_results(self, result):
        """Loggea resultados del procesamiento de eventos"""
        if not result:
            logger.info("📭 No hay eventos pendientes")
            return
        
        total_procesados = result.get("total_procesados", 0)
        logger.info(f"✅ Eventos procesados: {total_procesados}")
    
    def stop(self):
        """Detiene el worker de eventos"""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo EventWorker...")
        self.running = False
        logger.info("✅ EventWorker detenido")
    
    def process_once(self):
        """Ejecuta un solo ciclo de procesamiento de eventos"""
        logger.info("⚡ Ejecutando procesamiento único de eventos...")
        try:
            self._process_event_cycle()
            logger.info("✅ Procesamiento único de eventos completado")
        except Exception as e:
            logger.error(f"❌ Error en procesamiento único de eventos: {e}")
            raise