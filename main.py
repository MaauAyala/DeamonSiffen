# main.py (modificado)
import signal
import sys
import threading
from pathlib import Path
from daemon.worker import SifenWorker, WorkerConfig
from daemon.event_worker import EventWorker, EventWorkerConfig  # Nuevo
from config.setting import get_settings
import multiprocessing as mp

 
class DemonSiffenApp:
    def __init__(self):
        self.factura_worker = None
        self.evento_worker = None  # Nuevo
        self.settings = get_settings()
        self.running = False
    
    def _setup_services(self):
        """Inicializa ambos workers"""
        # Worker de facturas
        factura_config = WorkerConfig(
            interval=self.settings.PROCESSING_INTERVAL,
            batch_size=self.settings.BATCH_SIZE,
            max_retries=self.settings.MAX_RETRIES,
            debug=self.settings.DEBUG
        )
        self.factura_worker = SifenWorker(factura_config)
        self.factura_worker.setup()
        
        # Worker de eventos
        evento_config = EventWorkerConfig(
            interval=30,  # Intervalo más corto para eventos
            batch_size=20,
            max_retries=3,
            debug=self.settings.DEBUG
        )
        self.evento_worker = EventWorker(evento_config)
        self.evento_worker.setup()
    
    

    def run_daemon(self):
        """Ejecuta ambos workers usando multiprocessing"""
        if not self.factura_worker or not self.evento_worker:
            self._setup_services()
        
        self.running = True
        
        # Crear procesos para cada worker
        factura_process = mp.Process(
            target=self.factura_worker.start,
            name="FacturaWorker"
        )
        evento_process = mp.Process(
            target=self.evento_worker.start,
            name="EventoWorker"
        )
        
        try:
            # Iniciar ambos procesos
            factura_process.start()
            evento_process.start()
            
            # Esperar a que terminen
            factura_process.join()
            evento_process.join()
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupción recibida")
            factura_process.terminate()
            evento_process.terminate()
        finally:
            self.shutdown()
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de shutdown"""
        print(f"\n🛑 Señal {signum} recibida, iniciando shutdown...")
        self.running = False
        if self.factura_worker:
            self.factura_worker.stop()
        if self.evento_worker:
            self.evento_worker.stop()
    
    def shutdown(self):
        """Limpieza y shutdown"""
        print("🧹 Realizando shutdown...")
        self.running = False
        
        if self.factura_worker:
            self.factura_worker.stop()
        if self.evento_worker:
            self.evento_worker.stop()
        
        print("✅ Shutdown completado")

def main():
    """Punto de entrada principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DemonSiffen - Sistema SIFEN")
    parser.add_argument(
        "--mode", 
        choices=["daemon", "once"], 
        default="daemon",
        help="Modo de ejecución"
    )
    
    args = parser.parse_args()
    
    # Crear aplicación
    app = DemonSiffenApp()
    
    try:
        # Ejecutar según modo
        if args.mode == "daemon":
            print("🚀 Iniciando modo daemon...")
            app.run_daemon()
        elif args.mode == "once":
            print("⚡ Ejecutando procesamiento único...")
            app.run_once()
            
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()