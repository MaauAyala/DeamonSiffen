from sqlalchemy import Column, Integer, String, Date, Numeric,Boolean , ForeignKey, SmallInteger, TIMESTAMP, func, Text
from sqlalchemy.orm import relationship, declarative_base
from core.database import Base


class Documento(Base):
    __tablename__ = "de_documento"
    id = Column(Integer, primary_key=True, index=True)
    cdc_de = Column(String(44), unique=True , nullable=False)
    dverfor = Column(Integer)
    ddvid = Column(Integer)
    dfecfirma = Column(TIMESTAMP)
    dnumdoc = Column(Integer)
    dsisfact = Column(SmallInteger)
    dfeemide = Column(TIMESTAMP, nullable=False)
    estado_actual = Column(String(50), default='PENDIENTE_ENVIO')
    fecha_ultima_consulta = Column(TIMESTAMP)
    intentos_consulta = Column(Integer, default=0)
    dserienum = Column(String(2))
    drucem = Column(String(8))
    idtimbrado = Column(Integer)
    #iIndPres = Column(Integer)
    #dDesIndPres = Column(String(20))

    # Relaciones 
    operacion = relationship("Operacion", back_populates="documento", uselist=False)
    receptor = relationship("Receptor", back_populates="documento", uselist=False)
    items = relationship("Item", back_populates="documento")
    totales = relationship("Totales", back_populates="documento", uselist=False)
    operacion_comercial = relationship("OperacionComercial", back_populates="documento", uselist=False)
    nota_credito_debito = relationship("NotaCreditoDebito", back_populates="documento", uselist=False)
    estados = relationship("Estado", back_populates="documento")  # Historial de estados
    consultas = relationship("ConsultaDocumento", back_populates="documento") 
    campos_fuera = relationship("CamposFueraFirma",back_populates="documento")# Consultas realizadas
    lotes = relationship("LoteDocumento", back_populates="documento")
    


class Operacion(Base):
    __tablename__ = "de_operacion"
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    itipemi = Column(SmallInteger)
    ddestipemi = Column(String(12))
    dcodseg = Column(String(9))
    dinfoemi = Column(String(3000))
    dinfofisc = Column(String(3000))
    icondope = Column(Integer)  # 1=Contado, 2=Crédito
    ddcondope = Column(String(200))

    documento = relationship("Documento", back_populates="operacion")

    __mapper_args__ = {
        "polymorphic_on": icondope,
        "polymorphic_identity": 0,  # base
        "with_polymorphic": "*"
    }



class Timbrado(Base):
    __tablename__ = "de_timbrado"
    id = Column(Integer, primary_key=True)
    itide = Column(SmallInteger)
    ddestide = Column(String(50))
    dnumtim = Column(String(20))
    dest = Column(String(5))
    dpunexp = Column(String(5))
    dfeinit = Column(Date)
    activo = Column(Boolean)


class Emisor(Base):
    __tablename__ = "de_emisor"
    id = Column(Integer, primary_key=True)
    
    # Campos según especificación D100-D129
    drucem = Column(String(8), nullable=False)  # D101: RUC (3-8 caracteres)
    ddvemi = Column(SmallInteger, nullable=False)  # D102: Dígito verificador
    itipcont = Column(SmallInteger, nullable=False)  # D103: Tipo contribuyente (1,2)
    ctipreg = Column(SmallInteger)  # D104: Tipo régimen (1-2 dígitos) - OPCIONAL
    dnomemi = Column(String(255), nullable=False)  # D105: Nombre/Razón social
    dnomfanemi = Column(String(255))  # D106: Nombre fantasía (opcional)
    ddiremi = Column(String(255), nullable=False)  # D107: Dirección principal
    dnumcas = Column(String(6), nullable=False)  # D108: Número casa (1-6 caracteres)
    dcompdir1 = Column(String(255))  # D109: Complemento dirección 1 (opcional)
    dcompdir2 = Column(String(255))  # D110: Complemento dirección 2 (opcional)
    cdepemi = Column(SmallInteger, nullable=False)  # D111: Código departamento
    ddesdepemi = Column(String(16), nullable=False)  # D112: Descripción departamento (6-16 chars)
    cdisemi = Column(SmallInteger)  # D113: Código distrito (opcional)
    ddesdisemi = Column(String(30))  # D114: Descripción distrito (opcional)
    cciuemi = Column(SmallInteger, nullable=False)  # D115: Código ciudad emisión
    ddesciuemi = Column(String(30), nullable=False)  # D116: Descripción ciudad emisión
    
    # Campos adicionales según especificación
    dtelemi = Column(String(15), nullable=False)  # D117: Teléfono (6-15 caracteres)
    demaile = Column(String(80), nullable=False)  # D118: Email (3-80 caracteres)
    ddensuc = Column(String(30))  # D119: Denominación comercial sucursal (opcional)
    
    actividades = relationship("EmisorActividad", back_populates="emisor")

