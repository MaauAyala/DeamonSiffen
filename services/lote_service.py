import base64
import io
import zipfile
from core.xml_builder_lote import XMLBuilderLote
from domain.repositories.lote_repo import LoteRepo

class LoteService:
    def __init__(self, db):
        self.db = db
        self.repo = LoteRepo(db)
        
    def crearLotes(self, xml_list):
        
        xml_lote = XMLBuilderLote().build_lote(xml_list)
        
        
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("lote.xml", xml_lote)
        zip_b64 = base64.b64encode(buf.getvalue()).decode()

        
        nuevo_lote = self.repo.newLote(xml_lote, len(xml_list))

        
        dId = str(nuevo_lote.id)
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

        return xml_envio.encode("utf-8"), nuevo_lote
