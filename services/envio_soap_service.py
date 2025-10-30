from core.soap_client import SOAPClient
from domain.repositories.lote_repo import LoteRepo

class EnvioSOAPService:
    def __init__(self, db, soap_endpoint):
        self.db = db
        self.soap = SOAPClient(soap_endpoint)
        self.repo_lote = LoteRepo(db)

    def enviar_lote(self, lote):
        

        
        respuesta_xml = self.soap.send(lote)

        
        dCodRes, dMsgRes, dProtConsLote = self._parse_respuesta(respuesta_xml)

        
        self.repo_lote.actualizar_estado(
            lote.id,
            estado="ENVIADO",
            xml_respuesta=respuesta_xml,
            cod_res=dCodRes,
            msg_res=dMsgRes,
            protocolo=dProtConsLote,
        )

        return respuesta_xml

    def _parse_respuesta(self, xml_respuesta):
        """
        Extrae los campos clave de la respuesta SOAP.
        """
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_respuesta)
        ns = {"ns": "http://ekuatia.set.gov.py/sifen/xsd"}

        dCodRes = root.findtext(".//ns:dCodRes", namespaces=ns)
        dMsgRes = root.findtext(".//ns:dMsgRes", namespaces=ns)
        dProtConsLote = root.findtext(".//ns:dProtConsLote", namespaces=ns)

        return dCodRes, dMsgRes, dProtConsLote
