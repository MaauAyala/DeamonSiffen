import os
import warnings
from dotenv import load_dotenv
from lxml import etree as ET
from core.sign_xml import signxml
import decimal
from core.database import get_db
from domain.models.models import OperacionContado, Timbrado, OperacionCredito
from utils.hashQR import sha256_hash_bytes
from utils.toInt import to_int_if_possible


load_dotenv()


def safe_get(obj, attr, default=""):
    """Devuelve el atributo si existe, si no devuelve un valor por defecto."""
    try:
        # Intenta acceder al atributo. Si es un número, se asegura que no se use "" como default.
        if isinstance(default, (int, float, decimal.Decimal)) and not isinstance(obj, (int, float, decimal.Decimal)):
            return getattr(obj, attr, default) if obj else default
        return getattr(obj, attr, default) if obj else default
    except Exception:
        return default




class XMLBuilder:
    
    db = next(get_db())
    
    
    
    NS = {
        None: "http://ekuatia.set.gov.py/sifen/xsd",   # namespace default
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    def build(self, doc):
        
        rDE = ET.Element("rDE", nsmap=self.NS)


        rDE.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "http://ekuatia.set.gov.py/sifen/xsd siRecepDE_v150.xsd"
        )

        ET.SubElement(rDE, "dVerFor").text = str(safe_get(doc, "dverfor"))
        cdc =safe_get(doc, "cdc_de")
        dv = safe_get(doc, "ddvid")
        Id_DE=f'{cdc}{dv}'
        DE = ET.SubElement(rDE, "DE", Id=Id_DE)
        ET.SubElement(DE, "dDVId").text = str(safe_get(doc, "ddvid"))

        fechafirma =doc.dfecfirma.strftime("%Y-%m-%dT%H:%M:%S") #"2025-12-18T14:17:10"
        ET.SubElement(DE, "dFecFirma").text = fechafirma

        ET.SubElement(DE, "dSisFact").text = str(safe_get(doc, "dsisfact"))

        self._build_gOpeDE(DE, safe_get(doc, "operacion"))

        timbrado = (
            self.db.query(Timbrado)
            .filter(Timbrado.id == doc.idtimbrado)
            .first()
        )

        self._build_gTimb(DE, timbrado, doc)
        self._build_gDatGralOpe(DE, doc)
        self._build_gDtipDE(DE, doc)

        if timbrado.itide == 5:
            self._build_gCamNCDE(DE, safe_get(doc, "nota_credito_debito"))

        self._build_gTotSub(DE, safe_get(doc, "totales"))

        # 1. Serializar el nodo DE para la firma (ya tenemos la referencia)
        xml_unsigned = ET.tostring(DE, encoding="utf-8", pretty_print=False, xml_declaration=False)
        
        try:
            signature_node, digest_value = signxml(xml_unsigned)
        except Exception as e:
            raise Exception(f"Fallo durante la firma XML o extracción del DigestValue: {e}")


        
        # 3. ADJUNTAR LA SIGNATURE al final de rDE
        rDE.append(signature_node)
        
                # 2. CONSTRUIR <gCamFuFD> (y <rQR>) usando el DigestValue
        self._build_gCamFuFD(rDE, doc, digest_value)
        
        # 4. Serializar y retornar el XML COMPLETO Y FIRMADO CON declaración XML
        xml_signed = ET.tostring(rDE, encoding="utf-8", xml_declaration=False, pretty_print=False)
        
        return xml_signed

    def _build_gOpeDE(self, parent, ope):
        if not ope:
            warnings.warn("Documento sin operacion")
            return
        gOpeDE = ET.SubElement(parent, "gOpeDE")
        ET.SubElement(gOpeDE, "iTipEmi").text = str(safe_get(ope, "itipemi"))
        
        # CORRECCIÓN DE TYPO: dDesTipEmi en lugar de dDEsTipEmi
        ET.SubElement(gOpeDE, "dDesTipEmi").text = safe_get(ope, "ddestipemi")
        
        ET.SubElement(gOpeDE, "dCodSeg").text = safe_get(ope, "dcodseg")
        if safe_get(ope, "dinfoemi"):
            ET.SubElement(gOpeDE, "dInfoEmi").text = ope.dinfoemi
        if safe_get(ope, "dinfofisc"):
            ET.SubElement(gOpeDE, "dInfoFisc").text = ope.dinfofisc


    def _build_gTimb(self, parent, timb , doc):
        if not timb:
            warnings.warn("Documento sin timbrado")
            return
        gTimb = ET.SubElement(parent, "gTimb")
        ET.SubElement(gTimb, "iTiDE").text = str(safe_get(timb, "itide"))
        ET.SubElement(gTimb, "dDesTiDE").text = safe_get(timb, "ddestide")
        ET.SubElement(gTimb, "dNumTim").text = safe_get(timb, "dnumtim")
        ET.SubElement(gTimb, "dEst").text = safe_get(timb, "dest")
        ET.SubElement(gTimb, "dPunExp").text = safe_get(timb, "dpunexp")
        ET.SubElement(gTimb, "dNumDoc").text = str(safe_get(doc, "dnumdoc")).zfill(7)
        #ET.SubElement(gTimb, "dSerieNum").text = safe_get(doc, "dserienum")
        dfeinit = safe_get(timb, "dfeinit")
        if dfeinit:
            # Asume que dfeinit es un objeto datetime o similar
            ET.SubElement(gTimb, "dFeIniT").text = dfeinit.strftime("%Y-%m-%d")


    def _build_gDatGralOpe(self, parent, doc):
        gDatGralOpe = ET.SubElement(parent, "gDatGralOpe")
        dfeemide = safe_get(doc, "dfeemide")
        if dfeemide:
            # Asume que dfeemide es un objeto datetime o similar
            ET.SubElement(gDatGralOpe, "dFeEmiDE").text = dfeemide.strftime("%Y-%m-%dT%H:%M:%S") #"2025-12-18T14:14:10"
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
        # ADICIÓN: Elemento cTipReg faltante en el original
        if safe_get(emis, "ctipreg"):
            ET.SubElement(gEmis, "cTipReg").text = str(safe_get(emis, "ctipreg"))

        ET.SubElement(gEmis, "dNomEmi").text = safe_get(emis, "dnomemi")
        
        # Nombre fantasía (opcional)
        if safe_get(emis, "dnomfanemi"):
            ET.SubElement(gEmis, "dNomFanEmi").text = safe_get(emis, "dnomfanemi")
        
        ET.SubElement(gEmis, "dDirEmi").text = safe_get(emis, "ddiremi")
        ET.SubElement(gEmis, "dNumCas").text = safe_get(emis, "dnumcas")
        
        # Complementos de dirección (opcionales)
        if safe_get(emis, "dcompdir1"):
            ET.SubElement(gEmis, "dCompDir1").text = safe_get(emis, "dcompdir1")
        if safe_get(emis, "dcompdir2"):
            ET.SubElement(gEmis, "dCompDir2").text = safe_get(emis, "dcompdir2")
        
        ET.SubElement(gEmis, "cDepEmi").text = str(safe_get(emis, "cdepemi"))
        ET.SubElement(gEmis, "dDesDepEmi").text = safe_get(emis, "ddesdepemi")
        
        # Distrito (opcional)
        if safe_get(emis, "cdisemi"):
            ET.SubElement(gEmis, "cDisEmi").text = str(safe_get(emis, "cdisemi"))
        if safe_get(emis, "ddesdisemi"):
            ET.SubElement(gEmis, "dDesDisEmi").text = safe_get(emis, "ddesdisemi")
        
        ET.SubElement(gEmis, "cCiuEmi").text = str(safe_get(emis, "cciuemi")) 
        ET.SubElement(gEmis, "dDesCiuEmi").text = safe_get(emis, "ddesciuemi") 
        ET.SubElement(gEmis, "dTelEmi").text = safe_get(emis , "dtelemi")
        ET.SubElement(gEmis, "dEmailE").text = safe_get(emis , "demaile")
        
        # Denominación de sucursal (opcional)
        if safe_get(emis, "ddensuc"):
            ET.SubElement(gEmis, "dDenSuc").text = safe_get(emis, "ddensuc")
        
        for act in getattr(emis, "actividades", []):
            gActEco = ET.SubElement(gEmis, "gActEco")
            ET.SubElement(gActEco, "cActEco").text = safe_get(act, "cacteco")
            ET.SubElement(gActEco, "dDesActEco").text = safe_get(act, "ddesacteco")


    def _build_gDatRec(self, parent, rec):
        if not rec:
            warnings.warn("Documento sin receptor asociado")
            return
        gDatRec = ET.SubElement(parent, "gDatRec")
        ET.SubElement(gDatRec, "iNatRec").text = str(safe_get(rec , "inatrec", ""))# "1"
        ET.SubElement(gDatRec, "iTiOpe").text = str(safe_get(rec , "itiope", ""))# "1"

        # Datos de País
        ET.SubElement(gDatRec, "cPaisRec").text = safe_get(rec , "cpaisrec")#"PRY"
        ET.SubElement(gDatRec, "dDesPaisRe").text = safe_get(rec , "ddespaisre")#"Paraguay"

        # Datos de Identificación (RUC) - Solo si es contribuyente
        inatrec = safe_get(rec, "inatrec")
        if inatrec == 1:  # Contribuyente
            ET.SubElement(gDatRec, "iTiContRec").text = str(safe_get(rec , "iticontrec", ""))#"2" # Tipo Contribuyente 
            ET.SubElement(gDatRec, "dRucRec").text = safe_get(rec , "drucrec")#"1234567"
            ET.SubElement(gDatRec, "dDVRec").text = str(safe_get(rec , "ddvrec", ""))#"9"
        else:
            # No contribuyente - requiere tipo de documento de identidad
            if safe_get(rec, "itipidrec"):
                ET.SubElement(gDatRec, "iTipIdRec").text = str(safe_get(rec, "itipidrec"))
            if safe_get(rec, "ddtipidrec"):
                ET.SubElement(gDatRec, "dDTipIdRec").text = safe_get(rec, "ddtipidrec")
            if safe_get(rec, "dnumidrec"):
                ET.SubElement(gDatRec, "dNumIdRec").text = safe_get(rec, "dnumidrec")
        
        ET.SubElement(gDatRec, "dNomRec").text = safe_get(rec , "dnomrec")#"RECEPTOR DEL DOCUMENTO"
        
        # Nombre de fantasía (opcional)
        if safe_get(rec, "dnomfanrec"):
            ET.SubElement(gDatRec, "dNomFanRec").text = safe_get(rec, "dnomfanrec")

        # Datos de Dirección y Contacto
        if safe_get(rec, "ddirrec"):
            ET.SubElement(gDatRec, "dDirRec").text = safe_get(rec , "ddirrec")#"CALLE 1 ENTRE CALLE 2 Y CALLE 3"
        if safe_get(rec, "dnumcasrec"):
            ET.SubElement(gDatRec, "dNumCasRec").text = str(safe_get(rec , "dnumcasrec"))#"123" # Número de Casa/Lote (Opcional, pero SIFEN lo recomienda si existe)

        # Datos de Ubicación Geográfica
        if safe_get(rec , "cdeprec"):
            ET.SubElement(gDatRec, "cDepRec").text = str(safe_get(rec , "cdeprec"))#"1"
        if safe_get(rec , "ddesdeprec"):
            ET.SubElement(gDatRec, "dDesDepRec").text = safe_get(rec , "ddesdeprec")#"CAPITAL"
        if safe_get(rec , "cdisrec"):
            ET.SubElement(gDatRec, "cDisRec").text = str(safe_get(rec , "cdisrec"))#"1" # Código de Distrito (Campo nuevo que agregaste)
        if safe_get(rec , "ddesdisrec"):
            ET.SubElement(gDatRec, "dDesDisRec").text = safe_get(rec , "ddesdisrec")#"ASUNCION (DISTRITO)"
        if safe_get(rec , "cciurec"):
            ET.SubElement(gDatRec, "cCiuRec").text = str(safe_get(rec , "cciurec"))#"1"
        if safe_get(rec , "ddesciurec"):
            ET.SubElement(gDatRec, "dDesCiuRec").text = safe_get(rec , "ddesciurec")#"ASUNCION (DISTRITO)"
        if safe_get(rec , "dtelrec"):
            ET.SubElement(gDatRec, "dTelRec").text = safe_get(rec , "dtelrec")#"012123456"
        
        # Celular (opcional)
        if safe_get(rec, "dcelrec"):
            ET.SubElement(gDatRec, "dCelRec").text = safe_get(rec, "dcelrec")
        
        # Email (opcional)
        if safe_get(rec, "demailrec"):
            ET.SubElement(gDatRec, "dEmailRec").text = safe_get(rec, "demailrec")

        # Campo Opcional (código interno del cliente)
        if safe_get(rec , "dcodcliente"):
            ET.SubElement(gDatRec, "dCodCliente").text = safe_get(rec , "dcodcliente")#"00000004"


    def _build_gDtipDE(self, parent, doc):
        gDtipDE = ET.SubElement(parent, "gDtipDE")

        self._build_gCamFE(gDtipDE)

        gCamCond = ET.SubElement(gDtipDE, "gCamCond")

        # iCondOpe: 1=Contado, 2=Crédito
        operacion = safe_get(doc, "operacion")
        icondope = safe_get(operacion, "icondope") if operacion else 1
        
        if icondope == 2:  # Crédito
            ET.SubElement(gCamCond, "iCondOpe").text = "2"
            ET.SubElement(gCamCond, "dDCondOpe").text = "Crédito"

            # gPagCred SOLO si es crédito
            gPagCred = ET.SubElement(gCamCond, "gPagCred")
            
            if operacion and isinstance(operacion, OperacionCredito):
                icondcred = safe_get(operacion, "icondcred")
                if icondcred == 1:  # Plazo
                    ET.SubElement(gPagCred, "iCondCred").text = "1"
                    ET.SubElement(gPagCred, "dDCondCred").text = "Plazo"
                    ET.SubElement(gPagCred, "dPlazoCre").text = safe_get(operacion, "dplazocre")
                elif icondcred == 2:  # Cuota
                    ET.SubElement(gPagCred, "iCondCred").text = "2"
                    ET.SubElement(gPagCred, "dDCondCred").text = "Cuota"
                    ET.SubElement(gPagCred, "dCuotas").text = str(safe_get(operacion, "dcuotas"))
        else:  # Contado (1)
            
            ET.SubElement(gCamCond, "iCondOpe").text = "1"
            ET.SubElement(gCamCond, "dDCondOpe").text = "Contado"
            
            gPaConEIni = ET.SubElement(gCamCond, "gPaConEIni")
            
                
            ET.SubElement(gPaConEIni, "iTiPago").text = str(safe_get(operacion ,"itipago"))
            ET.SubElement(gPaConEIni , "dDesTiPag").text = safe_get(operacion, "ddestipag")
            ET.SubElement(gPaConEIni , "dMonTiPag").text = str(safe_get(operacion, "dmontipag"))
            ET.SubElement(gPaConEIni , "cMoneTiPag").text = safe_get(operacion, "cmonetipag")
            ET.SubElement(gPaConEIni , "dDMoneTiPag").text = safe_get(operacion, "ddmonetipag") 
            if safe_get(operacion, "cmonetipag") != "PYG":
                ET.SubElement(gPaConEIni , "dTiCamTiPag").text = str(safe_get(operacion, "dticamtiPpag") )

        for item in getattr(doc, "items", []):
            gCamItem = ET.SubElement(gDtipDE, "gCamItem")
            ET.SubElement(gCamItem, "dCodInt").text = safe_get(item, "dcodint")
            ET.SubElement(gCamItem, "dDesProSer").text = safe_get(item, "ddesproser")
            ET.SubElement(gCamItem, "cUniMed").text = str(safe_get(item, "cunimed"))
            ET.SubElement(gCamItem, "dDesUniMed").text = safe_get(item, "ddesunimed")
            ET.SubElement(gCamItem, "dCantProSer").text = str(safe_get(item, "dcantproser"))

            gValorItem = ET.SubElement(gCamItem, "gValorItem")
            ET.SubElement(gValorItem, "dPUniProSer").text = str(safe_get(item, "dpuniproser"))
            ET.SubElement(gValorItem, "dTotBruOpeItem").text = str(safe_get(item, "dtotbruopeitem"))

            gValorRestaItem = ET.SubElement(gValorItem, "gValorRestaItem")
            ET.SubElement(gValorRestaItem, "dDescItem").text = str(safe_get(item, "ddescitem", "0"))
            ET.SubElement(gValorRestaItem, "dPorcDesIt").text = str(safe_get(item, "dporcdesit", "0"))
            ET.SubElement(gValorRestaItem, "dDescGloItem").text = str(safe_get(item, "ddescgloitem", "0"))
            ET.SubElement(gValorRestaItem, "dTotOpeItem").text =str(safe_get(item, "dtotopeitem"))

            gCamIVA = ET.SubElement(gCamItem, "gCamIVA")
            ET.SubElement(gCamIVA, "iAfecIVA").text = str(safe_get(item, "iafeciva"))
            ET.SubElement(gCamIVA, "dDesAfecIVA").text = safe_get(item, "ddesafeciva")
            ET.SubElement(gCamIVA, "dPropIVA").text = str(safe_get(item, "dpropiva"))
            ET.SubElement(gCamIVA, "dTasaIVA").text = str(int(safe_get(item, "dtasaiva", 0)))
            ET.SubElement(gCamIVA, "dBasGravIVA").text = str(safe_get(item, "dbasgraviva"))
            ET.SubElement(gCamIVA, "dLiqIVAItem").text = str(safe_get(item, "dliqivaitem"))
            ET.SubElement(gCamIVA, "dBasExe").text = str(safe_get(item, "dbasexe", "0"))

        return gDtipDE



    def _build_gTotSub(self, parent, tot):
        if not tot:
            warnings.warn("Documento sin totales")
            return
        gTotSub = ET.SubElement(parent, "gTotSub")
        
        # ADICIÓN: Subtotales por Tasa (necesarios para el desglose)
        ET.SubElement(gTotSub, "dSubExe").text = str(safe_get(tot, "dsubexe", "0"))
        ET.SubElement(gTotSub, "dSubExo").text = str(safe_get(tot, "dsubexo", "0"))
        ET.SubElement(gTotSub, "dSub5").text = str(safe_get(tot, "dsub5", "0"))
        ET.SubElement(gTotSub, "dSub10").text = str(safe_get(tot, "dsub10", "0"))
        
        # dTotOpe es el Total de la Operación (suma de dSubExe, dSubExo, dSub5, dSub10)
        ET.SubElement(gTotSub, "dTotOpe").text = str(safe_get(tot, "dtotope"))
        
        # ADICIÓN: Otros Totales de Operación (Descuentos, Anticipos)
        ET.SubElement(gTotSub, "dTotDesc").text = str(safe_get(tot, "dtotdesc", "0.0"))
        ET.SubElement(gTotSub, "dTotDescGlotem").text = str(safe_get(tot, "dtotdescglotem", "0.0"))
        ET.SubElement(gTotSub, "dTotAntItem").text = str(safe_get(tot, "dtotantitem", "0.0"))
        ET.SubElement(gTotSub, "dTotAnt").text = str(safe_get(tot, "dtotant", "0.0"))
        valor_decimal = safe_get(tot, "dporcdesctotal", 0.0)
        valor_formateado = "{:.8f}".format(valor_decimal)
        ET.SubElement(gTotSub, "dPorcDescTotal").text = valor_formateado
        ET.SubElement(gTotSub, "dDescTotal").text =  str(safe_get(tot, "ddesctotal", "0"))
        ET.SubElement(gTotSub, "dAnticipo").text =  str(safe_get(tot, "danticipo", "0"))   
        ET.SubElement(gTotSub, "dRedon").text =  str(safe_get(tot, "dredon", "0"))
        ET.SubElement(gTotSub, "dComi").text =  str(safe_get(tot, "dcomi", "0"))
        ET.SubElement(gTotSub, "dTotGralOpe").text = str(safe_get(tot, "dtotgralope", "0"))
        
        # me falta liquidaciones de IVA y de comision
        ET.SubElement(gTotSub, "dIVA5").text = to_int_if_possible(safe_get(tot, "diva5", "0"))
        ET.SubElement(gTotSub, "dIVA10").text = to_int_if_possible(safe_get(tot, "diva10", "0"))
        ET.SubElement(gTotSub, "dTotIVA").text = to_int_if_possible(safe_get(tot, "dtotiva", "0"))
        
        # ADICIÓN: Base Imponible
        ET.SubElement(gTotSub, "dBaseGrav5").text = to_int_if_possible(safe_get(tot, "dbasegrav5", "0"))
        ET.SubElement(gTotSub, "dBaseGrav10").text = to_int_if_possible(safe_get(tot, "dbasegrav10", "0"))
        ET.SubElement(gTotSub, "dTBasGraIVA").text = to_int_if_possible(safe_get(tot, "dtbasgraiva", "0"))
        


    def _build_gCamNCDE(self, parent, nc):
        """Construye el bloque específico de Nota de Crédito / Débito."""
        if not nc:
            warnings.warn("Documento marcado como Nota de Crédito pero sin datos asociados")
            return

        gCamNCDE = ET.SubElement(parent, "gCamNCDE")
        ET.SubElement(gCamNCDE, "iMotEmi").text = str(safe_get(nc, "imotemi"))
        ET.SubElement(gCamNCDE, "dDesMotEmi").text = safe_get(nc, "ddesmotemi")

        # Campos referenciados a la factura original
        ET.SubElement(gCamNCDE, "dNumTim").text = safe_get(nc, "dnumtim_ref")
        ET.SubElement(gCamNCDE, "dEst").text = safe_get(nc, "dest_ref")
        ET.SubElement(gCamNCDE, "dPunExp").text = safe_get(nc, "dpunexp_ref")
        ET.SubElement(gCamNCDE, "dNumDoc").text = safe_get(nc, "dnumdoc_ref")
        
    def _build_gCamFuFD(self, rDE, doc, digest_value):
        gCamFuFD = ET.SubElement(rDE, "gCamFuFD")

        # ---- parámetros obligatorios del QR ----
        version = "150" 
        cdc =safe_get(doc, "cdc_de")
        dv = safe_get(doc, "ddvid")
        Id=f'{cdc}{dv}'  # el CDC completo (44 dígitos)
        dfeemide = safe_get(doc, "dfeemide")
        dFeEmiDE = dfeemide.strftime("%Y-%m-%dT%H:%M:%S").encode().hex() if dfeemide else ""
        receptor = safe_get(doc, "receptor")
        dRucRec = safe_get(receptor, "drucrec") if receptor else ""
        totales = safe_get(doc, "totales")
        dTotGralOpe = str(safe_get(totales, "dtotgralope", "0")) if totales else "0"
        dTotIVA = to_int_if_possible(safe_get(totales, "dtotiva", "0") if totales else "0")
        items = getattr(doc, "items", [])
        cItems = str(len(items))
        DigestValue = (digest_value).encode().hex()
        IdCSC = "0001"  # siempre fijo en TEST  

        # ---- construir URL QR ----
        datos_qr = (
            f"nVersion={version}&"
            f"Id={Id}&"
            f"dFeEmiDE={dFeEmiDE}&"
            f"dRucRec={dRucRec}&"
            f"dTotGralOpe={dTotGralOpe}&"
            f"dTotIVA={dTotIVA}&"
            f"cItems={cItems}&"
            f"DigestValue={DigestValue}&"
            f"IdCSC={IdCSC}"
        )
        
        
        CSC = os.environ["CSC"]

        cadena_hash = datos_qr + CSC
        hashQR = sha256_hash_bytes(cadena_hash.encode("utf-8"))
        # validar test y prod para mdoificar el url del qr
        
        urlqr = os.environ["URL_QR"]
        
        url_final = (
            {urlqr}
            + datos_qr +
            f"&cHashQR={hashQR}"
        )

        ET.SubElement(gCamFuFD, "dCarQR").text = url_final
        
    def _build_gCamFE(self,parent):
        gCamFE = ET.SubElement(parent, "gCamFE")
        
        ET.SubElement(gCamFE, "iIndPres").text = "1"
        ET.SubElement(gCamFE, "dDesIndPres").text = "Operación presencial"
        
        
