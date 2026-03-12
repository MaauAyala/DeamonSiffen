# PDF Worker - Generador Automático de PDFs para Documentos Aprobados

## Descripción

El **PDFWorker** es un worker de DemonSiffen que genera automáticamente PDFs para documentos que han sido aprobados por SIFEN. Este worker funciona como un proceso independiente que se ejecuta periódicamente para crear representaciones visuales en PDF de los documentos electrónicos.

## Características

✅ **Procesamiento automático**: Busca automáticamente documentos con estado `APROBADO`
✅ **Parsing de XML**: Extrae datos del XML del documento usando `parseXML.parse_sifen_xml()`
✅ **Generación de PDFs**: Crea PDFs usando el utility `buildReport.generar_pdf_factura()`
✅ **Organización por número**: Los PDFs se guardan con el formato `ESTABLECIMIENTO-PUNTO-NUMERO.pdf`
✅ **Manejo de errores**: Registra y continúa procesando en caso de errores
✅ **Logging detallado**: Logs completos del proceso de generación

## Estructura de Archivos

```
daemon/
└── pdf_worker.py                 # Worker principal
services/
└── pdf_service.py                # Servicio de generación de PDFs
domain/repositories/
└── doc_repo.py                   # Método getAprobados() agregado
main.py                           # Integración del worker
```

## Configuración

El worker se configura mediante la clase `PDFWorkerConfig`:

```python
@dataclass
class PDFWorkerConfig:
    interval: int = 120      # Intervalo de procesamiento (segundos)
    batch_size: int = 50     # Documentos a procesar por ciclo
    max_retries: int = 3     # Reintentos en caso de error
    debug: bool = False      # Modo debug
```

### Valores por defecto en main.py

```python
pdf_config = PDFWorkerConfig(
    interval=120,      # Ejecuta cada 2 minutos
    batch_size=50,     # Procesa 50 documentos por ciclo
    max_retries=3,
    debug=settings.DEBUG
)
```

## Flujo de Procesamiento

1. **Búsqueda**: Consulta la BD por documentos con `estado_actual = "APROBADO"`
2. **Validación**: Verifica que el documento tenga XML válido
3. **Parsing**: Extrae datos del XML usando `parse_sifen_xml()`
4. **Generación**: Crea el PDF con `generar_pdf_factura()`
5. **Guardado**: Almacena en `logs/pdf_generados/{EST}-{PTO}-{NUM}.pdf`
6. **Registro**: Marca el documento como procesado

## Salida de PDFs

Los PDFs se generan en:
```
logs/pdf_generados/
├── 001-001-000001.pdf
├── 001-001-000002.pdf
├── 001-001-000003.pdf
└── ...
```

**Nombre del archivo**: `{ESTABLECIMIENTO}-{PUNTO_EXPEDICION}-{NUMERO_DOCUMENTO}.pdf`

## Integración en main.py

El worker se ejecuta como un proceso independiente:

```python
# Inicialización
pdf_worker = PDFWorker(pdf_config)
pdf_worker.setup()

# Ejecución
pdf_process = mp.Process(target=pdf_worker.start, name="PDFWorker")
pdf_process.start()
```

## Métodos Públicos

### `setup()`
Configura y valida el worker antes de ejecutarse.

```python
worker.setup()
```

### `start()`
Inicia el bucle infinito de procesamiento.

```python
worker.start()  # Bloquea hasta que se interrumpa
```

### `stop()`
Detiene el worker de forma segura.

```python
worker.stop()
```

### `process_once()`
Ejecuta un solo ciclo sin loop (útil para testing).

```python
worker.process_once()  # Procesa una sola vez
```

## Logging

El worker genera logs detallados:

```
🔧 Configurando PDFWorker...
✅ PDFWorker configurado - Intervalo: 120s - Batch: 50
🚀 Iniciando PDFWorker...
📋 Iniciando ciclo de generación de PDFs...
📄 Generando PDF: 001-001-000001.pdf
✅ PDF generado exitosamente: logs/pdf_generados/001-001-000001.pdf
📊 PDFs generados en ciclo:
   ✅ Exitosos: 5/5
   ❌ Errores: 0/5
```

## Manejo de Errores

El worker maneja automáticamente:
- ✅ XMLs vacíos o mal formados
- ✅ Datos incompletos en el documento
- ✅ Errores de I/O al guardar archivos
- ✅ Continúa procesando otros documentos si uno falla

Los errores se registran con detalles:
```
❌ Error parseando XML para documento 5: Invalid XML format
   - Doc ID: 5, CDC: ..., Error: XML Parse Error
```

## Requisitos

### Dependencias de Python
- `reportlab`: Generación de PDF
- `qrcode`: Generación de códigos QR
- `sqlalchemy`: ORM de base de datos

### Archivos necesarios
- `utils/buildReport.py`: Función `generar_pdf_factura()`
- `utils/parseXML.py`: Función `parse_sifen_xml()`
- Base de datos con documentos aprobados

## Ejemplo de Uso

### Ejecución como daemon (automática)
```bash
python main.py --mode daemon
```

El PDFWorker se ejecutará automáticamente cada 2 minutos.

### Procesamiento único
```python
from daemon.pdf_worker import PDFWorker, PDFWorkerConfig
from core.infraestructure.database.database import get_db_session

with get_db_session() as db:
    worker = PDFWorker()
    worker.setup()
    worker.process_once()
```

### Ejecución personalizada
```python
from daemon.pdf_worker import PDFWorker, PDFWorkerConfig
from core.infraestructure.database.database import get_db_session

config = PDFWorkerConfig(
    interval=60,
    batch_size=100,
    debug=True
)

worker = PDFWorker(config)
worker.setup()
worker.start()  # Se ejecutará en loop
```

## Estadísticas y Monitoreo

Cada ciclo retorna estadísticas:

```python
{
    "total_procesados": 50,
    "exitosos": 48,
    "errores": 2,
    "detalles_errores": [
        {
            "doc_id": 10,
            "cdc": "...",
            "error": "XML vacío"
        },
        ...
    ]
}
```

## Troubleshooting

### No se generan PDFs
1. Verificar que hay documentos con estado `APROBADO`
2. Revisar logs para errores de XML
3. Validar que el directorio `logs/` existe

### Error "XML Parse Error"
1. Verificar que `xml_de` contiene XML válido
2. Revisar la estructura del XML con `parse_sifen_xml()`

### Permiso denegado al guardar PDF
1. Verificar permisos de carpeta `logs/pdf_generados/`
2. Asegurar que el usuario tiene permisos de escritura

## Notas de Desarrollo

- El worker es **thread-safe** para uso multi-proceso
- Usa logging centralizado del proyecto en `config.logger`
- Sigue el patrón de arquitectura de workers existentes
- Integrable fácilmente con el sistema de daemon de DemonSiffen
