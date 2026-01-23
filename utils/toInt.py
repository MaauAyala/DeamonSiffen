from decimal import Decimal

def to_int_if_possible(value) -> str:
    """
    Convierte un número (str, float, Decimal, int) a string:
    - Si es entero (ej: 1000.00, 953.0, 48) → devuelve "1000", "953", "48"
    - Si tiene decimales reales → mantiene los decimales necesarios
    Ejemplos:
        1000.00  → "1000"
        1000.50  → "1000.50"
        953      → "953"
        48.0     → "48"
    """
    if value is None:
        return "0"
    
    # Si ya es string, intentamos convertir
    if isinstance(value, str):
        try:
            value = Decimal(value)
        except:
            return str(value)
    
    # Si es float, convertimos a Decimal para evitar errores de precisión
    if isinstance(value, float):
        value = Decimal(str(value))
    
    # Si es int o ya Decimal
    if isinstance(value, (int, Decimal)):
        if value == value.to_integral_value():
            return str(int(value))  # ← elimina .00
        else:
            # Mantiene solo los decimales necesarios (sin trailing zeros)
            return f"{value:f}".rstrip("0").rstrip(".") if "." in f"{value:f}" else f"{value:f}"
    
    return str(value)