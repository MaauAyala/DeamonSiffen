import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / f'sifen_{datetime.now().strftime("%Y%m%d")}.log'

# Crear directorio de logs si no existe
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str = 'sifen') -> logging.Logger:
    """
    Configura y devuelve un logger con el nombre especificado.
    
    Args:
        name (str): Nombre del logger. Por defecto 'sifen'.
        
    Returns:
        logging.Logger: Instancia del logger configurado.
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Evitar que los logs se propaguen al logger raíz
    logger.propagate = False
    
    # Si ya tiene handlers, no agregar más
    if logger.handlers:
        return logger
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Handler para archivo con rotación (10MB por archivo, manteniendo 5 archivos de respaldo)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Obtiene un logger configurado.
    
    Args:
        name (str, opcional): Nombre del logger. Si no se especifica, 
                            se usa el nombre del módulo que lo llama.
    
    Returns:
        logging.Logger: Instancia del logger configurado.
    """
    if name is None:
        import inspect
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        name = mod.__name__ if mod else 'root'
    
    return setup_logger(name)

# Logger por defecto
logger = get_logger('sifen')

# Ejemplo de uso:
if __name__ == "__main__":
    logger.debug("Este es un mensaje de depuración")
    logger.info("Este es un mensaje informativo")
    logger.warning("Esta es una advertencia")
    logger.error("Este es un mensaje de error")
    logger.critical("¡Este es un mensaje crítico!")