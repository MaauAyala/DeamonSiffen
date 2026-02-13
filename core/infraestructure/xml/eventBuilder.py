from datetime import datetime, timedelta
from domain.models.models import Evento
from lxml import etree as ET
from core.infraestructure.xml.sign_xml import signxml
import decimal
from core.infraestructure.database.database import get_db
from enum import Enum
from domain.repositories.evento_repo import EventoRepository
class eventBuilder:

    db = next(get_db())
    
    NS = { 
       None: "http://ekuatia.set.gov.py/sifen/xsd",
       "xsi": "http://www.w3.org/2001/XMLSchema-instance",       
    }
    
    def build(self, evento: Evento = None):

        gGroupGesEve = ET.Element("gGroupGesEve", nsmap=self.NS)
        gGroupGesEve.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "http://ekuatia.set.gov.py/sifen/xsd siRecepEvento_v150.xsd"
        )
        
        rGesEve = ET.SubElement(gGroupGesEve, "rGesEve")
        rGesEve.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "http://ekuatia.set.gov.py/sifen/xsd siRecepEvento_v150.xsd"
        )
        
        rEve = self._build_rEve(evento)
        rGesEve.append(rEve)

        xml_bytes = ET.tostring(rEve, encoding="UTF-8", xml_declaration=False)
        rEveFirmado, digest_value = signxml(xml_bytes)
        rGesEve.append(rEveFirmado)
        
        return ET.tostring(gGroupGesEve, encoding="UTF-8", xml_declaration=False)
    
    def _build_rEve(self, evento) -> ET.Element:

        rEve = ET.Element("rEve", Id=str(evento.id))
        
        dfecfirma = datetime.now() - timedelta(seconds=120)
        EventoRepository(self.db).LoadFecFirma(evento_id=evento.id,fec=dfecfirma)
        ET.SubElement(rEve, "dFecFirma").text = dfecfirma.strftime("%Y-%m-%dT%H:%M:%S")
        
        ET.SubElement(rEve, "dVerFor").text = str(getattr(evento, "dverfor", "150"))
        
        gGroupTiEvt = ET.SubElement(rEve, "gGroupTiEvt")
        
        tipo_evento = str(getattr(evento, "itigde", "1"))

        if tipo_evento == "1":
            self._build_cancelacion(gGroupTiEvt, evento)
        elif tipo_evento == "2":
            self._build_inutilizacion(gGroupTiEvt, evento)
        else:
            raise ValueError(f"Tipo de evento no soportado: {tipo_evento}")
        
        return rEve
    
    def _build_cancelacion(self, parent: ET.Element, evento) -> None:

        rGeVeCan = ET.SubElement(parent, "rGeVeCan")
        
        ET.SubElement(rGeVeCan, "Id").text = str(getattr(evento, "cdc_dte", ""))
        ET.SubElement(rGeVeCan, "mOtEve").text = str(getattr(evento, "mototeve", ""))

        if hasattr(evento, 'nombre_solicitante'):
            ET.SubElement(rGeVeCan, "dNomSoli").text = str(evento.nombre_solicitante)

        if hasattr(evento, 'tipo_identificador'):
            ET.SubElement(rGeVeCan, "dTiIDSoli").text = str(evento.tipo_identificador)

        if hasattr(evento, 'numero_identificacion'):
            ET.SubElement(rGeVeCan, "dNumIDSoli").text = str(evento.numero_identificacion)
    
    def _build_inutilizacion(self, parent: ET.Element, evento) -> None:

        rGeVeInu = ET.SubElement(parent, "rGeVeInu")
        gDatGralOpe = ET.SubElement(rGeVeInu, "gDatGralOpe")
        
        ET.SubElement(gDatGralOpe, "dRucOpe").text = str(getattr(evento, "ruc", ""))
        ET.SubElement(gDatGralOpe, "dDV").text = str(self._calcular_dv(evento.ruc)) if hasattr(evento, "ruc") else "1"
        ET.SubElement(gDatGralOpe, "dEst").text = str(getattr(evento, "establecimiento", "001"))
        ET.SubElement(gDatGralOpe, "dPunExp").text = str(getattr(evento, "punto_expedicion", "001"))
        ET.SubElement(gDatGralOpe, "dNumTim").text = str(getattr(evento, "timbrado", "1234567"))
        
        gRangNum = ET.SubElement(rGeVeInu, "gRangNum")
        ET.SubElement(gRangNum, "dNumIni").text = str(getattr(evento, "rango_desde", "1"))
        ET.SubElement(gRangNum, "dNumFin").text = str(getattr(evento, "rango_hasta", "100"))
        
        ET.SubElement(rGeVeInu, "mOtEve").text = str(getattr(evento, "mototeve", ""))
