from domain.repositories.doc_repo import DocumentoRepo
from core.database import get_db

def test_getPendientes():
    db = next(get_db())
    
    repo = DocumentoRepo(db)
    
    pendientes = repo.getPendiente()
    
    for de in pendientes:
        print(de.id)
