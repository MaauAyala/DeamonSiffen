from services.consulta_lote_service import consultaLote
from core.infraestructure.soap.soap_client import SOAPClient
cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
key_path = r"C:\Users\mauri\clave_privada_desenc.pem"
s =SOAPClient(cert_path, key_path, True)

idC = 1
numL =5586437372040580010

consultaLote(s,idC,numL)