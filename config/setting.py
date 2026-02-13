"""
Configuración centralizada de DemonSiffen
Carga variables de entorno y proporciona valores por defecto
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Clase de configuración centralizada"""
    
    # Database
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "7606")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "Sifen_API")
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    
    # SIFEN Endpoints
    EVENTO_ENDPOINT: str = os.getenv("EVENTO_ENDPOINT", "https://sifen.set.gov.py/de/ws/async/envi-de.wsdl")
    LOTE_ENDPOINT: str = os.getenv("LOTE_ENDPOINT", "https://sifen.set.gov.py/de/ws/async/recibe-lote.wsdl")
    CONSULTA_ENDPOINT: str = os.getenv("CONSULTA_ENDPOINT", "https://sifen.set.gov.py/de/ws/consultas/consulta.wsdl")
    CONSULTA_RUC_ENDPOINT: str = os.getenv("CONSULTA_RUC_ENDPOINT", "https://sifen.set.gov.py/de/ws/consultas/consulta-ruc.wsdl")
    CONSULTA_LOTE_ENDPOINT: str = os.getenv("CONSULTA_LOTE_ENDPOINT", "https://sifen.set.gov.py/de/ws/consultas/consulta-lote.wsdl")
    
    # Certificados
    CERT_PATH: str = os.getenv("CERT_PATH", r"C:\Users\mauri\credenciales\certificado.pem")
    KEY_PATH: str = os.getenv("KEY_PATH", r"C:\Users\mauri\clave_privada_desenc.pem")
    
    # QR Settings
    URL_QR: str = os.getenv("URL_QR", "https://ekuatia.set.gov.py/consultas/qr?")
    CSC: str = os.getenv("CSC", "0001")  # Test: 0001, Producción: 0003
    
    # Processing
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "50"))
    PROCESSING_INTERVAL: int = int(os.getenv("PROCESSING_INTERVAL", "60"))  # segundos
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/demon_siffen.log")
    
    # Debug
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que la configuración sea correcta"""
        required = [
            "DATABASE_URL",
            "CERT_PATH", 
            "KEY_PATH"
        ]
        
        for attr in required:
            value = getattr(cls, attr)
            if not value:
                raise ValueError(f"Configuración requerida faltante: {attr}")
        
        # Validar que los certificados existan
        if not os.path.exists(cls.CERT_PATH):
            raise FileNotFoundError(f"Certificado no encontrado: {cls.CERT_PATH}")
        
        if not os.path.exists(cls.KEY_PATH):
            raise FileNotFoundError(f"Llave privada no encontrada: {cls.KEY_PATH}")
        
        return True
    
    @classmethod
    def get_summary(cls) -> dict:
        """Retorna resumen de configuración (sin datos sensibles)"""
        return {
            "database": {
                "host": cls.DB_HOST,
                "name": cls.DB_NAME,
                "user": cls.DB_USER
            },
            "endpoints": {
                "evento": cls.EVENTO_ENDPOINT,
                "lote": cls.LOTE_ENDPOINT,
                "consulta": cls.CONSULTA_ENDPOINT
            },
            "processing": {
                "batch_size": cls.BATCH_SIZE,
                "interval": cls.PROCESSING_INTERVAL,
                "max_retries": cls.MAX_RETRIES
            },
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL
        }

# Instancia global de configuración
settings = Settings()

# Variables legacy para compatibilidad (las que ya usabas)
SOAP_ENDPOINT = settings.EVENTO_ENDPOINT
INTERVAL = settings.PROCESSING_INTERVAL
limite = settings.BATCH_SIZE

def get_settings() -> Settings:
    """Retorna la instancia de configuración"""
    return settings

# Validación al importar
try:
    settings.validate()
    print(f"✅ Configuración validada - Debug: {settings.DEBUG}")
except Exception as e:
    print(f"❌ Error en configuración: {e}")
    raise