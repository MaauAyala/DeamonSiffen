import os
import logging
import requests
from requests import Session, Request

class SOAPClient:
    def __init__(self, cert_path: str, key_path: str, debug: bool = True):
        self.cert = (cert_path, key_path)
        self.debug = debug
        self.session = Session()
        self.logger = logging.getLogger(__name__)

        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def send(self, endpoint: str, soap_bytes: bytes, timeout: int = 45):
        headers = {
            "Content-Type": "application/soap+xml; charset=UTF-8",
            "Accept": "application/soap+xml, application/xml, text/xml",
            "User-Agent": "python-sifen-client/1.0",
        }

        req = Request("POST", endpoint, data=soap_bytes, headers=headers)
        pre = self.session.prepare_request(req)

        if self.debug:
            os.makedirs("tests/output", exist_ok=True)
            with open("tests/output/last_soap_sent.xml", "wb") as f:
                f.write(soap_bytes)

        resp = self.session.send(pre, cert=self.cert, timeout=timeout)

        if self.debug:
            with open("tests/output/last_soap_response.xml", "wb") as f:
                f.write(resp.content)

            print("\n===== HTTP STATUS =====")
            print(resp.status_code)
            print("\n===== SOAP RESPONSE =====")
            try:
                print(resp.content.decode("utf-8"))
            except Exception:
                print(resp.content.decode("latin1", errors="replace"))

        resp.raise_for_status()
        return resp


    # def sendLote(self, xml_bytes: bytes, numlote):
    #     xml_b64 = base64.b64encode(xml_bytes).decode()
    #     numdocfill = str(numlote).zfill(8)
    #     envelope = f"""
    #     <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    #         <soap:Header>
    #             <deHeaderMsg xmlns="https://www.sifen.gov.py/De/wsdl/siRecepLoteDe"/>
    #         </soap:Header>
    #         <soap:Body>
    #             <rEnvioLote xmlns="http://ekuatia.set.gov.py/sifen/xsd">
    #                 <dId>{numdocfill}</dId>
    #                 <xDE>{xml_b64}</xDE>
    #                 </rEnvioLote>
    #         </soap:Body>
    #     </soap:Envelope>
    #     """

    #     headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
    #     try:
    #         os.makedirs("tests/output", exist_ok=True)
    #         with open("tests/output/last_soap.xml", "w", encoding="utf-8") as f:
    #             f.write(envelope)
    #         if self.debug: self.logger.debug("Saved last_soap.xml")
    #     except Exception as e:
    #         if self.debug: self.logger.exception("No se pudo guardar last_soap.xml: %s", e)

    #     response = requests.post(
    #         self.endpoint,
    #         data=envelope.encode("utf-8"),
    #         headers=headers,
    #         cert=self.cert,
    #         timeout=30
    #     )

    #     if response.status_code >= 400:
    #         try:
    #             with open("tests/output/last_soap_response.xml", "w", encoding="utf-8") as f:
    #                 f.write(response.text)
    #             if self.debug: self.logger.debug("Saved last_soap_response.xml")
    #         except Exception:
    #             if self.debug: self.logger.exception("No se pudo guardar la respuesta del SOAP.")

    #         if self.debug:
    #             self.logger.debug("=== RESPUESTA DEL SERVIDOR (ERROR) ===")
    #             self.logger.debug(response.text[:2000])
    #             self.logger.debug("======================================")

    #     response.raise_for_status()
    #     return response.text
    
    # def consultaRuc(self, ruc, numdoc: int):
    #     numdocfill = str(numdoc).zfill(7)

    #     envelope = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    #     <soap:Envelope xmlns:soap='http://www.w3.org/2003/05/soap-envelope'>
    #     <soap:Header/>
    #     <soap:Body>
    #     <rEnviConsRUC xmlns='http://ekuatia.set.gov.py/sifen/xsd'>
    #     <dId>{numdocfill}</dId>
    #     <dRUCCons>{ruc}</dRUCCons>
    #     </rEnviConsRUC>
    #     </soap:Body>
    #     </soap:Envelope>"""

    #     os.makedirs("tests/output", exist_ok=True)
    #     with open("tests/output/last_soap_individual.xml", "w", encoding="utf-8") as f:
    #         f.write(envelope)

    #     headers = {"Content-Type": "application/soap+xml; charset=utf-8"}

    #     response = requests.post(
    #         self.endpoint,
    #         data=envelope.encode("utf-8"),
    #         headers=headers,
    #         cert=self.cert,
    #         timeout=45
    #     )

    #     if response.status_code >= 400:
    #         if self.debug: self.logger.debug("🔴 Error HTTP %s", response.status_code)
    #         try:
    #             with open("tests/output/last_soap_response.xml", "w", encoding="utf-8") as f:
    #                 f.write(response.text)
    #         except Exception:
    #             if self.debug: self.logger.exception("No se pudo guardar la respuesta del SOAP.")

    #     return response






    # def enviar_evento_cancelacion(
    #     endpoint: str,
    #     cdc: str,
    #     motivo: str,
    #     idevento: int = 1,
    #     timeout: int = 30
    # ):
    #     NS_SOAP = "http://www.w3.org/2003/05/soap-envelope"
    #     NS_SIFEN = "http://ekuatia.set.gov.py/sifen/xsd"
    #     NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"

    #     ET.register_namespace("soap", NS_SOAP)

    #     # ===== SOAP ENVELOPE =====
    #     envelope = ET.Element(f"{{{NS_SOAP}}}Envelope")
    #     ET.SubElement(envelope, f"{{{NS_SOAP}}}Header")
    #     body = ET.SubElement(envelope, f"{{{NS_SOAP}}}Body")

    #     # ===== EVENTO CANCELACIÓN =====
    #     gGroupGesEve = ET.SubElement(
    #         body,
    #         f"{{{NS_SIFEN}}}gGroupGesEve",
    #         {
    #             f"{{{NS_XSI}}}schemaLocation":
    #                 f"{NS_SIFEN} siRecepEvento_v150.xsd"
    #         }
    #     )

    #     rGesEve = ET.SubElement(gGroupGesEve, f"{{{NS_SIFEN}}}rGesEve")
    #     rEve = ET.SubElement(rGesEve, f"{{{NS_SIFEN}}}rEve", {"Id": str(idevento)})

    #     ET.SubElement(rEve, f"{{{NS_SIFEN}}}dFecFirma").text = \
    #         datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    #     ET.SubElement(rEve, f"{{{NS_SIFEN}}}dVerFor").text = "150"

    #     gGroupTiEvt = ET.SubElement(rEve, f"{{{NS_SIFEN}}}gGroupTiEvt")
    #     rGeVeCan = ET.SubElement(gGroupTiEvt, f"{{{NS_SIFEN}}}rGeVeCan")

    #     ET.SubElement(rGeVeCan, f"{{{NS_SIFEN}}}Id").text = cdc
    #     ET.SubElement(rGeVeCan, f"{{{NS_SIFEN}}}mOtEve").text = motivo

    #     # ===== XML FINAL =====
    #     xml_bytes = ET.tostring(envelope, encoding="utf-8", xml_declaration=True)

    #     print("\n===== SOAP REQUEST =====")
    #     print(xml_bytes.decode("utf-8"))

    #     headers = {
    #         "Content-Type": "application/soap+xml; charset=utf-8"
    #     }

    #     response = requests.post(
    #         endpoint,
    #         data=xml_bytes,
    #         headers=headers,
    #         timeout=timeout
    #     )

    #     print("\n===== HTTP STATUS =====")
    #     print(response.status_code)

    #     print("\n===== SOAP RESPONSE =====")
    #     print(response.text)

    #     return response
