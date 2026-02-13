import os
from dotenv import load_dotenv
from core.infraestructure.soap.soap_client import SOAPClient

load_dotenv()

endpoint =os.environ["EVENTO_ENDPOINT"]

def sendEvento(client: SOAPClient, xmlEve: bytes, numdoc: int):
    if not isinstance(xmlEve, (bytes, bytearray)):
        raise TypeError("rde_xml_bytes debe ser bytes")

    # Quitar BOM si existe
    xmlEveByte = xmlEve
    if xmlEve.startswith(b'\xef\xbb\xbf'):
        xmlEveByte = xmlEve[3:]
    
    dId = str(numdoc).encode("utf-8")

    # Construir SOAP sin tocar el rDE firmado

    soap_bytes = (
        b'<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:xsd="http://ekuatia.set.gov.py/sifen/xsd">'
        b'<soap:Header/>'
        b'<soap:Body>'
        b'<xsd:rEnviEventoDe>'
        b'<xsd:dId>' + dId + b'</xsd:dId>'
        b'<xsd:dEvReg>' + xmlEveByte + b'</xsd:dEvReg>'
        b'</xsd:rEnviEventoDe>'
        b'</soap:Body>'
        b'</soap:Envelope>'
    )

    return client.send(endpoint, soap_bytes)


    # soap_bytes = (
    #     b'<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:xsd="http://ekuatia.set.gov.py/sifen/xsd">'
    #     b'<soap:Header/>'
    #     b'<soap:Body>'
    #     b'<xsd:rEnviEventoDe>'
    #     b'<xsd:dId>' + dId + b'</xsd:dId>'
    #     b'<xsd:dEvReg>' + xmlEveByte + b'</xsd:dEvReg>'
    #     b'</xsd:rEnviEventoDe>'
    #     b'</soap:Body>'
    #     b'</soap:Envelope>'
    # )