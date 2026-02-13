from datetime import datetime
import xml.etree.ElementTree as ET


def parse_lote_response(xml_bytes: bytes):
    ns = {
        "env": "http://www.w3.org/2003/05/soap-envelope",
        "ns2": "http://ekuatia.set.gov.py/sifen/xsd"
    }

    root = ET.fromstring(xml_bytes)

    body = root.find("env:Body", ns)
    response = body.find("ns2:rResEnviConsLoteDe", ns)

    # --- Cabecera lote ---
    fec_proc = response.find("ns2:dFecProc", ns).text
    cod_res_lot = response.find("ns2:dCodResLot", ns).text
    msg_res_lot = response.find("ns2:dMsgResLot", ns).text

    lote_data = {
        "fec_proc": datetime.fromisoformat(fec_proc),
        "cod_res_lot": cod_res_lot,
        "msg_res_lot": msg_res_lot,
        "detalles": []
    }

    # --- Documentos ---
    for item in response.findall("ns2:gResProcLote", ns):
        cdc = item.find("ns2:id", ns).text
        est_res = item.find("ns2:dEstRes", ns).text
        prot_aut = item.find("ns2:dProtAut", ns).text

        g_res_proc = item.find("ns2:gResProc", ns)
        cod_res = g_res_proc.find("ns2:dCodRes", ns).text
        msg_res = g_res_proc.find("ns2:dMsgRes", ns).text

        lote_data["detalles"].append({
            "cdc": cdc,
            "est_res": est_res,
            "prot_aut": prot_aut,
            "cod_res": cod_res,
            "msg_res": msg_res
        })

    return lote_data
