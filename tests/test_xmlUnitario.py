import sys, os
import psycopg2
from core.xml_builder import XMLBuilder
from domain.repositories.doc_repo import DocumentoRepo
from core.database import get_db

def test_generar_xml():
    id_test = 49
    output_dir = "tests/output"
    os.makedirs(output_dir, exist_ok=True)

    # crear sesión de BD
    db = next(get_db())

    repo = DocumentoRepo(db)
    doc = repo.getDE(id_test)

    if not doc:
        raise ValueError(f"No se encontró el documento con id {id_test}")

    xml_bytes = XMLBuilder().build(doc)



    # guardar archivo
    output_path = os.path.join(output_dir, f"documento_{id_test}.xml")
    with open(output_path, "wb") as f:
        f.write(xml_bytes)

    print(f"✅ XML generado correctamente en: {output_path}")
