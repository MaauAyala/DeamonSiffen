import sys, os
import psycopg2
from core.xml_builder import XMLBuilder
from domain.repositories.doc_repo import DocumentoRepo
from core.database import get_db
from core.soap_client import SOAPClient
from core.enviDE import sendDE
from core.consultaRuc import consultaRuc


def test_generar_xml():
    id_test = 91
    output_dir = "tests/output"
    os.makedirs(output_dir, exist_ok=True)

    # crear sesión de BD
    db = next(get_db())

    repo = DocumentoRepo(db)
    doc = repo.getDE(id_test)
    
    if not doc:
        raise ValueError(f"No se encontró el documento con id {id_test}")

    
    print("TIMBRADO ITIDE:", doc.timbrado.itide ,doc.timbrado.ddestide,"Numerodoc: ",doc.dnumdoc)

    xml_bytes = XMLBuilder().build(doc)
    soap_endpoint = "https://sifen.set.gov.py/de/ws/sync/recibe.wsd"  # endpoint SIFEN real
    cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
    key_path = r"C:\Users\mauri\clave_privada_desenc.pem"  # passphrase si tu key está encriptada

    soap_client = SOAPClient(cert_path, key_path,True)
    response = sendDE(soap_client,xml_bytes,doc.dnumdoc)
    print(response)
    #response = consultaRuc(soap_client,"5671440","1")
    #print(response)


    # output_path = os.path.join(output_dir, f"documento_{id_test}.xml")
    # with open(output_path, "wb") as f:
    #     f.write(xml_bytes)

    # print(f"✅ XML generado correctamente en: {output_path}")
    
    
    


