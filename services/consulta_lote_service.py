endpoint  = "https://sifen.set.gov.py/de/ws/consultas/consulta-lote.wsdl?"

from core.infraestructure.soap.soap_client import SOAPClient



def consultaLote(client: SOAPClient, idConsulta: str, numeroLote: int):

        soap = f'''<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
    <soap:Header/>
    <soap:Body>
        <rEnviConsLoteDe xmlns="http://ekuatia.set.gov.py/sifen/xsd">
        <dId>{idConsulta}</dId>
        <dProtConsLote>{numeroLote}</dProtConsLote>
        </rEnviConsLoteDe>
    </soap:Body>
    </soap:Envelope>
    '''.encode("utf-8")
    

        return client.send(endpoint,soap)
