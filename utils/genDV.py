def calcular_dv_11a(numero: str, basemax: int = 11) -> int:
    """
    Calcula el dígito verificador (DV) usando el algoritmo módulo 11.
    Admite entrada alfanumérica (por ejemplo, RUC o cédula con letra final).
    """

    # Paso 1: Reemplazar letras por su código ASCII
    numero_al = ""
    for c in numero.upper():
        if c.isdigit():
            numero_al += c
        else:
            numero_al += str(ord(c))  # ord obtiene el valor ASCII

    # Paso 2: Calcular el DV
    k = 2
    total = 0

    for c in reversed(numero_al):
        if k > basemax:
            k = 2
        total += int(c) * k
        k += 1

    resto = total % 11
    if resto > 1:
        digito = 11 - resto
    else:
        digito = 0

    return digito