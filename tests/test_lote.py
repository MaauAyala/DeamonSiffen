import sys, os
import psycopg2
from core.xml_builder import XMLBuilder
from domain.repositories.doc_repo import DocumentoRepo
from core.database import get_db
from core.soap_client import SOAPClient
from core.enviDE import sendDE
from core.consultaRuc import consultaRuc
from services.response_service import getResponse
from services.lote_service import LoteService
from core.xml_builder_lote import XMLBuilderLote


def test_generar_xml():
    id_test = 96
    #id_2 = 96
    output_dir = "tests/output"
    os.makedirs(output_dir, exist_ok=True)

    # crear sesión de BD
    db = next(get_db())

    repo = DocumentoRepo(db)
    doc = repo.getDE(id_test)
    #doc2 = repo.getDE(id_2)
    
    if not doc:
        raise ValueError(f"No se encontró el documento con id {id_test}")

    print("TIMBRADO ITIDE:", doc.timbrado.itide ,doc.timbrado.ddestide,"Numerodoc: ",doc.dnumdoc)

    xml_bytes = XMLBuilder().build(doc)
    #xml2 = XMLBuilder().build(doc2)
    rdlist=[xml_bytes]  
    builder = XMLBuilderLote()
    rLoteDE =builder.build_lote(rde_list =rdlist)
    # Guardar el XML individual
    with open("tests/output/onlyxml.xml", "wb") as f:
        f.write(rLoteDE)
    
    # Configurar cliente SOAP
    cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
    key_path = r"C:\Users\mauri\clave_privada_desenc.pem"
    soap_client = SOAPClient(cert_path, key_path, True)
    
    
    # Enviar como lote
    print("\n=== ENVIANDO COMO LOTE ===")
    response = LoteService.rEnvioLote(soap_client, rLoteDE, id=1)
    
    #getResponse(response.text,db,94)
    
    print(f"\n=== RESPUESTA COMPLETA ===")
    print(f"Status Code: {response.status_code}")