class EmisorActividad(Base):
    __tablename__ = "de_emisor_actividad"
    id = Column(Integer, primary_key=True)
    emisor_id = Column(Integer, ForeignKey("de_emisor.id", ondelete="CASCADE"))
    cacteco = Column(String(20), nullable=False)
    ddesacteco = Column(String(255), nullable=False)
    
    emisor = relationship("Emisor", back_populates="actividades")
class Receptor(Base):
    __tablename__ = "de_receptor"

    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))

    # D201 - Naturaleza del receptor (1 contribuyente, 2 no contribuyente)
    inatrec = Column(SmallInteger, nullable=False)
    # D202 - Tipo de operación (1 B2B, 2 B2C, 3 B2G, 4 B2F)
    itiope = Column(SmallInteger, nullable=False)
    # D203 / D204 - País del receptor
    cpaisrec = Column(String(10), nullable=False)
    ddespaisre = Column(String(50), nullable=False)
    # D205 - Tipo de contribuyente receptor (solo si inatrec = 1)
    iticontrec = Column(SmallInteger)
    # D206 / D207 - RUC y DV
    drucrec = Column(String(20))
    ddvrec = Column(SmallInteger)
    # ⚠️ D208 / D209 / D210 - Tipo de documento, descripción y número
    # (Obligatorio si NO es contribuyente)
    itipidrec = Column(SmallInteger)
    ddtipidrec = Column(String(50))
    dnumidrec = Column(String(20))
    # D211 - Nombre o razón social
    dnomrec = Column(String(255), nullable=False)
    # D212 - Nombre de fantasía (opcional)
    dnomfanrec = Column(String(255))
    # D213 - Dirección
    ddirrec = Column(String(255))
    # D218 - Número de casa
    dnumcasrec = Column(String(10))
    # D219 / D220 - Departamento
    cdeprec = Column(SmallInteger)
    ddesdeprec = Column(String(50))
    # D221 / D222 - Distrito
    cdisrec = Column(SmallInteger)
    ddesdisrec = Column(String(50))
    # D223 / D224 - Ciudad
    cciurec = Column(SmallInteger)
    ddesciurec = Column(String(50))
    # D214 - Teléfono
    dtelrec = Column(String(50))
    # D215 - Celular
    dcelrec = Column(String(20))
    # D216 - Email
    demailrec = Column(String(80))
    # D217 - Código interno del cliente (opcional)
    dcodcliente = Column(String(50))

    

    documento = relationship("Documento", back_populates="receptor")


class Item(Base):
    __tablename__ = "de_item"
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    dcodint = Column(String(50))
    ddesproser = Column(String(255))
    cunimed = Column(String(10))
    ddesunimed = Column(String(20))
    dcantproser = Column(Numeric(15, 2))
    dinfitem = Column(String(100))
    dpuniproser = Column(Numeric(15, 2))
    dtotbruopeitem = Column(Numeric(15, 2))
    ddescitem = Column(Numeric(15, 2))
    dporcdesit = Column(Numeric(6, 2))
    ddescgloitem = Column(Numeric(15, 2))
    dtotopeitem = Column(Numeric(15, 2))
    #ItemIVa
    iafeciva = Column(SmallInteger)
    ddesafeciva = Column(String(50))
    dpropiva = Column(Numeric(6, 2))
    dtasaiva = Column(Numeric(6, 2))
    dbasgraviva = Column(Numeric(15, 2))
    dliqivaitem = Column(Numeric(15, 2))
    dbasexe = Column(Numeric(15, 2), default=0)

    documento = relationship("Documento", back_populates="items")


class Totales(Base):
    __tablename__ = "de_totales"
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    dsubexe = Column(Numeric(15,2))
    dsubexo = Column(Numeric(15,2))
    dsub5 = Column(Numeric(15,2))
    dsub10 = Column(Numeric(15,2))
    dtotope = Column(Numeric(15,2))
    dtotdesc = Column(Numeric(15,2))
    dtotdescglotem = Column(Numeric(15,2))
    dtotantitem = Column(Numeric(15,2))
    dtotant = Column(Numeric(15,2))
    dporcdesctotal = Column(Numeric(precision=11, scale=8), nullable=False, default=0)
    ddesctotal = Column(Numeric(15,2))
    danticipo = Column(Numeric(15,2))
    dredon = Column(Numeric(15,2))
    dtotgralope = Column(Numeric(15,2))
    diva5 = Column(Numeric(15,2))
    diva10 = Column(Numeric(15,2))
    dtotiva = Column(Numeric(15,2))
    dbasegrav5 = Column(Numeric(15,2))
    dbasegrav10 = Column(Numeric(15,2))
    dtbasgraiva = Column(Numeric(15,2))

    documento = relationship("Documento", back_populates="totales")

