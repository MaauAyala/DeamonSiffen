import base64
import io
import zipfile



class LoteService:
        
    def rEnvioLote(self, xml,id):
        
      
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("lote.xml", xml)
        zip_b64 = base64.b64encode(buf.getvalue()).decode()

       
        dId = str(id)
        xml_envio = f"""
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
               xmlns:xsd="http://ekuatia.set.gov.py/sifen/xsd">
  <soap:Header/>
  <soap:Body>
    <xsd:rEnvioLoteDe>
      <xsd:dId>{dId}</xsd:dId>
      <xsd:xLoteDE>{zip_b64}</xsd:xLoteDE>
    </xsd:rEnvioLoteDe>
  </soap:Body>
</soap:Envelope>
"""

        return xml_envio.encode("utf-8")
