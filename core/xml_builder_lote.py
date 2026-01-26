from lxml import etree

class XMLBuilderLote:
    NS = "http://ekuatia.set.gov.py/sifen/xsd"
    XSI = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_LOC = "http://ekuatia.set.gov.py/sifen/xsd siRecepDE_v150.xsd"

    def build_lote(self, rde_list):
        
        nsmap = {None: self.NS} # "xsi": self.XSI#
        rLoteDE = etree.Element("rLoteDE", nsmap=nsmap)
        #rLoteDE.set(f"{{{self.XSI}}}schemaLocation", self.SCHEMA_LOC)

        # # versión del formato
        # etree.SubElement(rEnvLoteDE, "dVerFor").text = "150"

        # agregar los <rDE> firmados
        for rde_xml in rde_list:
            rde_node = etree.fromstring(rde_xml)
            rLoteDE.append(rde_node)

        return etree.tostring(
            rLoteDE,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8"
        )
