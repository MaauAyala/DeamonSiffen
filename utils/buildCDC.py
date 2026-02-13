from datetime import datetime
from domain.models.models import Documento
from utils.genDV import calcular_dv_11a


def _req(val, name):
    if val is None:
        raise ValueError(f"CDC ERROR → {name} viene None")
    return val


def _z(val, n, name):
    try:
        return str(int(val)).zfill(n)
    except Exception:
        raise ValueError(f"CDC ERROR → {name} inválido: {val}")


def buildCDC(db, doc: Documento):
    _req(doc, "doc")
    _req(doc.emisor, "doc.emisor")
    _req(doc.timbrado, "doc.timbrado")
    _req(doc.operacion, "doc.operacion")

    partes = {}

    partes["tipo_doc"] = _z(_req(doc.tipo_doc, "doc.tipo_doc"), 2, "tipo_doc")
    partes["ruc"] = _z(_req(doc.drucem, "doc.drucem"), 8, "drucem")
    partes["dv"] = str(_req(doc.emisor.ddvemi, "doc.emisor.ddvemi"))
    partes["est"] = _z(_req(doc.timbrado.dest, "doc.timbrado.dest"), 3, "dest")
    partes["punto"] = _z(_req(doc.timbrado.dpunexp, "doc.timbrado.dpunexp"), 3, "dpunexp")
    partes["nro"] = _z(_req(doc.dnumdoc, "doc.dnumdoc"), 7, "dnumdoc")
    partes["tipcont"] = str(_req(doc.emisor.itipcont, "doc.emisor.itipcont"))

    fecha = _req(doc.dfeemide, "doc.dfeemide")
    if not isinstance(fecha, datetime):
        raise ValueError(f"CDC ERROR → dfeemide no es datetime: {fecha}")
    partes["fecha"] = fecha.strftime("%Y%m%d")

    partes["tipemi"] = str(_req(doc.operacion.itipemi, "doc.operacion.itipemi"))
    partes["codseg"] = _z(_req(doc.operacion.dcodseg, "doc.operacion.dcodseg"), 9, "dcodseg")

    cdc = "".join(partes.values())

    dv =calcular_dv_11a(cdc)
    
    doc.cdc_de = cdc+dv
    doc.ddvid = dv
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return cdc, partes  # ← devolvemos partes para debug
