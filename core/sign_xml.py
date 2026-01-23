from copy import deepcopy
from xml.dom.expatbuilder import Namespaces
from signxml import XMLSigner, methods, namespaces
from lxml import etree
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey


def signxml(xml_bytes: bytes) -> tuple[etree.Element, str]:
    parser = etree.XMLParser(remove_blank_text=True)
    de_node = etree.fromstring(xml_bytes, parser=parser)

    # Cargar certificado y clave privada
    with open(r"C:\Users\mauri\credenciales\certificado.pem", "rb") as f:
        cert_pem = f.read()
    with open(r"C:\Users\mauri\credenciales\clave_privada.pem", "rb") as f:
        key = f.read()
    password = b"7606"

    cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
    issuer_name = cert.issuer.rfc4514_string()
    serial_number = str(cert.serial_number)

    de_id = de_node.get("Id")
    if not de_id:
        raise ValueError("<DE> no tiene atributo Id")

    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#" 
    )
    signer.namespaces = {None: namespaces.ds}
    try:
        signed_root = signer.sign(
            de_node,
            key=key,
            passphrase=password,
            cert=cert_pem,
            reference_uri="#" + de_id
        )

        # Extraer nodo Signature
        signature_node = signed_root.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
        if signature_node is None:
            raise ValueError("No se generó el nodo Signature")

        # DigestValue
        digest_node = signature_node.find(".//{http://www.w3.org/2000/09/xmldsig#}DigestValue")
        digest_value = digest_node.text if digest_node is not None else None

        # Agregar X509IssuerSerial si existe X509Data
        x509_data = signature_node.find(".//{http://www.w3.org/2000/09/xmldsig#}X509Data")
        if x509_data is not None:
            issuer_serial = etree.SubElement(x509_data, "{http://www.w3.org/2000/09/xmldsig#}X509IssuerSerial")
            etree.SubElement(issuer_serial, "{http://www.w3.org/2000/09/xmldsig#}X509IssuerName").text = issuer_name
            etree.SubElement(issuer_serial, "{http://www.w3.org/2000/09/xmldsig#}X509SerialNumber").text = serial_number

        signature_copy = deepcopy(signature_node)
        # Quitar todos los prefijos y xmlns:ds
        

    except InvalidKey:
        raise ValueError("Clave privada inválida o contraseña errónea.")
    except Exception as e:
        raise RuntimeError(f"Error durante la firma XML: {str(e)}")

    return signature_copy, digest_value
