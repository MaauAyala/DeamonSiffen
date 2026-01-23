def remove_prefixes(element):
    """Quita todos los prefijos de un nodo y sus hijos, incluyendo xmlns:ds"""
    
    # Quitar atributo xmlns:ds si existe en el nodo raíz
    if "xmlns:ds" in element.attrib:
        del element.attrib["xmlns:ds"]

    for el in element.iter():
        # Quitar prefijo del tag
        if el.tag.startswith("{"):
            el.tag = el.tag.split("}", 1)[1]  # mantener solo el localname

        # Limpiar atributos que tengan namespace
        for attr in list(el.attrib):
            if attr.startswith("{"):
                new_attr = attr.split("}", 1)[1]
                el.attrib[new_attr] = el.attrib.pop(attr)

    return element
