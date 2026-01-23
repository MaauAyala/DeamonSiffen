# Archivo: tests/testSignxml.py

import os
from core.sign_xml import signxml
from lxml import etree

def test_signature_is_added():
    try:
        
        id_test = 20
        output_dir = "tests/output"
        os.makedirs(output_dir, exist_ok=True)
        # 1. Cargar el XML de prueba
        print(" Cargando XML de prueba...")
        with open(r"C:\Users\mauri\demonSiffen\tests\output\documento_20.xml", "rb") as f:
            xml_data = f.read()
        print(f" XML cargado: {len(xml_data)} bytes")

        # 2. Firmar el XML
        print(" Firmando XML...")
        xml_firmado = signxml(xml_data)
        
        print(f" XML firmado: {len(xml_firmado)} bytes")

        # 3. Verificar que la firma fue añadida
        xml_str = xml_firmado.decode("utf-8")
        
        # Verificar que contiene el elemento Signature (con o sin namespace)
        signature_found = False
        if "<Signature" in xml_str:
            signature_found = True
        elif "ns:Signature" in xml_str:
            signature_found = True
        elif "Signature" in xml_str:
            signature_found = True
            
        if not signature_found:
            print(" ERROR: No se encontró el elemento <Signature>")
            print("XML resultante (primeros 1000 chars):")
            print(xml_str[:1000])
            print("\nBuscando 'Signature' en el XML:")
            lines = xml_str.split('\n')
            for i, line in enumerate(lines):
                if 'Signature' in line:
                    print(f"Línea {i+1}: {line.strip()}")
            raise AssertionError("No se encontró el elemento <Signature> en el XML firmado")
        
        # Verificar que contiene elementos de firma específicos
        assert "SignatureValue" in xml_str, "No se encontró SignatureValue en el XML"
        assert "X509Certificate" in xml_str, "No se encontró X509Certificate en el XML"
        
        print(" Firma XML verificada correctamente")
        print(" Elementos de firma encontrados:")
        if "<Signature" in xml_str:
            print("   - Elemento <Signature>: ")
        if "SignatureValue" in xml_str:
            print("   - SignatureValue: ")
        if "X509Certificate" in xml_str:
            print("   - X509Certificate: ")
            
    except FileNotFoundError as e:
        print(f" Error de archivo: {e}")
        raise
    except ValueError as e:
        print(f" Error de validación: {e}")
        raise
    except Exception as e:
        print(f" Error inesperado: {e}")
        print("Posibles causas:")
        print("   - Contraseña de clave privada incorrecta")
        print("   - Certificado o clave inválidos")
        print("   - Problemas con el XML de entrada")
        raise
    
    output_path = os.path.join(output_dir, f"documento_{id_test}.xml")
    with open(output_path, "wb") as f:
        f.write(xml_firmado)