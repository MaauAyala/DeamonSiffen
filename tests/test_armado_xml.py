import sys, os
import psycopg2
from services.lote_service import LoteService
from core.infraestructure.xml.xml_builder import XMLBuilder
from domain.repositories.doc_repo import DocumentoRepo
from core.infraestructure.database import get_db

def test_generar_xml():
    id_test = 213
    output_dir = "tests/output"
    os.makedirs(output_dir, exist_ok=True)

    # crear sesión de BD
    db = next(get_db())

    repo = DocumentoRepo(db)
    documentos = repo.getPendiente()

    if not documentos:
        raise ValueError(f"No se encontró el documento con id {id_test}")

    # generar el XML
    xml_lote =[]
    for doc in documentos:
        xml_de = XMLBuilder().build(doc)
        xml_lote.append(xml_de)
    
    xml_bytes,nuevo_id = LoteService(db).crearLotes(xml_lote)

    # guardar archivo
    output_path = os.path.join(output_dir, f"documento_{id_test}.xml")
    with open(output_path, "wb") as f:
        f.write(xml_bytes)

    print(f"✅ XML generado correctamente en: {output_path}")
