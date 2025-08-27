import pypandoc

def export_text(content: str, path: str, fmt: str = "txt"):
    """
    Exporta contenido a TXT o MD con formato básico.
    - content: texto plano o markdown generado por el agente
    - path: ruta destino (ej. 'data/unh.txt' o 'data/unh.md')
    - fmt: 'txt' o 'md'
    """
    if fmt not in ["txt", "md"]:
        raise ValueError("Formato no soportado. Usa 'txt' o 'md'.")
    
    pypandoc.convert_text(
        content,
        fmt,
        format="md",   # entrada siempre tratada como markdown
        outputfile=path,
        extra_args=["--standalone"]
    )
    return path
