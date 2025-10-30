import requests

class SOAPClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def send(self, xml: bytes):
        envelope = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                {xml.decode()}
            </soapenv:Body>
        </soapenv:Envelope>
        """
        headers = {"Content-Type": "text/xml; charset=utf-8"}
        response = requests.post(self.endpoint, data=envelope, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
