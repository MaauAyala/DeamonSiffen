from datetime import datetime
import xml.etree.ElementTree as ET


def _get_text(parent, path, ns):
    node = parent.find(path, ns)
    return node.text if node is not None else None


def parse_lote_response(xml_bytes: bytes):
    ns = {
        "env": "http://www.w3.org/2003/05/soap-envelope",
        "ns2": "http://ekuatia.set.gov.py/sifen/xsd"
    }

    root = ET.fromstring(xml_bytes)

    body = root.find("env:Body", ns)
    if body is None:
        raise ValueError("SOAP Body no encontrado")

    response = body.find("ns2:rResEnviConsLoteDe", ns)
    if response is None:
        raise ValueError("rResEnviConsLoteDe no encontrado")

    # --- Cabecera lote ---
    fec_proc_raw = _get_text(response, "ns2:dFecProc", ns)
    cod_res_lot = _get_text(response, "ns2:dCodResLot", ns)
    msg_res_lot = _get_text(response, "ns2:dMsgResLot", ns)

    lote_data = {
        "fec_proc": datetime.fromisoformat(fec_proc_raw) if fec_proc_raw else None,
        "cod_res_lot": cod_res_lot,
        "msg_res_lot": msg_res_lot,
        "detalles": []
    }

    # --- Documentos ---
    for item in response.findall("ns2:gResProcLote", ns):

        cdc = _get_text(item, "ns2:id", ns)
        est_res = _get_text(item, "ns2:dEstRes", ns)
        prot_aut = _get_text(item, "ns2:dProtAut", ns)

        g_res_proc = item.find("ns2:gResProc", ns)

        cod_res = None
        msg_res = None

        if g_res_proc is not None:
            cod_res = _get_text(g_res_proc, "ns2:dCodRes", ns)
            msg_res = _get_text(g_res_proc, "ns2:dMsgRes", ns)

        lote_data["detalles"].append({
            "cdc": cdc,
            "est_res": est_res,
            "prot_aut": prot_aut,
            "cod_res": cod_res,
            "msg_res": msg_res
        })

    return lote_data