import base64
import io
import os
import zipfile
from dotenv import load_dotenv
from core.infraestructure.soap.soap_client import SOAPClient

load_dotenv()
endpoint= os.environ["LOTE_ENDPOINT"]





class LoteService:
  
  endpoint = "https://sifen-test.set.gov.py/de/ws/async/recibe-lote.wsdl"
  
  def rEnvioLote(client, xml: bytes, id: int):
      """
      Envía un lote de documentos electrónicos a Sifen.
      
      Args:
          client: Cliente SOAP configurado
          xml: XML del lote en bytes (debe ser un XML válido de Sifen)
          id: ID del lote
      
      Returns:
          Respuesta del servidor
      """
      if not isinstance(xml, (bytes, bytearray)):
          raise TypeError("xml debe ser bytes")
      
      # Quitar BOM si existe (igual que en sendEvento)
      if xml.startswith(b'\xef\xbb\xbf'):
          xml = xml[3:]
      
      # 1. Crear ZIP en memoria
      buf = io.BytesIO()
      with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
          zf.writestr("lote.xml", xml)
      
      # 2. Codificar a base64
      zip_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
      
      # 3. Convertir a bytes para concatenación
      zip_b64_bytes = zip_b64.encode("utf-8")
      
      # 4. ID formateado (ajusta el padding según requiera Sifen para lotes)
      dId = str(id).encode("utf-8")  # Ajusta zfill si necesario
      
      # 5. Construir SOAP envelope (mismo estilo que sendEvento)
      soap_bytes = (
          b'<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">'
          b'<soap:Header/>'
          b'<soap:Body>'
          b'<rEnvioLote xmlns="http://ekuatia.set.gov.py/sifen/xsd">'
          b'<dId>' + dId + b'</dId>'
          b'<xDE>' + zip_b64_bytes + b'</xDE>'
          b'</rEnvioLote>'
          b'</soap:Body>'
          b'</soap:Envelope>'
      )
      

      response = client.send(endpoint, soap_bytes)
      return response.content.decode("utf-8") 