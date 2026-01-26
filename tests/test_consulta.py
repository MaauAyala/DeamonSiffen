from services.consulta_cdc_service import consultaCDC
from core.soap_client import SOAPClient

cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
key_path = r"C:\Users\mauri\clave_privada_desenc.pem"
soap_client = SOAPClient(cert_path, key_path, True)

cdc = "01048496782001001000000322026012611309459320"
id = 1

consultaCDC(client=soap_client,cdc=cdc , numdoc=id)