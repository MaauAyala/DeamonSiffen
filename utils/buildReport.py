from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib import pagesizes
import qrcode
import os
from reportlab.lib.styles import ParagraphStyle


logo = Image("FacturApp.jpeg", width=43*mm, height=26*mm)
MIN_FILAS = 22

normal_item = ParagraphStyle(
    name="NormalItem",
    fontSize=8,
    leading=10
)

def generar_pdf_factura(data: dict, output_path="factura.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=pagesizes.A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    elements = []

    # ----------------------------
    # Estilos
    # ----------------------------
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        name="NormalSmall",
        parent=styles["Normal"],
        fontSize=9,
        leading=11
    )
    bold_style = ParagraphStyle(
        name="Bold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12
    )

    # ----------------------------
    # HEADER
    # ----------------------------
    actividades_texto = "<br/>".join(
    [f"{act['descripcion']}" 
     for act in data['emisor']['actividades']]
    )
    emisor_block = Table([
    [Paragraph(f"<b>{data['emisor']['nombre']}</b>", bold_style)],
    [logo]
    
    
    ])
    actividades_block = Table([
        [Paragraph("<b>Actividades económicas:</b>", bold_style)],
        [Paragraph(actividades_texto, normal)]
    ])
    
    emisor_block.setStyle([
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ])

    actividades_block.setStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ])
    
    header_data = [
        [
            emisor_block,
            Spacer(1, 10),
            actividades_block,
            Paragraph(f"""
            <b>RUC:</b> {data['emisor']['ruc']}-{data['emisor']['dv']}<br/>
            <b>Timbrado:</b> {data['timbrado']['numero_timbrado']}<br/>
            <b>Inicio de Vigencia:</b> {data['timbrado']["inicio_vigencia"]}<br/>
            <b>{data['tipo_factura']}</b> <br/>
            <b>N°:</b> {data['timbrado']['establecimiento']}-\
{data['timbrado']['punto_expedicion']}-\
{data['timbrado']['numero_documento']}
            """, normal)
        ]
    ]


    header_table = Table(header_data, colWidths=[80*mm, 10*mm, 60*mm, 50*mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOX", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    header_table.setStyle([
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ])
    elements.append(header_table)
    elements.append(Spacer(1, 5))

    # ----------------------------
    # RECEPTOR
    # ----------------------------
    receptor_data = [
        [
            Paragraph(f"""
        <b>Fecha y Hora de Emisión:</b> {data['fecha_emision']}<br/>
        <b>RUC/documento de identidad:</b> {data['receptor']['ruc']}-{data['receptor']['dv']}<br/>
        <b>Moneda:</b> {data['descr_moneda']}<br/>
        <b>Tipo de Cambio:</b> <br/>
        <b>Tipo de operación:</b> {data['tipo_operacion']}<br/>
        <b>Email:</b> {data['receptor']['email']}<br/>
        
        """, normal),
        Paragraph(f"""
        <b>Condición de Venta:</b> {data['condicion_venta']}<br/>
        <b>Nombre o razón social:</b> {data['receptor']['nombre']}<br/>
        <b>Dirección:</b> <br/>
        <b>Teléfono:</b> {data['receptor']['telefono']}<br/>
        <b>Info : </b> {data['infoemi']}
                   """,normal)
        ]
    ]

    receptor_table = Table(receptor_data, colWidths=[100*mm])
    receptor_table.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.white),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(receptor_table)
    elements.append(Spacer(1, 10))

    # ----------------------------Código Descripción Precio unitario Cantidad Exentas 5% 10%
    # TABLA DE ÍTEMS
    # ----------------------------
    table_data = [
        ["Código", "Descripción", "Precio unitario", "Cantidad.", "Exentas", "5% ", "10%"]
    ]

    for item in data["items"]:
        table_data.append([
            item["codigo"],
            Paragraph(item["descripcion"], normal_item),
            #Paragraph(item["infoitem"], normal_item),
            item["precio_unitario"],
            item["cantidad"],
            "0",
            "0",
            item['iva']['sub10'],
        ])
    while len(table_data) - 1 < MIN_FILAS:
        table_data.append(["", "", "", "", "", "", ""])

    items_table = Table(table_data, repeatRows=1, colWidths=[
        15*mm, 80*mm, 30*mm, 15*mm, 15*mm, 15*mm, 30*mm
    ])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("ALIGN", (3,1), (-1,-1), "RIGHT"),  # Cant., P.Unit, IVA, Total
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # TOTALES
    # ----------------------------
    totales_data = [
        ["Total Operación:", data["totales"]["total_operacion"]],
        ["Total IVA:", data["totales"]["total_iva"]],
        ["IVA 10%:", data["totales"]["iva_10"]],
        ["Base Gravada 10%:", data["totales"]["base_gravada_10"]],
    ]
    totales_table = Table(totales_data, colWidths=[170*mm, 30*mm])
    totales_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(totales_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # QR + CDC
    # ----------------------------
    qr_path = None
    if data.get("qr_url"):
        qr = qrcode.make(data["qr_url"])
        qr_path = "qr_temp.png"
        qr.save(qr_path)

        imageqr = Image(qr_path, width=30*mm, height=30*mm)
        cdc_paragraph = Paragraph(f"""
                                  Consulte la validez de esta Factura Electrónica con el número de CDC impreso abajo en:
https://ekuatia.set.gov.py/consultas<br/>
                                  {data.get('cdc', '')}<br/>
                                  ESTE DOCUMENTO ES UNA REPRESENTACIÓN GRÁFICA DE UN DOCUMENTO ELECTRÓNICO (XML)
                                  """, normal)

        qrtable = Table([[imageqr, cdc_paragraph]], colWidths=[45*mm, 155*mm])
        qrtable.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("BOX", (0,0), (-1,-1), 0.5, colors.black),

            # Padding general
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),

            # QR (columna 0)
            ("LEFTPADDING", (0,0), (0,0), 6),
            ("RIGHTPADDING", (0,0), (0,0), 0),
            
            ("LEFTPADDING", (0,0), (0,0), 0),   # menos espacio a la izquierda
            ("RIGHTPADDING", (1,0), (1,0), 6),
        ]))
        elements.append(qrtable)

    # ----------------------------
    # BUILD
    # ----------------------------
    doc.build(elements)

    # borrar el QR temporal
    if qr_path and os.path.exists(qr_path):
        os.remove(qr_path)