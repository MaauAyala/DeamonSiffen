from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Date, Numeric, ForeignKey, SmallInteger, TIMESTAMP, func, Text
from sqlalchemy.orm import relationship
from core.database import Base

class Documento(Base):
    __tablename__ = "de_documento"
    id = Column(Integer, primary_key=True, index=True)
    cdc_de = Column(String(44), unique=True , nullable=False)
    id_de = Column(String(100), unique=True, nullable=False)
    dverfor = Column(Integer)
    ddvid = Column(Integer)
    dfecfirma = Column(TIMESTAMP)
    dsisfact = Column(SmallInteger)
    dfeemide = Column(TIMESTAMP, nullable=False)
    estado_actual = Column(String(50), default='PENDIENTE_ENVIO')
    fecha_ultima_consulta = Column(TIMESTAMP)
    intentos_consulta = Column(Integer, default=0)
    nro_lote = Column(String(15))

    # Relaciones 
    operacion = relationship("Operacion", back_populates="documento", uselist=False)
    timbrado = relationship("Timbrado", back_populates="documento", uselist=False)
    emisor = relationship("Emisor", back_populates="documento", uselist=False)
    receptor = relationship("Receptor", back_populates="documento", uselist=False)
    items = relationship("Item", back_populates="documento")
    totales = relationship("Totales", back_populates="documento", uselist=False)
    operacion_comercial = relationship("OperacionComercial", back_populates="documento", uselist=False)
    nota_credito_debito = relationship("NotaCreditoDebito", back_populates="documento", uselist=False)
    eventos = relationship("Evento", back_populates="documento")
    estados = relationship("Estado", back_populates="documento")  # Historial de estados
    consultas = relationship("ConsultaDocumento", back_populates="documento")  # Consultas realizadas
    campos_fuera = relationship("CamposFueraFirma",back_populates="documento")# Consultas realizadas


class Operacion(Base):
    __tablename__ = "de_operacion"
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    itipemi = Column(SmallInteger)
    ddestipemi = Column(String(12))
    dcodseg = Column(String(9))
    dinfoemi = Column(String(3000))
    dinfofisc = Column(String(3000))

    documento = relationship("Documento", back_populates="operacion")


class Timbrado(Base):
    __tablename__ = "de_timbrado"
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    itide = Column(SmallInteger)
    ddestide = Column(String(50))
    dnumtim = Column(String(20))
    dest = Column(String(5))
    dpunexp = Column(String(5))
    dnumdoc = Column(String(20))
    dserienum = Column(String(10))
    dfeinit = Column(Date)

    documento = relationship("Documento", back_populates="timbrado")

class Emisor(Base):
    __tablename__ = "de_emisor"
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    
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
    cciuremi = Column(SmallInteger, nullable=False)  # D115: Código ciudad emisión
    ddesciuremi = Column(String(30), nullable=False)  # D116: Descripción ciudad emisión
    
    # Campos adicionales según especificación
    dtelem = Column(String(15), nullable=False)  # D117: Teléfono (6-15 caracteres)
    demail = Column(String(80), nullable=False)  # D118: Email (3-80 caracteres)
    ddensuc = Column(String(30))  # D119: Denominación comercial sucursal (opcional)

    actividades = relationship("EmisorActividad", back_populates="emisor")
    documento = relationship("Documento", back_populates="emisor")

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
    inatrec = Column(SmallInteger)
    itiope = Column(SmallInteger)
    cpaisrec = Column(String(10))
    ddespaisre = Column(String(50))
    iticontrec = Column(SmallInteger)
    drucrec = Column(String(20))
    ddvrec = Column(SmallInteger)
    dnomrec = Column(String(255))
    ddirrec = Column(String(255))
    dnumcasrec = Column(String(10))
    cdeprec = Column(SmallInteger)
    ddesdeprec = Column(String(50))
    cdisrec = Column(SmallInteger)
    ddesdisrec = Column(String(50))
    cciurec = Column(SmallInteger)
    ddesciurec = Column(String(50))
    dtelrec = Column(String(50))
    dcodcliente = Column(String(50))

    documento = relationship("Documento", back_populates="receptor")


class Item(Base):
    __tablename__ = "de_item"
    id = Column(Integer, primary_key=True)
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    dcodint = Column(String(50))
    ddesproser = Column(String(255))
    cuni_med = Column(String(10))
    ddesunimed = Column(String(20))
    dcantproser = Column(Numeric(15, 2))
    dinfitem = Column(String(100))
    dpuniproser = Column(Numeric(15, 2))
    dtotbruopeitem = Column(Numeric(15, 2))
    ddescitem = Column(Numeric(15, 2))
    dporcdesit = Column(Numeric(6, 2))
    ddescgloitem = Column(Numeric(15, 2))
    dtotopeitem = Column(Numeric(15, 2))
    iafeciva = Column(SmallInteger)
    ddesafeciva = Column(String(50))
    dpropiva = Column(Numeric(6, 2))
    dtasaiva = Column(Numeric(6, 2))
    dbasgraviva = Column(Numeric(15, 2))
    dliqivaitem = Column(Numeric(15, 2))

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
    
    documento = relationship("Documento", back_populates="nota_credito_debito")
    
    
class Evento(Base):
    __tablename__ = "de_eventos"
    
    id = Column(Integer, primary_key=True)
    id_evento = Column(String(10), nullable=False)  # GDE003
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
    
    de_id = Column(Integer, ForeignKey("de_documento.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=func.now())
    
    documento = relationship("Documento", back_populates="eventos")
    

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
    
class LoteDE(Base):
    __tablename__ = "de_lote"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_creacion = Column(DateTime, default=datetime.now())
    estado = Column(String(20), default="PENDIENTE")
    xml_lote = Column(Text)
    xml_respuesta = Column(Text)
    cantidad_de = Column(Integer, default=0)