class OperacionComercial(Base):
    __tablename__ = "de_operacion_comercial"
    
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    itiptra = Column(SmallInteger)
    ddestiptra = Column(String(36))
    itimp = Column(SmallInteger, nullable=False)
    ddestimp = Column(String(11), nullable=False)
    cmoneope = Column(String(3), nullable=False)
    ddesmoneope = Column(String(20), nullable=False)
    dcondticam = Column(SmallInteger)
    dticam = Column(Numeric(9, 4))
    icondant = Column(SmallInteger)
    ddescondant = Column(String(17))
    
    documento = relationship("Documento", back_populates="operacion_comercial")
    
class NotaCreditoDebito(Base):
    __tablename__ = "de_nota_credito_debito"
    
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    imotemi = Column(SmallInteger, nullable=False)  # E401: Motivo de emisión (1-8)
    ddesmotemi = Column(String(30), nullable=False)  # E402: Descripción motivo
    
    # Campos referenciados a la factura original
    dnumtim_ref = Column(String(20))  # Número de timbrado del documento referenciado
    dest_ref = Column(String(5))      # Establecimiento del documento referenciado
    dpunexp_ref = Column(String(5))   # Punto de expedición del documento referenciado
    dnumdoc_ref = Column(String(20))  # Número del documento referenciado
    
    documento = relationship("Documento", back_populates="nota_credito_debito")
    
    
class Evento(Base):
    __tablename__ = "de_eventos"
    
    id = Column(Integer, primary_key=True)
    dfecfirma = Column(TIMESTAMP, nullable=False)   # GDE004
    dverfor = Column(Integer, nullable=False)       # GDE005
    dtigde = Column(Integer, nullable=False)        # GDE006: 1=Cancelación, 2=Inutilización
    
    # Campos para CANCELACIÓN (dtigde = 1)
    cdc_dte = Column(String(44))                    # GEC002: CDC del DTE
    mototeve  = Column(Text)                         # GEC003: Motivo
    
    # Campos para INUTILIZACIÓN (dtigde = 2)
    dnumtim = Column(String(8))                     # GEI002: Número del Timbrado
    dest = Column(String(3))                        # GEI003: Establecimiento
    dpunexp = Column(String(3))                     # GEI004: Punto de expedición
    dnumin = Column(String(7))                      # GEI005: Número Inicio del rango
    dnumfin = Column(String(7))                     # GEI006: Número Final del rango
    itide = Column(SmallInteger)                    # GEI007: Tipo de Documento Electrónico
    

    created_at = Column(TIMESTAMP, default=func.now())
    

    

class Estado(Base):
    __tablename__ = "de_estado"

    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    dcodres = Column(String(10), nullable=False)          # Código del resultado (ej: 0301)
    dmsgres = Column(String(255), nullable=False)         # Mensaje del resultado
    dfecproc = Column(TIMESTAMP, default=func.now())      # Fecha/hora del procesamiento

    documento = relationship("Documento", back_populates="estados")
 

class ConsultaLote(Base):
    __tablename__ = "de_consulta_lote"
    
    id = Column(Integer, primary_key=True)
    nro_lote = Column(String(15), nullable=False)            # Número de lote consultado
    fecha_consulta = Column(TIMESTAMP, default=func.now())
    cod_respuesta_lote = Column(Integer)                     # 0360, 0361, 0362
    msg_respuesta_lote = Column(String(255))
    
    # Relación con documentos consultados
    documentos_consultados = relationship("ConsultaDocumento", back_populates="consulta_lote")

class ConsultaDocumento(Base):
    __tablename__ = "de_consulta_documento"
    
    id = Column(Integer, primary_key=True)
    consulta_lote_id = Column(Integer, ForeignKey("de_consulta_lote.id"))
    documento_id = Column(Integer, ForeignKey("de_documento.id"))
    cdc = Column(String(44), nullable=False)
    
    consulta_lote = relationship("ConsultaLote", back_populates="documentos_consultados")
    documento = relationship("Documento")
    
    
