from services.evento_service import EventoService
from core.infraestructure.database.database import get_db

db = next(get_db())
EventoService(db).procesar_eventos_pendientes()