from core.eventBuilder import eventBuilder

# Crear instancia
builder = eventBuilder()

# Llamar método
try:
    strr = builder.build()  # Si build() no tiene parámetros
    # O si tiene parámetro:
    # strr = builder.build(algun_evento)
    
    print("=== XML GENERADO ===")
    print(strr)
    print(f"Longitud: {len(strr)} caracteres")
    print(f"Tipo: {type(strr)}")
    
except TypeError as e:
    print(f"Error de tipo: {e}")
    print("Probablemente build() requiere un parámetro")
except Exception as e:
    print(f"Error: {e}")