class CamposFueraFirma(Base):
    __tablename__ = "de_campos_fuera_fe"
    
    id = Column(Integer, primary_key=True)
    documento_id = Column(Integer, ForeignKey("de_documento.id"))
    dcarqr = Column(String(600),nullable=True)
    dinfadic = Column(String(5000),nullable=True)
    
    documento = relationship("Documento")
    
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)  
    password_hash = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)  
    created_at = Column(TIMESTAMP, default=func.now())
    
class OperacionContado(Operacion):
    itipago = Column(Integer, nullable=True)
    ddestipag = Column(String(20), nullable=True)
    dmontipag = Column(Numeric(15, 4), nullable=True)
    cmonetipag = Column(String(3), nullable=True)
    ddmonetipag = Column(String (20))
    dticamtipag = Column(Numeric(5,4))

    # Subpagos
    pago_tarjeta = relationship(
        "PagoTarjeta", 
        uselist=False, 
        back_populates="operacion_contado",
        foreign_keys="PagoTarjeta.operacion_id"
    )
    
    pago_cheque = relationship(
        "PagoCheque", 
        uselist=False, 
        back_populates="operacion_contado",
        foreign_keys="PagoCheque.operacion_id"
    )

    __mapper_args__ = {
        "polymorphic_identity": 1
    }

#Sub pago Credito
class OperacionCredito(Operacion):
    icondcred = Column(Integer, nullable=True)  # 1=Plazo, 2=Cuota
    dplazocre = Column(String(15), nullable=True)
    dcuotas = Column(Integer, nullable=True)
    dmonent = Column(Numeric(15, 4), nullable=True)

    cuotas = relationship("Cuota", back_populates="operacion_credito", cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": 2
    }


class PagoTarjeta(Base):
    __tablename__ = "pagos_tarjeta"

    id = Column(Integer, primary_key=True)
    operacion_id = Column(Integer, ForeignKey("de_operacion.id"))
    
    # E621
    identarj = Column(Integer, nullable=False)
    # 1=Visa, 2=Mastercard, 3=Amex, 4=Maestro, 5=Panal, 6=Cabal, 99=Otro
    # E622
    ddesdentarj = Column(String(20), nullable=False)
    # E623
    drsprotar = Column(String(60))
    # E624
    drucprotar = Column(String(8))
    # E625
    ddvprotar = Column(Integer)
    # E626
    iforpropa = Column(Integer, nullable=False)
    # 1=POS, 2=Pago Electrónico, 9=Otro
    # E627
    dcodauope = Column(String(10))
    # E628
    dnomtit = Column(String(30))
    # E629
    dnumtarj = Column(String(4))  # últimos 4 dígitos
    
    operacion_contado = relationship("OperacionContado", back_populates="pago_tarjeta")


class PagoCheque(Base):
    __tablename__ = "pagos_cheque"

    id = Column(Integer, primary_key=True)
    operacion_id = Column(Integer, ForeignKey("de_operacion.id"))
    
    # E631
    dnumcheq = Column(String(8), nullable=False)
    # completar con ceros a la izquierda (validar en schema)

    # E632
    dbcoemi = Column(String(20), nullable=False)
    
    operacion_contado = relationship("OperacionContado", back_populates="pago_cheque")
class Cuota(Base):
    __tablename__ = "cuotas"
    id = Column(Integer, primary_key=True)
    operacion_id = Column(Integer, ForeignKey("de_operacion.id"))
    cmonetcuo = Column(String(3), nullable=False)
    ddmonetcuo = Column(String(20), nullable=False)
    dmoncuota = Column(Numeric(15, 4), nullable=False)
    dvenccuo = Column(String(10))

    operacion_credito = relationship("OperacionCredito", back_populates="cuotas")


class Lote(Base):
    __tablename__ = "de_lote"

    id = Column(Integer, primary_key=True)
    nro_lote_sifen = Column(String(15), unique=True, nullable=True)
    estado = Column(String(30), default="ENVIADO")  
    fecha_envio = Column(TIMESTAMP, default=func.now())
    xml_request = Column(Text)
    xml_response = Column(Text)
    
    documentos = relationship("LoteDocumento", back_populates="lote")


class LoteDocumento(Base):
    __tablename__ = "de_lote_documento"

    id = Column(Integer, primary_key=True)
    lote_id = Column(Integer, ForeignKey("de_lote.id", ondelete="CASCADE"))
    documento_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    cdc = Column(String(44), nullable=False)

    estado_resultado = Column(String(30))     # APROBADO / RECHAZADO
    codigo_error = Column(String(10))
    mensaje_error = Column(String(255))
    
    lote = relationship("Lote", back_populates="documentos")
    documento = relationship("Documento", back_populates="lotes")
