import pprint
from utils.parseXML import parse_sifen_xml
from domain.repositories.doc_repo import DocumentoRepo
from core.infraestructure.database.database import get_db
from domain.models.models import Documento
from utils.buildReport import generar_pdf_factura

db = next(get_db())

def test_parse_xml():
    id = 120
    doc = DocumentoRepo(db=db).getDE(id=id)

    xml= doc.xml_de
    print(doc.cdc_de)
    assert xml is not None

    data = parse_sifen_xml(xml)
    generar_pdf_factura(data)

