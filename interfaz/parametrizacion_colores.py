"""Paleta y roles visuales de Chomsky Lab.

Para cambiar el aspecto general, edita PALETA_BASE aquí. El resto de la
interfaz usa nombres con intención (FONDO_APP, TEXTO, BORDE...) y no hex
sueltos, así cada tono se puede mantener desde un solo lugar.
"""

# Tonos entregados como referencia visual.
PALETA_BASE = {
    "noche": "#0E0B1D",
    "berenjena": "#2A1E4D",
    "violeta": "#5A3B8C",
    "lavanda": "#8B7CC7",
    "lavanda_clara": "#C9C2E3",
    "pizarra": "#3A3A52",
}

# Roles generales: ventana, tarjetas, entradas, texto y líneas.
FONDO_APP = PALETA_BASE["noche"]
PANEL = PALETA_BASE["berenjena"]
PANEL_ELEVADO = PALETA_BASE["pizarra"]
CAMPO = PALETA_BASE["pizarra"]
TEXTO = PALETA_BASE["lavanda_clara"]
TEXTO_SUAVE = PALETA_BASE["lavanda_clara"]
BORDE = PALETA_BASE["violeta"]
GRILLA = PALETA_BASE["berenjena"]

# Acciones y selección.
ACENTO = PALETA_BASE["lavanda_clara"]
ACENTO_HOVER = PALETA_BASE["lavanda"]
SELECCION = PALETA_BASE["violeta"]
SELECCION_ACTIVA = PALETA_BASE["violeta"]

# La paleta es monocromática: los símbolos y las palabras del resultado
# (✓ ACEPTADA, ✕ RECHAZADA, — NO EVALUADA) también indican cada estado.
ESTADO_OK = PALETA_BASE["lavanda_clara"]
ESTADO_ERROR = PALETA_BASE["lavanda_clara"]
ESTADO_ATENCION = PALETA_BASE["lavanda"]

# Acento pequeño para identificar cada nivel en la portada.
COLOR_POR_NIVEL = {
    3: PALETA_BASE["lavanda"],
    2: PALETA_BASE["violeta"],
    1: PALETA_BASE["lavanda_clara"],
    0: PALETA_BASE["pizarra"],
}

# Colores de texto para que números y etiquetas sigan legibles sobre cada tono.
COLOR_RUTA_POR_NIVEL = {
    3: PALETA_BASE["lavanda"],
    2: PALETA_BASE["lavanda_clara"],
    1: PALETA_BASE["lavanda_clara"],
    0: PALETA_BASE["lavanda"],
}
TEXTO_ETIQUETA_NIVEL = {
    3: FONDO_APP,
    2: TEXTO,
    1: FONDO_APP,
    0: TEXTO,
}
