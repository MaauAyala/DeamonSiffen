from domain.models.eventoModel import Evento
from lxml import etree as ET
from core.sign_xml import signxml
import decimal
from core.database import get_db
from enum import Enum


class eventBuilder:

    db = next(get_db())
    
    NS = { 
       None: "http://ekuatia.set.gov.py/sifen/xsd",
       "xsi": "http://www.w3.org/2001/XMLSchema-instance",       
    }
    
    def build(self, evento: Evento = None):

        if evento is None:
            # Valores por defecto para testing
            evento = type('MockEvento', (), {
                'id': '1',
                'tipo_evento': TipoEvento.CANCELACION.value,
                'dfecfirma': '2025-12-18T14:17:10',
                'dverfor': '150',
                'cdc_dte': '124422142412421321321',
                'mototeve': 'Prueba de Evento',
                'tipeve' :'1',
                # Campos específicos de inutilización si necesitas
                'ruc': '80000001',
                'establecimiento': '001',
                'punto_expedicion': '001',
                'timbrado': '1234567',
                'rango_desde': '1',
                'rango_hasta': '100'
            })()
        
        # Elemento raíz
        rEnviEventoDe = ET.Element("rEnviEventoDe")
        
        # dId
        id_element = ET.SubElement(rEnviEventoDe, "dId")
        id_element.text = str(evento.id)
        
        # dEvReg
        dEvReg = ET.SubElement(rEnviEventoDe, "dEvReg")
        
        # gGroupGesEve
        gGroupGesEve = ET.SubElement(dEvReg, "gGroupGesEve", nsmap=self.NS)
        gGroupGesEve.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "http://ekuatia.set.gov.py/sifen/xsd siRecepEvento_v150.xsd"
        )
        
        # rGesEve
        rGesEve = ET.SubElement(gGroupGesEve, "rGesEve")
        rGesEve.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "http://ekuatia.set.gov.py/sifen/xsd siRecepEvento_v150.xsd"
        )
        
        # rEve con contenido específico según tipo de evento
        rEve = self._build_rEve(evento)
        rGesEve.append(rEve)
        
        # Convertir a string
        xml_str = ET.tostring(
            rEnviEventoDe,
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True
        ).decode('utf-8')
        
        return xml_str
    
    def _build_rEve(self, evento) -> ET.Element:
        """
        Construye el elemento rEve según el tipo de evento
        """
        # Crear elemento rEve con Id
        rEve = ET.Element("rEve", Id=str(evento.id))
        
        # Elementos comunes a todos los eventos
        dFecFirma_element = ET.SubElement(rEve, "dFecFirma")
        dFecFirma_element.text = evento.dfecfirma if hasattr(evento, 'dfecfirma') else "2025-12-18T14:17:10"
        
        dVerFor_element = ET.SubElement(rEve, "dVerFor")
        dVerFor_element.text = evento.dverfor if hasattr(evento, 'dverfor') else "150"
        
        # gGroupTiEvt con contenido específico
        gGroupTiEvt = ET.SubElement(rEve, "gGroupTiEvt")
        
        # Determinar tipo de evento
        tipo_evento = getattr(evento, 'tipo_evento', Evento.tipeve)
        
        if tipo_evento == 1:
            self._build_cancelacion(gGroupTiEvt, evento)
        elif tipo_evento == 2:
            self._build_inutilizacion(gGroupTiEvt, evento)
        else:
            raise ValueError(f"Tipo de evento no soportado: {tipo_evento}")
        
        return rEve
    
    def _build_cancelacion(self, parent: ET.Element, evento) -> None:
        """
        Construye estructura para evento de cancelación
        """
        rGeVeCan = ET.SubElement(parent, "rGeVeCan")
        
        # CDC de la factura
        cdc_element = ET.SubElement(rGeVeCan, "Id")
        cdc_element.text = evento.cdc_dte if hasattr(evento, 'cdc_dte') else "124422142412421321321"
        
        # Motivo
        mOtEve_element = ET.SubElement(rGeVeCan, "mOtEve")
        mOtEve_element.text = evento.mototeve if hasattr(evento, 'mototeve') else "Prueba de Evento"
        
        # Campos opcionales de cancelación
        if hasattr(evento, 'nombre_solicitante'):
            ET.SubElement(rGeVeCan, "dNomSoli").text = evento.nombre_solicitante
        
        if hasattr(evento, 'tipo_identificador'):
            ET.SubElement(rGeVeCan, "dTiIDSoli").text = evento.tipo_identificador
        
        if hasattr(evento, 'numero_identificacion'):
            ET.SubElement(rGeVeCan, "dNumIDSoli").text = evento.numero_identificacion
    
    def _build_inutilizacion(self, parent: ET.Element, evento) -> None:
        """
        Construye estructura para evento de inutilización
        """
        rGeVeInu = ET.SubElement(parent, "rGeVeInu")
        
        # Datos generales del contribuyente
        gDatGralOpe = ET.SubElement(rGeVeInu, "gDatGralOpe")
        
        # RUC
        dRucOpe = ET.SubElement(gDatGralOpe, "dRucOpe")
        dRucOpe.text = evento.ruc if hasattr(evento, 'ruc') else "80000001"
        
        # Dígito verificador (calcular o usar uno proporcionado)
        dDV = ET.SubElement(gDatGralOpe, "dDV")
        dDV.text = self._calcular_dv(evento.ruc) if hasattr(evento, 'ruc') else "1"
        
        # Establecimiento
        dEst = ET.SubElement(gDatGralOpe, "dEst")
        dEst.text = evento.establecimiento if hasattr(evento, 'establecimiento') else "001"
        
        # Punto de expedición
        dPunExp = ET.SubElement(gDatGralOpe, "dPunExp")
        dPunExp.text = evento.punto_expedicion if hasattr(evento, 'punto_expedicion') else "001"
        
        # Número de timbrado
        dNumTim = ET.SubElement(gDatGralOpe, "dNumTim")
        dNumTim.text = evento.timbrado if hasattr(evento, 'timbrado') else "1234567"
        
        # Rango de números
        gRangNum = ET.SubElement(rGeVeInu, "gRangNum")
        
        dNumIni = ET.SubElement(gRangNum, "dNumIni")
        dNumIni.text = evento.rango_desde if hasattr(evento, 'rango_desde') else "1"
        
        dNumFin = ET.SubElement(gRangNum, "dNumFin")
        dNumFin.text = evento.rango_hasta if hasattr(evento, 'rango_hasta') else "100"
        
        # Motivo
        mOtEve = ET.SubElement(rGeVeInu, "mOtEve")
        mOtEve.text = evento.mototeve if hasattr(evento, 'mototeve') else "Equipo dañado"
