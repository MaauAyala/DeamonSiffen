from lxml import etree

class XMLBuilderLote:
    NS = "http://ekuatia.set.gov.py/sifen/xsd"
    XSI = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_LOC = "http://ekuatia.set.gov.py/sifen/xsd siRecepDE_v150.xsd"

    def build_lote(self, rde_list):
        xml = b'<?xml version="1.0" encoding="UTF-8"?>'
        xml += b'<rLoteDE xmlns="http://ekuatia.set.gov.py/sifen/xsd">'

        for rde in rde_list:
            xml += rde.strip()  # rde YA firmado, sin tocar

        xml += b'</rLoteDE>'
        return xml