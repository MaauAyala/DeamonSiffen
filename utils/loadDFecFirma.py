from datetime import datetime, timedelta
from domain.models.models import Documento


def loadFec(db, doc: Documento):
    """Carga dfecfirma 1 segundo antes de la transmisión."""
    fecha_firma = datetime.now() - timedelta(seconds=120)
    doc.dfecfirma = fecha_firma
    db.flush()  # asegura que SQLAlchemy reconozca el cambio
    db.refresh(doc)  # actualiza el objeto con la DB si hay triggers o default
