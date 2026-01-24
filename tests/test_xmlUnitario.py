import sys, os
import psycopg2
from core.xml_builder import XMLBuilder
from domain.repositories.doc_repo import DocumentoRepo
from core.database import get_db
from core.soap_client import SOAPClient
from core.enviDE import sendDE
from core.consultaRuc import consultaRuc
from services.response_service import guardarResponse
from services.lote_service import LoteService


def test_generar_xml():
    id_test = 94
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
    cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
    key_path = r"C:\Users\mauri\clave_privada_desenc.pem"  # passphrase si tu key está encriptada
    print(xml_bytes.decode("utf-8"))
    soap_client = SOAPClient(cert_path, key_path,True)
    response = LoteService.rEnvioLote(soap_client,xml = xml_bytes ,id=1)
    print(response)
    guardarResponse(response.text,db,id_test)
    #response = consultaRuc(soap_client,"5671440","1")
    #print(response)


    # output_path = os.path.join(output_dir, f"documento_{id_test}.xml")
    # with open(output_path, "wb") as f:
    #     f.write(xml_bytes)

    # print(f"✅ XML generado correctamente en: {output_path}")
    
    
    


