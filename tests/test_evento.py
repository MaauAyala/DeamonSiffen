import sys
from pathlib import Path

# Agregar el path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from core.infraestructure.use_cases import enviEv
from core.infraestructure.xml.eventBuilder import eventBuilder
from domain.models.models import Evento
from core.infraestructure.soap.soap_client import SOAPClient
builder = eventBuilder()

evento = Evento(
    id=2,  
    dverfor="150",  
    cdc_dte="01048496782001001000000522026021011327530839", 
    mototeve="Prueba de Evento", 
    dnumtim="18583670", 
    dest="001", 
    tipeve=1, 
    itide=1, 
    de_id=99
)



xml = builder.build(evento)
xml_bytes = xml.encode('utf-8') if isinstance(xml, str) else xml
with open("tests/output/xmlEvento.xml", "wb") as f:
    f.write(xml.encode('utf-8'))
    
    
    endpoint = "https://sifen-test.set.gov.py/de/ws/eventos/evento.wsdl?wsdl"
    cert_path = r"C:\Users\mauri\credenciales\certificado.pem"
    key_path = r"C:\Users\mauri\clave_privada_desenc.pem"
    soap_client = SOAPClient(cert_path, key_path, True)
    
    response = enviEv.sendEvento(soap_client,xml_bytes,1)

    print(response
          )