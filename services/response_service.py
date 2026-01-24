from sqlalchemy.orm import Session
from datetime import datetime
from domain.models.models import Estado
import xml.etree.ElementTree as ET
import html

def guardarResponse(xml_string: str, db: Session, documento_id: int) -> Estado:
    """
    Guarda la respuesta XML del SIFEN en la tabla de estados.
    
    Args:
        xml_string: XML de respuesta
        db: Sesión de base de datos
        documento_id: ID del documento relacionado
    
    Returns:
        Objeto Estado creado
    """
    try:
        root = ET.fromstring(xml_string)
        
        # Namespaces
        ns = {
            'ns2': 'http://ekuatia.set.gov.py/sifen/xsd',
            'env': 'http://www.w3.org/2003/05/soap-envelope'
        }
        
        # Buscar elementos
        rprotde = root.find('.//ns2:rProtDe', ns)
        
        if rprotde is None:
            raise ValueError("XML no contiene rProtDe")
        
        # Extraer datos
        dcodres = rprotde.findtext('ns2:gResProc/ns2:dCodRes', default='0000', namespaces=ns)
        dmsgres = rprotde.findtext('ns2:gResProc/ns2:dMsgRes', default='Sin mensaje', namespaces=ns)
        dfecproc_str = rprotde.findtext('ns2:dFecProc', namespaces=ns)
        
        # Decodificar HTML entities
        dmsgres = html.unescape(dmsgres)
        
        # Parsear fecha
        dfecproc = None
        if dfecproc_str:
            try:
                dfecproc = datetime.fromisoformat(dfecproc_str.replace('Z', '+00:00'))
            except:
                dfecproc = datetime.now()
        
        # Crear y guardar estado
        estado = Estado(
            de_id=documento_id,
            dcodres=dcodres,
            dmsgres=dmsgres[:255],  # Limitar a 255 caracteres
            dfecproc=dfecproc or datetime.now()
        )
        
        db.add(estado)
        db.commit()
        db.refresh(estado)
        
        return estado
        
    except ET.ParseError:
        raise ValueError("XML mal formado")
    except Exception as e:
        db.rollback()
        raise Exception(f"Error guardando respuesta: {str(e)}")