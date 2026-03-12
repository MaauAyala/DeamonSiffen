import xml.etree.ElementTree as ET

def format_miles(value: str):
    if value is None:
        return None
    try:
        num = float(value)
        # Paraguay usa coma decimal y punto miles
        return f"{num:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return value
def parse_sifen_xml(xml_string: str) -> dict:
    ns = {"s": "http://ekuatia.set.gov.py/sifen/xsd"}

    root = ET.fromstring(xml_string)
    de = root.find("s:DE", ns)

    if de is None:
        raise ValueError("No se encontró el nodo DE")

    cdc = de.attrib.get("Id")

    timb = de.find("s:gTimb", ns)
    gDtipDE =de.find("s:gDtipDE",ns)
    gOpeDE = de.find("s:gOpeDE",ns)
    gCamCond =gDtipDE.find("s:gCamCond",ns)

    dat_gral = de.find("s:gDatGralOpe", ns)
    gOpeCom = dat_gral.find("s:gOpeCom",ns)
    emis = dat_gral.find("s:gEmis", ns)
    rec = dat_gral.find("s:gDatRec", ns)
    totales = de.find("s:gTotSub", ns)
    complementos = de.find("s:gCamGen",ns)

    
    actividades = []

    act_nodes = emis.findall("s:gActEco", ns)

    for act in act_nodes:
        actividades.append({
            "codigo": act.findtext("s:cActEco", default=None, namespaces=ns),
            "descripcion": act.findtext("s:dDesActEco", default=None, namespaces=ns),
        })
    # ------------------------
    # PRODUCTOS
    # ------------------------
    items = []
    items_nodes = de.findall("s:gDtipDE/s:gCamItem", ns)

    for item in items_nodes:
        valor_item = item.find("s:gValorItem", ns)
        iva_item = item.find("s:gCamIVA", ns)

        items.append({
            "codigo": item.findtext("s:dCodInt", default=None, namespaces=ns),
            "descripcion": item.findtext("s:dDesProSer", default=None, namespaces=ns),
            "unidad": item.findtext("s:dDesUniMed", default=None, namespaces=ns),
            "cantidad": item.findtext("s:dCantProSer", default=None, namespaces=ns),
            "infoitem": item.findtext("s:dInfItem", default=None, namespaces=ns),
            "precio_unitario": format_miles(valor_item.findtext("s:dPUniProSer", default=None, namespaces=ns)),
            "total_bruto": valor_item.findtext("s:dTotBruOpeItem", default=None, namespaces=ns),
            "total_item": valor_item.findtext("s:gValorRestaItem/s:dTotOpeItem", default=None, namespaces=ns),
            "exentas": valor_item.findtext("s:dSubExe", default=None, namespaces=ns),
            "iva": {
                "tipo_afectacion": iva_item.findtext("s:dDesAfecIVA", default=None, namespaces=ns),
                "tasa": iva_item.findtext("s:dTasaIVA", default=None, namespaces=ns),
                "base_gravada": iva_item.findtext("s:dBasGravIVA", default=None, namespaces=ns),
                "liquidacion_iva": iva_item.findtext("s:dLiqIVAItem", default=None, namespaces=ns),
                "sub10": format_miles(totales.findtext("s:dSub10", default=None, namespaces=ns)),
            }
        })

    # ------------------------
    # QR
    # ------------------------
    qr_node = root.find("s:gCamFuFD/s:dCarQR", ns)
    qr_url = qr_node.text if qr_node is not None else None

    data = {
        "cdc": cdc,
        "fecha_emision": dat_gral.findtext("s:dFeEmiDE", default=None, namespaces=ns),
        "tipo_factura": timb.findtext("s:dDesTiDE",default=None,namespaces=ns),
        "condicion_venta":gCamCond.findtext("s:dDCondOpe",default=None,namespaces=ns),
        "descr_moneda":gOpeCom.findtext("s:dDesMoneOpe",default=None,namespaces=ns),
        "tipo_operacion":gOpeCom.findtext("s:dDesTipTra",default=None,namespaces=ns),
        "infoemi":gOpeDE.findtext("s:dInfoEmi",default=None,namespaces=ns),
        
        "timbrado": {
            "numero_timbrado": timb.findtext("s:dNumTim", default=None, namespaces=ns),
            "establecimiento": timb.findtext("s:dEst", default=None, namespaces=ns),
            "punto_expedicion": timb.findtext("s:dPunExp", default=None, namespaces=ns),
            "numero_documento": timb.findtext("s:dNumDoc", default=None, namespaces=ns),
            "serie": timb.findtext("s:dSerieNum", default=None, namespaces=ns),
            "inicio_vigencia":timb.findtext("s:dFeIniT", default=None, namespaces=ns),
        },

        "emisor": {
            "ruc": emis.findtext("s:dRucEm", default=None, namespaces=ns),
            "dv": emis.findtext("s:dDVEmi", default=None, namespaces=ns),
            "nombre": emis.findtext("s:dNomEmi", default=None, namespaces=ns),
            "direccion": emis.findtext("s:dDirEmi", default=None, namespaces=ns),
            "telefono": emis.findtext("s:dTelEmi", default=None, namespaces=ns),
            "email": emis.findtext("s:dEmailE", default=None, namespaces=ns),
            "actividades":actividades,
        },

        "receptor": {
            "ruc": rec.findtext("s:dRucRec", default=None, namespaces=ns),
            "dv": rec.findtext("s:dDVRec", default=None, namespaces=ns),
            "nombre": rec.findtext("s:dNomRec", default=None, namespaces=ns),
            "telefono": rec.findtext("s:dCelRec", default=None, namespaces=ns),
            "email": rec.findtext("s:dEmailRec", default=None, namespaces=ns),
        },

        "items": items,

        "totales": {
            "total_operacion": format_miles(totales.findtext("s:dTotGralOpe", default=None, namespaces=ns)),
            "total_iva": format_miles(totales.findtext("s:dTotIVA", default=None, namespaces=ns)),
            "iva_10": format_miles(totales.findtext("s:dIVA10", default=None, namespaces=ns)),
            "base_gravada_10":format_miles( totales.findtext("s:dBaseGrav10", default=None, namespaces=ns)),
        },
        # "complementos":{
        #   #"orden_compra":complementos.findtext("s:dOrdCompra",default=None,namespaces=ns), 
        #   "orden_venta": complementos.findtext("s:dOrdVta",default=None,namespaces=ns),
        #   "aasiento": complementos.findtext("s:dAsiento",default=None,namespaces=ns),
        # },

        "qr_url": qr_url
    }

    return data
