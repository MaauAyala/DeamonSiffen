# main.py (modificado)
import signal
import sys
import threading
from pathlib import Path
from daemon.estados_worker import EstadosWorker , EstadosWorkerConfig
from daemon.worker import SifenWorker, WorkerConfig
from daemon.event_worker import EventWorker, EventWorkerConfig  # Nuevo
from daemon.pdf_worker import PDFWorker, PDFWorkerConfig  # Nuevo worker de PDFs
from config.setting import get_settings
import multiprocessing as mp

 
class DemonSiffenApp:
    def __init__(self):
        self.factura_worker = None
        self.evento_worker = None  
        self.estados_worker = None
        self.pdf_worker = None  # Nuevo worker de PDFs
        self.settings = get_settings()
        self.running = False
    
    def _setup_services(self):
        """Inicializa  workers"""
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
    
        estados_config = EstadosWorkerConfig(
            interval=30,  # Intervalo más corto para eventos
            batch_size=20,
            max_retries=3,
            debug=self.settings.DEBUG,
            estados="RECIBIDO_SIFEN"
        )
        self.estados_worker = EstadosWorker(estados_config)
        self.estados_worker.setup()
        
        # Worker de PDFs para documentos aprobados
        pdf_config = PDFWorkerConfig(
            interval=120,  # Intervalo de 2 minutos
            batch_size=50,
            max_retries=3,
            debug=self.settings.DEBUG
        )
        self.pdf_worker = PDFWorker(pdf_config)
        self.pdf_worker.setup()
    
    

    def run_daemon(self):
        """Ejecuta todos los workers usando multiprocessing"""
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
        estados_process = mp.Process(
            target=self.estados_worker.start,
            name="EstadosWorker"
        )
        pdf_process = mp.Process(
            target=self.pdf_worker.start,
            name="PDFWorker"
        )
        try:
            # Iniciar todos los procesos
            factura_process.start()
            evento_process.start()
            estados_process.start()
            pdf_process.start()
            
            # Esperar a que terminen
            factura_process.join()
            evento_process.join()
            estados_process.join()
            pdf_process.join()
            
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupción recibida")
            factura_process.terminate()
            evento_process.terminate()
            estados_process.terminate()
            pdf_process.terminate()
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
        if self.estados_worker:
            self.estados_worker.stop()
        if self.pdf_worker:
            self.pdf_worker.stop()
    
    def shutdown(self):
        """Limpieza y shutdown"""
        print("🧹 Realizando shutdown...")
        self.running = False
        
        if self.factura_worker:
            self.factura_worker.stop()
        if self.evento_worker:
            self.evento_worker.stop()
        if self.estados_worker:
            self.estados_worker.stop()
        if self.pdf_worker:
            self.pdf_worker.stop()
        
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