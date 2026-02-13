from lxml import etree
from sqlalchemy.orm import Session
from datetime import datetime

from domain.models.models import (
    Lote, Documento, LoteDocumento,
    ConsultaLote, ConsultaDocumento, Estado
)


def serviceResponseLote(db: Session, lote_id: int, xml_response: str):
    """
    Procesa el response SOAP de consulta/envío de lote SIFEN
    y persiste:
    - XML crudo en Lote
    - Resultado general en ConsultaLote
    - Resultado por CDC en LoteDocumento + Documento + Estado
    """

    # =====================
    # 1. Parsear XML
    # =====================
    root = etree.fromstring(xml_response.encode("utf-8"))
    ns = {
        "env": "http://www.w3.org/2003/05/soap-envelope",
        "ns2": "http://ekuatia.set.gov.py/sifen/xsd"
    }

    body = root.find("env:Body", ns)
    res = body.find("ns2:rResEnviConsLoteDe", ns)

    if res is None:
        raise ValueError("SOAP inválido: no existe rResEnviConsLoteDe")

    dFecProc = res.findtext("ns2:dFecProc", namespaces=ns)
    dCodResLot = res.findtext("ns2:dCodResLot", namespaces=ns)
    dMsgResLot = res.findtext("ns2:dMsgResLot", namespaces=ns)

    gResProcLote_nodes = res.findall("ns2:gResProcLote", ns)

    # =====================
    # 2. Obtener lote
    # =====================
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise ValueError(f"Lote {lote_id} no existe")

    lote.xml_response = xml_response
    lote.estado = "PROCESADO"
    db.add(lote)

    # =====================
    # 3. Guardar consulta lote
    # =====================
    consulta_lote = ConsultaLote(
        nro_lote=lote.nro_lote_sifen,
        cod_respuesta_lote=dCodResLot,
        msg_respuesta_lote=dMsgResLot,
        fecha_consulta=_parse_datetime(dFecProc),
    )
    db.add(consulta_lote)
    db.flush()  # para tener consulta_lote.id

    # =====================
    # 4. Procesar cada DE del lote
    # =====================
    for nodo in gResProcLote_nodes:
        cdc = nodo.findtext("ns2:id", namespaces=ns)
        estado_res = nodo.findtext("ns2:dEstRes", namespaces=ns)  # Aprobado / Rechazado
        prot_aut = nodo.findtext("ns2:dProtAut", namespaces=ns)

        gResProc = nodo.find("ns2:gResProc", ns)
        cod_res = gResProc.findtext("ns2:dCodRes", namespaces=ns) if gResProc is not None else None
        msg_res = gResProc.findtext("ns2:dMsgRes", namespaces=ns) if gResProc is not None else None

        # ---------------------
        # Buscar documento
        # ---------------------
        documento = db.query(Documento).filter(Documento.cdc_de == cdc).first()
        if not documento:
            # Esto es error grave de tu sistema: mandaste un CDC que no existe
            raise ValueError(f"CDC {cdc} no existe en de_documento")

        # ---------------------
        # Actualizar Documento
        # ---------------------
        if estado_res and estado_res.upper() == "APROBADO":
            documento.estado_actual = "APROBADO"
        else:
            documento.estado_actual = "RECHAZADO"

        documento.fecha_ultima_consulta = datetime.utcnow()
        documento.intentos_consulta = (documento.intentos_consulta or 0) + 1
        db.add(documento)

        # ---------------------
        # Historial de estados
        # ---------------------
        estado_hist = Estado(
            de_id=documento.id,
            dcodres=cod_res or "0000",
            dmsgres=msg_res or estado_res or "SIN MENSAJE",
            dfecproc=_parse_datetime(dFecProc),
        )
        db.add(estado_hist)

        # ---------------------
        # Relación lote-documento
        # ---------------------
        lote_doc = (
            db.query(LoteDocumento)
            .filter(
                LoteDocumento.lote_id == lote.id,
                LoteDocumento.documento_id == documento.id,
            )
            .first()
        )

        if not lote_doc:
            lote_doc = LoteDocumento(
                lote_id=lote.id,
                documento_id=documento.id,
                cdc=cdc,
            )

        lote_doc.estado_resultado = estado_res.upper() if estado_res else None
        lote_doc.codigo_error = cod_res
        lote_doc.mensaje_error = msg_res
        db.add(lote_doc)

        # ---------------------
        # Guardar consulta documento
        # ---------------------
        cons_doc = ConsultaDocumento(
            consulta_lote_id=consulta_lote.id,
            documento_id=documento.id,
            cdc=cdc,
        )
        db.add(cons_doc)

    db.commit()
    return True


def _parse_datetime(value: str | None):
    if not value:
        return None
    # Ej: 2026-01-27T13:14:34-03:00
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
