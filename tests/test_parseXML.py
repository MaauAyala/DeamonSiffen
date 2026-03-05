from utils.parseResponseLote import parse_lote_response
from domain.repositories.lote_repo import LoteRepository
from core.infraestructure.database.database import get_db
from domain.models.models import Lote
from services.consulta_lote_service import consultaLote
from core.infraestructure.soap.soap_client import SOAPClient
from domain.repositories.doc_repo import DocumentoRepo

def test_xmlParse():
    db = next(get_db())
    cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
    key_path = r"C:\Users\mauri\clave_privada_desenc.pem"
    soap_client = SOAPClient(cert_path, key_path, True)
    idlote = 17
    loterepo =LoteRepository(db)

    lote : Lote =loterepo.obtener_lote_por_id(idlote)

    response =consultaLote(soap_client,1,lote.nro_lote_sifen)

    data =parse_lote_response(response.content)
    docrepo =DocumentoRepo(db)
    docrepo.loadEstRes(data)
