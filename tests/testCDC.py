from core.infraestructure.database.database import get_db
from domain.repositories.doc_repo import DocumentoRepo
from utils.buildCDC import buildCDC


def test_generar_xml():
    id_test = 99


    # crear sesión de BD
    db = next(get_db())

    repo = DocumentoRepo(db)
    doc = repo.getDE(id_test)
    
    
    CDC, partes = buildCDC(db,doc)
    print(CDC)