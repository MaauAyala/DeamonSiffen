import warnings
import xml.etree.ElementTree as ET
from core.sign_xml import signxml

def safe_get(obj, attr, default=""):
    """Devuelve el atributo si existe, si no devuelve un valor por defecto."""
    try:
        return getattr(obj, attr, default) if obj else default
    except Exception:
        return default


class XMLBuilder:
    
    NS = "http://ekuatia.set.gov.py/sifen/xsd"
    
    def build(self, doc):
        rDE = ET.Element("rDE", xmlns=self.NS)
        ET.SubElement(rDE, "dVerFor").text = str(safe_get(doc, "dverfor"))

        DE = ET.SubElement(rDE, "DE", Id=safe_get(doc, "id_de"))
        ET.SubElement(DE, "dDVId").text = str(safe_get(doc, "ddvid"))
        ET.SubElement(DE, "dFecFirma").text = str(safe_get(doc, "dfecfirma"))
        ET.SubElement(DE, "sSisFact").text = str(safe_get(doc, "dsisfact"))

        self._build_gOpeDE(DE, safe_get(doc, "operacion"))
        self._build_gTimb(DE, safe_get(doc, "timbrado"))
        self._build_gDatGralOpe(DE, doc)
        self._build_gDtipDE(DE, doc)
        self._build_gTotSub(DE, safe_get(doc, "totales"))

        xml_unsigned = ET.tostring(rDE, encoding="utf-8", method="xml")
        return xml_unsigned


    def _build_gOpeDE(self, parent, ope):
        if not ope:
            warnings.warn("Documento sin operacion")
            return
        gOpeDE = ET.SubElement(parent, "gOpeDE")
        ET.SubElement(gOpeDE, "iTipEmi").text = str(safe_get(ope, "itipemi"))
        ET.SubElement(gOpeDE, "dDEsTipEmi").text = safe_get(ope, "ddestipemi")
        ET.SubElement(gOpeDE, "dCodSeg").text = safe_get(ope, "dcodseg")
        if safe_get(ope, "dinfoemi"):
            ET.SubElement(gOpeDE, "dInfoEmi").text = ope.dinfoemi
        if safe_get(ope, "dinfofisc"):
            ET.SubElement(gOpeDE, "dInfoFisc").text = ope.dinfofisc


    def _build_gTimb(self, parent, timb):
        if not timb:
            warnings.warn("Documento sin timbrado")
            return
        gTimb = ET.SubElement(parent, "gTimb")
        ET.SubElement(gTimb, "iTiDE").text = str(safe_get(timb, "itide"))
        ET.SubElement(gTimb, "dDesTiDE").text = safe_get(timb, "ddestide")
        ET.SubElement(gTimb, "dNumTim").text = safe_get(timb, "dnumtim")
        ET.SubElement(gTimb, "dEst").text = safe_get(timb, "dest")
        ET.SubElement(gTimb, "dPunExp").text = safe_get(timb, "dpunexp")
        ET.SubElement(gTimb, "dNumDoc").text = safe_get(timb, "dnumdoc")
        ET.SubElement(gTimb, "dSerieNum").text = safe_get(timb, "dserienum")
        dfeinit = safe_get(timb, "dfeinit")
        if dfeinit:
            ET.SubElement(gTimb, "dFeIniT").text = dfeinit.strftime("%Y-%m-%d")


    def _build_gDatGralOpe(self, parent, doc):
        gDatGralOpe = ET.SubElement(parent, "gDatGralOpe")
        dfeemide = safe_get(doc, "dfeemide")
        if dfeemide:
            ET.SubElement(gDatGralOpe, "dFeEmiDE").text = dfeemide.strftime("%Y-%m-%dT%H:%M:%S")
        self._build_gOpeCom(gDatGralOpe, safe_get(doc, "operacion_comercial"))
        self._build_gEmis(gDatGralOpe, safe_get(doc, "emisor"))
        self._build_gDatRec(gDatGralOpe, safe_get(doc, "receptor"))


    def _build_gOpeCom(self, parent, opcom):
        if not opcom:
            warnings.warn("Documento sin operación comercial")
            return
        gOpeCom = ET.SubElement(parent, "gOpeCom")
        ET.SubElement(gOpeCom, "iTipTra").text = str(safe_get(opcom, "itiptra"))
        ET.SubElement(gOpeCom, "dDesTipTra").text = safe_get(opcom, "ddestiptra")
        ET.SubElement(gOpeCom, "iTImp").text = str(safe_get(opcom, "itimp"))
        ET.SubElement(gOpeCom, "dDesTImp").text = safe_get(opcom, "ddestimp")
        ET.SubElement(gOpeCom, "cMoneOpe").text = safe_get(opcom, "cmoneope")
        ET.SubElement(gOpeCom, "dDesMoneOpe").text = safe_get(opcom, "ddesmoneope")


    def _build_gEmis(self, parent, emis):
        if not emis:
            warnings.warn("Documento sin emisor asociado")
            return
        gEmis = ET.SubElement(parent, "gEmis")
        ET.SubElement(gEmis, "dRucEm").text = safe_get(emis, "drucem")
        ET.SubElement(gEmis, "dDVEmi").text = str(safe_get(emis, "ddvemi"))
        ET.SubElement(gEmis, "iTipCont").text = str(safe_get(emis, "itipcont"))
        ET.SubElement(gEmis, "dNomEmi").text = safe_get(emis, "dnomemi")
        ET.SubElement(gEmis, "dDirEmi").text = safe_get(emis, "ddiremi")
        ET.SubElement(gEmis, "dNumCas").text = safe_get(emis, "dnumcas")
        ET.SubElement(gEmis, "cDepEmi").text = str(safe_get(emis, "cdepemi"))
        ET.SubElement(gEmis, "dDesDepEmi").text = safe_get(emis, "ddesdepemi")
        ET.SubElement(gEmis, "cCiuEmi").text = str(safe_get(emis, "cciuremi"))
        ET.SubElement(gEmis, "dDesCiuEmi").text = safe_get(emis, "ddesciuremi")

        for act in getattr(emis, "actividades", []):
            gActEco = ET.SubElement(gEmis, "gActEco")
            ET.SubElement(gActEco, "cActEco").text = safe_get(act, "cacteco")
            ET.SubElement(gActEco, "dDesActEco").text = safe_get(act, "ddesacteco")


    def _build_gDatRec(self, parent, rec):
        if not rec:
            warnings.warn("Documento sin receptor asociado")
            return
        gDatRec = ET.SubElement(parent, "gDatRec")
        ET.SubElement(gDatRec, "iNatRec").text = str(safe_get(rec, "inatrec"))
        ET.SubElement(gDatRec, "iTiOpe").text = str(safe_get(rec, "itiope"))
        ET.SubElement(gDatRec, "dNomRec").text = safe_get(rec, "dnomrec")


    def _build_gDtipDE(self, parent, doc):
        gDtipDE = ET.SubElement(parent, "gDtipDE")
        for item in getattr(doc, "items", []):
            gCamItem = ET.SubElement(gDtipDE, "gCamItem")
            ET.SubElement(gCamItem, "dCodInt").text = safe_get(item, "dcodint")
            ET.SubElement(gCamItem, "dDesProSer").text = safe_get(item, "ddesproser")
            ET.SubElement(gCamItem, "dTotBruOpeItem").text = str(safe_get(item, "dtotbruopeitem"))


    def _build_gTotSub(self, parent, tot):
        if not tot:
            warnings.warn("Documento sin totales")
            return
        gTotSub = ET.SubElement(parent, "gTotSub")
        ET.SubElement(gTotSub, "dTotOpe").text = str(safe_get(tot, "dtotgralope"))
        ET.SubElement(gTotSub, "dTotIVA").text = str(safe_get(tot, "dtotiva"))
