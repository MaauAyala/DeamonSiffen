from lxml import etree

def parse_evento_response(xml_bytes: bytes) -> dict:
    root = etree.fromstring(xml_bytes)
    ns = {"ns": "http://ekuatia.set.gov.py/sifen/xsd"}

    def get(path):
        el = root.find(path, namespaces=ns)
        return el.text if el is not None else None

    return {
        "dCodRes": get(".//ns:dCodRes"),
        "dMsgRes": get(".//ns:dMsgRes"),
        "dProtAut": get(".//ns:dProtAut"),
        "dEstRes": get(".//ns:dEstRes"),
        "dFecProc": get(".//ns:dFecProc"),
        "id": get(".//ns:id"),
    }