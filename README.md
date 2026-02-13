# 📚 DemonSiffen - Guía de Uso

## 🚀 **Inicio Rápido**

### **Requisitos Previos**
- Python 3.8+
- PostgreSQL
- Certificados SIFEN (.pem, .key)
- Variables de entorno configuradas

### **Instalación**
```bash
# Clonar repositorio
git clone <repo-url>
cd demonSiffen

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus datos
```

---

## 🎯 **Modos de Ejecución**

### **1. Modo Daemon (Producción)**
```bash
python main.py --mode daemon
```

**Descripción:**
- Ejecución continua en background
- Procesa documentos cada 60 segundos (configurable)
- Se detiene con `Ctrl+C`
- Ideal para producción

**Características:**
- ✅ Procesamiento automático
- ✅ Manejo de errores con reintentos
- ✅ Logs detallados
- ✅ Shutdown graceful

### **2. Modo Único (Testing)**
```bash
python main.py --mode once
```

**Descripción:**
- Ejecuta un solo ciclo de procesamiento
- Procesa todos los documentos pendientes
- Termina automáticamente
- Ideal para pruebas y depuración

**Características:**
- ✅ Ejecución única
- ✅ Resultados inmediatos
- ✅ Fácil para debugging
- ✅ Sin proceso background

### **3. Modo Default**
```bash
python main.py
```

**Descripción:**
- Equivalente a `--mode daemon`
- Comportamiento por defecto
- Útil para ejecución rápida

---

## ⚙️ **Configuración**

### **Variables de Entorno Principales**

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# SIFEN Endpoints
EVENTO_ENDPOINT=https://sifen.set.gov.py/de/ws/async/envi-de.wsdl
LOTE_ENDPOINT=https://sifen.set.gov.py/de/ws/async/recibe-lote.wsdl

# Certificados
CERT_PATH=C:\ruta\certificado.pem
KEY_PATH=C:\ruta\clave_privada.pem

# Procesamiento
BATCH_SIZE=50
PROCESSING_INTERVAL=60
DEBUG=False
```

### **Configuración de Worker**

```python
# En config/setting.py
WorkerConfig(
    interval=60,        # Segundos entre ciclos
    batch_size=50,     # Documentos por lote
    max_retries=3,     # Reintentos en caso de error
    debug=False        # Modo debug
)
```

---

## 📊 **Tipos de Documentos**

### **Códigos Soportados**

| Código | Tipo | Descripción |
|--------|------|-------------|
| `FE` | Factura Electrónica | Documento fiscal estándar |
| `NC` | Nota de Crédito | Corrección de facturas |
| `ND` | Nota de Débito | Aumento de valores |
| `RE` | Retención Electrónica | Retenciones fiscales |
| `EV` | Evento Electrónico | Eventos SIFEN |

### **Agrupamiento Automático**

```python
# El sistema agrupa automáticamente por tipo:
# - Lote 1: 25 documentos FE
# - Lote 2: 10 documentos NC  
# - Lote 3: 5 documentos ND
```

---

## 🔧 **Flujo de Procesamiento**

### **1. Obtención de Documentos**
```python
documentos = repo_doc.getPendiente()
# Filtra documentos con estado = 'PENDIENTE_ENVIO'
```

### **2. Agrupación por Tipo**
```python
grupos = {}
for doc in documentos:
    tipo_doc = doc.tipo_doc or 'FE'  # Default: Factura
    grupos.setdefault(tipo_doc, []).append(doc)
```

### **3. Procesamiento por Lotes**
```python
for tipo_doc, docs_tipo in grupos.items():
    for batch in dividir_en_lotes(docs_tipo, batch_size):
        procesar_lote(batch, tipo_doc)
```

### **4. Generación de XML**
```python
# XML individual por documento
xml_de = XMLBuilder().build(doc)

