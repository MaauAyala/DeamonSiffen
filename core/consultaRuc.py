from core.soap_client import SOAPClient

endpoint = "https://sifen.set.gov.py/de/ws/consultas/consulta-ruc.wsdl"

def consultaRuc(client: SOAPClient,ruc: str, numdoc: int):


    dRuc = ruc.encode("utf-8")
    dId = str(numdoc).zfill(7).encode("utf-8")

    # Construir SOAP sin tocar el rDE firmado
    soap_bytes = (
        b'<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">'
        b'<soap:Header/>'
        b'<soap:Body>'
        b'<rEnviConsRUC xmlns="http://ekuatia.set.gov.py/sifen/xsd">'
        b'<dId>' + dId + b'</dId>'
        b'<dRUCCons>' + dRuc  + b'</dRUCCons>'
        b'</rEnviConsRUC>'
        b'</soap:Body>'
        b'</soap:Envelope>'
    )
    

    return client.send(endpoint,soap_bytes)
