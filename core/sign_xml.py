from signxml import XMLSigner, methods
from lxml import etree

def signxml(xml_bytes):
    parser = etree.XMLParser(remove_blank_text=True)
    xml = etree.fromstring(xml_bytes, parser=parser)

    
    with open("certificado.pem") as f:
        cert = f.read()
    with open("clave_privada.pem") as f:
        key = f.read()

    
    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
    )

    
    de_node = xml.find(".//{*}DE")
    signed_node = signer.sign(de_node, key=key, cert=cert, reference_uri="#" + de_node.get("Id"))

    
    xml.append(signed_node.find(".//{*}Signature"))

    
    return etree.tostring(xml, encoding="utf-8", xml_declaration=True)