# XML del lote
xml_lote = XMLBuilderLote().build_lote(xmls_documentos)
```

### **5. Envío a SIFEN**
```python
soap_client = SOAPClient(cert_path, key_path, debug=True)
response = soap_client.send(xml_lote)
```

---

## 📝 **Logs y Monitoreo**

### **Niveles de Log**
```python
# Configuración en .env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/demon_siffen.log
```

### **Mensajes Típicos**
```
🚀 Iniciando DemonSiffen...
✅ Configuración validada - Debug: False
📋 Iniciando ciclo de procesamiento...
📊 Procesando 25 documentos tipo FE
📦 Lote creado en BD con ID: 123
✅ Lote 123 enviado exitosamente a SIFEN
⏳ Esperando 60 segundos...
```

---

## 🛠️ **Comandos Útiles**

### **Ejecución y Testing**
```bash
# Ejecutar en modo daemon
python main.py --mode daemon

# Ejecutar una sola vez
python main.py --mode once

# Ver configuración actual
python -c "from config.setting import get_settings; print(get_settings().get_summary())"
```

### **Debugging**
```bash
# Habilitar debug
DEBUG=True python main.py --mode once

# Ver logs en tiempo real
tail -f logs/demon_siffen.log

# Validar configuración
python -c "from config.setting import get_settings; get_settings().validate()"
```

---

## 🚨 **Manejo de Errores**

### **Tipos de Error Comunes**

| Error | Causa | Solución |
|-------|--------|----------|
| `Configuración requerida faltante` | Variables de entorno | Verificar [.env](cci:7://file:///c:/Users/mauri/demonSiffen/.env:0:0-0:0) |
| `Certificado no encontrado` | Ruta incorrecta | Verificar `CERT_PATH` |
| `Error en ciclo de procesamiento` | Problemas con documentos | Revisar logs |
| `Error enviando lote` | Problemas SIFEN | Verificar conexión |

### **Reintentos Automáticos**
```python
# Configuración de reintentos
MAX_RETRIES=3  # Reintentos por lote
PROCESSING_INTERVAL=60  # Esperar antes de reintentar
```

---

## 📈 **Monitoreo y Estado**

### **Consulta de Estado**
```python
# Obtener estado del worker
status = worker.get_status()
# Returns: {"running": True, "config": {...}}

# Consultar lote específico
resultado = service.consultar_estado_lote(lote_id=123)
```

### **Métricas Disponibles**
- 📊 Total documentos procesados
- 📦 Lotes enviados
- ⏱️ Tiempo de procesamiento
- 🔄 Tasa de errores
- 📝 Logs detallados

---

## 🎯 **Best Practices**

### **Producción**
```bash
# 1. Validar configuración
python -c "from config.setting import get_settings; get_settings().validate()"

# 2. Ejecutar en modo daemon
python main.py --mode daemon

# 3. Monitorear logs
tail -f logs/demon_siffen.log
```

### **Desarrollo**
```bash
# 1. Habilitar debug
DEBUG=True python main.py --mode once

# 2. Procesamiento único para testing
python main.py --mode once

# 3. Revisar resultados
cat logs/demon_siffen.log | grep "✅"
```

### **Mantenimiento**
```bash
# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +7 -delete

# Validar certificados
openssl x509 -in certificado.pem -text -noout

# Backup de base de datos
pg_dump Sifen_API > backup_$(date +%Y%m%d).sql
```

---

## 🆘 **Soporte y Troubleshooting**

### **Problemas Comunes**

**Q: El sistema no inicia**
```bash
# Verificar configuración
python -c "from config.setting import get_settings; print(get_settings().validate())"
```

**Q: No procesa documentos**
```bash
# Verificar documentos pendientes
python -c "from services.factura_service import FacturaService; from core.database import get_session; s=FacturaService(get_session()); print(s.repo_doc.getPendiente())"
```

**Q: Error de conexión SIFEN**
```bash
# Verificar certificados y endpoints
openssl s_client -connect sifen.set.gov.py:443
```

### **Contacto y Ayuda**
- 📧 Email: soporte@demonSiffen.com
- 📖 Documentación: docs.demonSiffen.com
- 🐛 Issues: GitHub Issues

---

**🎉 ¡Listo para usar DemonSiffen!**

Para comenzar: `python main.py --mode once`