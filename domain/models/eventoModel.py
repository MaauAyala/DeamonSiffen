from sqlalchemy import Column, Integer, String, Date, Numeric,Boolean , ForeignKey, SmallInteger, TIMESTAMP, func, Text
from sqlalchemy.orm import relationship
from core.database import Base


class Evento(Base):
    __tablename__ = "de_eventos"
    id = Column(Integer , primary_key = True ,index =True)
    dfecfirma = Column(TIMESTAMP)
    dverfor = Column(Integer)
    dtigde =Column(String(100))
    cdc_dte = Column(String(44))
    mototeve = Column(String(300))
    dnumtim = Column(String(8))
    dest = Column(String(3))
    dnumin = Column(String(7))
    dnumfin = Column(String(7))
    tipeve = Column(Integer)
    itide = Column(Integer)
    de_id = Column(Integer)    
    