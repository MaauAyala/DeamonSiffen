import os
from dotenv import load_dotenv
from core.soap_client import SOAPClient

load_dotenv()

endpoint =os.environ["CSC"]

def sendEvento(client: SOAPClient,rde_xml_bytes: bytes, numdoc: int):

    if not isinstance(rde_xml_bytes, (bytes, bytearray)):
        raise TypeError("rde_xml_bytes debe ser bytes")

    # Quitar BOM si existe
    if rde_xml_bytes.startswith(b'\xef\xbb\xbf'):
        rde_xml_bytes = rde_xml_bytes[3:]

    dId = str(numdoc).zfill(7).encode("utf-8")

    # Construir SOAP sin tocar el rDE firmado
    soap_bytes = (
        b'<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">'
        b'<soap:Header/>'
        b'<soap:Body>'
        b'<rEnviDe xmlns="http://ekuatia.set.gov.py/sifen/xsd">'
        b'<dId>' + dId + b'</dId>'
        b'<xDE>' + rde_xml_bytes + b'</xDE>'
        b'</rEnviDe>'
        b'</soap:Body>'
        b'</soap:Envelope>'
    )

    return client.send(endpoint,soap_bytes)
