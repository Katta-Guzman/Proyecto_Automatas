"""Portada de Chomsky Lab: navegación, teoría y selección de simuladores."""

import tkinter as tk
from tkinter import ttk

from interfaz.parametrizacion_colores import (
    ACENTO,
    ACENTO_HOVER,
    BORDE,
    CAMPO,
    COLOR_POR_NIVEL,
    COLOR_RUTA_POR_NIVEL,
    FONDO_APP,
    PANEL,
    PANEL_ELEVADO,
    SELECCION_ACTIVA,
    TEXTO,
    TEXTO_ETIQUETA_NIVEL,
    TEXTO_SUAVE,
)
from interfaz.simulador import Simulador

# Cada tarjeta explica el tipo de memoria y enseña una mini máquina dibujada
# con Canvas. El gráfico anticipa lo que se verá al abrir cada simulador.
MODULOS = [
    {
        "nivel": 3,
        "titulo": "Autómata finito",
        "memoria": "Estado actual",
        "descripcion": "Sigue estados y transiciones para reconocer patrones regulares.",
        "ejemplo": "Cadena: baba",
    },
    {
        "nivel": 2,
        "titulo": "Autómata de pila",
        "memoria": "Pila LIFO",
        "descripcion": "Guarda marcas y las retira en orden inverso, como una pila de platos.",
        "ejemplo": "Cadena: aabb · n=2",
    },
    {
        "nivel": 1,
        "titulo": "Cinta linealmente acotada",
        "memoria": "Cinta del tamaño de la entrada",
        "descripcion": "Marca símbolos y mueve el cabezal entre dos límites fijos.",
        "ejemplo": "Cadena: aabbcc · n=2",
    },
    {
        "nivel": 0,
        "titulo": "Máquina de Turing",
        "memoria": "Cinta extendible",
        "descripcion": "Lee, escribe y desplaza el cabezal para reconocer o calcular.",
        "ejemplo": "Cadena: 0110",
    },
]


class Aplicacion:
    """Ventana principal y navegación del laboratorio."""

    ANCHO_BARRA_LATERAL = 224

    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Chomsky Lab | Aprende autómatas paso a paso")
        ancho_pantalla = self.ventana.winfo_screenwidth()
        alto_pantalla = self.ventana.winfo_screenheight()
        ancho_ventana = min(1600, max(1020, ancho_pantalla - 80))
        alto_ventana = min(900, max(680, alto_pantalla - 140))
        self.ventana.geometry(f"{ancho_ventana}x{alto_ventana}")
        self.ancho_ventana = ancho_ventana
        self.ventana.minsize(1020, 680)
        self.ventana.configure(bg=FONDO_APP)
        self._configurar_estilos()
        self.contenido = None
        self.scroller = None
        self.page = None
        self.section_cards = None
        self.canvas_hero = None
        self.botones_nav = {}
        self.miniaturas = {}
        self.ventana.bind("<Configure>", self._redimensionar_portada, add="+")
        self.mostrar_simuladores()

    def _configurar_estilos(self):
        """Define los estilos ttk para que coincidan con la paleta central."""
        estilo = ttk.Style(self.ventana)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=FONDO_APP)
        estilo.configure("Panel.TFrame", background=PANEL)
        estilo.configure("TLabel", background=FONDO_APP, foreground=TEXTO,
                         font=("Segoe UI", 10))
        estilo.configure("Muted.TLabel", background=FONDO_APP, foreground=TEXTO_SUAVE,
                         font=("Segoe UI", 9))
        estilo.configure("Panel.TLabel", background=PANEL, foreground=TEXTO,
                         font=("Segoe UI", 10))
        estilo.configure("Title.TLabel", background=FONDO_APP, foreground=TEXTO,
                         font=("Segoe UI Semibold", 29, "bold"))
        estilo.configure("Heading.TLabel", background=FONDO_APP, foreground=TEXTO,
                         font=("Segoe UI Semibold", 17, "bold"))
        estilo.configure("TButton", font=("Segoe UI Semibold", 10), padding=(12, 8),
                         background=PANEL_ELEVADO, foreground=TEXTO, borderwidth=0)
        estilo.map("TButton", background=[("active", ACENTO_HOVER)],
                   foreground=[("disabled", TEXTO_SUAVE)])
        estilo.configure("Accent.TButton", background=ACENTO, foreground=FONDO_APP)
        estilo.map("Accent.TButton", background=[("active", ACENTO_HOVER)])
        estilo.configure("Quiet.TButton", background=PANEL, foreground=TEXTO,
                         borderwidth=1, relief="solid")
        estilo.map("Quiet.TButton", background=[("active", PANEL_ELEVADO)])
        estilo.configure("TEntry", fieldbackground=CAMPO, foreground=TEXTO,
                         insertcolor=TEXTO, padding=9, borderwidth=1)
        estilo.configure("Input.TEntry", fieldbackground=CAMPO, foreground=TEXTO,
                         insertcolor=TEXTO, padding=9, borderwidth=1)
        estilo.configure("TCombobox", fieldbackground=CAMPO, foreground=TEXTO,
                         background=PANEL_ELEVADO, arrowcolor=TEXTO, padding=8)
        estilo.map("TCombobox", fieldbackground=[("readonly", CAMPO)],
                   foreground=[("readonly", TEXTO)])
        estilo.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                         foreground=TEXTO, rowheight=31, borderwidth=0,
                         font=("Segoe UI", 9))
        estilo.configure("Treeview.Heading", background=PANEL_ELEVADO,
                         foreground=TEXTO, font=("Segoe UI Semibold", 9, "bold"),
                         relief="flat")
        estilo.map("Treeview", background=[("selected", SELECCION_ACTIVA)],
                   foreground=[("selected", TEXTO)])
        estilo.configure("Vertical.TScrollbar", background=PANEL_ELEVADO,
                         troughcolor=FONDO_APP, arrowcolor=TEXTO, borderwidth=0)

    def _limpiar(self):
        """Retira la vista actual antes de abrir inicio o un simulador."""
        if self.contenido is not None:
            self.contenido.destroy()
        self.contenido = None
        self.scroller = None
        self.page = None
        self.section_cards = None
        self.botones_nav = {}
        self.miniaturas = {}

    def mostrar_simuladores(self):
        """Construye la vista principal con la selección de simuladores."""
        self._limpiar()
        self.contenido = tk.Frame(self.ventana, bg=FONDO_APP)
        self.contenido.pack(fill="both", expand=True)

        barra = tk.Frame(self.contenido, bg=PANEL, width=self.ANCHO_BARRA_LATERAL)
        barra.pack(side="left", fill="y")
        barra.pack_propagate(False)
        self._construir_barra_lateral(barra)

        area = tk.Frame(self.contenido, bg=FONDO_APP)
        area.pack(side="left", fill="both", expand=True)
        self.scroller = tk.Canvas(area, bg=FONDO_APP, highlightthickness=0)
        desplazamiento = ttk.Scrollbar(
            area, orient="vertical", command=self.scroller.yview,
            style="Vertical.TScrollbar",
        )
        self.scroller.configure(yscrollcommand=desplazamiento.set)
        desplazamiento.pack(side="right", fill="y")
        self.scroller.pack(side="left", fill="both", expand=True)

        self.page = tk.Frame(self.scroller, bg=FONDO_APP, padx=30, pady=22)
        ventana_canvas = self.scroller.create_window((0, 0), window=self.page, anchor="nw")
        self.page.bind("<Configure>", lambda _e: self.scroller.configure(
            scrollregion=self.scroller.bbox("all")))
        self.scroller.bind("<Configure>", lambda evento: self.scroller.itemconfigure(
            ventana_canvas, width=evento.width))
        self._construir_contenido_inicio()
        self._habilitar_rueda(self.page)
        self._marcar_navegacion("Simuladores")
        self.ventana.after_idle(self._redimensionar_portada)

    def _construir_barra_lateral(self, barra):
        """Arma una navegación breve y una recomendación para nuevos usuarios."""
        identidad = tk.Frame(barra, bg=PANEL)
        identidad.pack(fill="x", padx=18, pady=(23, 22))
        marca = tk.Frame(identidad, bg=ACENTO, width=43, height=43)
        marca.pack(side="left", padx=(0, 10))
        marca.pack_propagate(False)
        tk.Label(marca, text="λ", bg=ACENTO, fg=FONDO_APP,
                 font=("Cambria Math", 20, "bold")).pack(fill="both", expand=True)
        nombre = tk.Frame(identidad, bg=PANEL)
        nombre.pack(side="left", fill="x", expand=True)
        tk.Label(nombre, text="Chomsky Lab", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 12, "bold")).pack(anchor="w")
        tk.Label(nombre, text="Aprende computación", bg=PANEL, fg=TEXTO_SUAVE,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))

        tk.Frame(barra, bg=BORDE, height=1).pack(fill="x", padx=18, pady=(0, 15))
        tk.Label(barra, text="Laboratorio", bg=PANEL, fg=TEXTO_SUAVE,
                 font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=21, pady=(0, 7))
        opciones = [
            ("Simuladores", "◉", self._ir_a_simuladores),
            ("Teoría", "∑", self._mostrar_teoria),
            ("Ejercicios", "✓", self._mostrar_ejercicios),
            ("Recursos", "▤", self._mostrar_recursos),
            ("Acerca del Lab", "ⓘ", self._mostrar_acerca),
        ]
        for nombre_opcion, icono, accion in opciones:
            self._crear_opcion_nav(barra, nombre_opcion, icono, accion)

        recomendacion = tk.Frame(barra, bg=FONDO_APP, padx=14, pady=13)
        recomendacion.pack(side="bottom", fill="x", padx=14, pady=(0, 15))
        tk.Label(recomendacion, text="¿PRIMERA VEZ?", bg=FONDO_APP, fg=ACENTO,
                 font=("Segoe UI Semibold", 8, "bold")).pack(anchor="w")
        tk.Label(
            recomendacion,
            text="Empieza con estados y observa cómo avanza una cadena.",
            bg=FONDO_APP, fg=TEXTO_SUAVE, font=("Segoe UI", 9),
            wraplength=170, justify="left",
        ).pack(anchor="w", pady=(6, 10))
        self._crear_boton(
            recomendacion, "Probar nivel 3", lambda: self.mostrar_nivel(3),
            compacto=True,
        ).pack(anchor="w")

    def _crear_opcion_nav(self, padre, nombre, icono, accion):
        """Crea una fila de navegación con estados activo y hover."""
        fila = tk.Frame(padre, bg=PANEL, cursor="hand2")
        fila.pack(fill="x", padx=12, pady=2)
        simbolo = tk.Label(fila, text=icono, bg=PANEL, fg=TEXTO_SUAVE,
                           width=3, font=("Segoe UI Symbol", 13))
        simbolo.pack(side="left", padx=(7, 2), pady=8)
        texto = tk.Label(fila, text=nombre, bg=PANEL, fg=TEXTO_SUAVE,
                         anchor="w", font=("Segoe UI", 10))
        texto.pack(side="left", fill="x", expand=True, pady=10)
        self.botones_nav[nombre] = (fila, simbolo, texto)

        def navegar(_evento=None):
            self._marcar_navegacion(nombre)
            accion()

        for widget in (fila, simbolo, texto):
            widget.bind("<Button-1>", navegar)
            widget.bind("<Enter>", lambda _e, n=nombre: self._hover_nav(n, True))
            widget.bind("<Leave>", lambda _e, n=nombre: self._hover_nav(n, False))

    def _marcar_navegacion(self, seleccion):
        """Mantiene visible qué sección está abierta."""
        for nombre, (fila, simbolo, texto) in self.botones_nav.items():
            activo = nombre == seleccion
            fondo = SELECCION_ACTIVA if activo else PANEL
            frente = TEXTO if activo else TEXTO_SUAVE
            fila.configure(bg=fondo)
            simbolo.configure(bg=fondo, fg=frente)
            texto.configure(
                bg=fondo, fg=frente,
                font=("Segoe UI Semibold" if activo else "Segoe UI", 10),
            )

    def _hover_nav(self, nombre, dentro):
        """Resalta una opción sin quitar el indicador de sección activa."""
        if nombre not in self.botones_nav:
            return
        fila, simbolo, texto = self.botones_nav[nombre]
        if texto.cget("bg") == SELECCION_ACTIVA:
            return
        fondo = PANEL_ELEVADO if dentro else PANEL
        fila.configure(bg=fondo)
        simbolo.configure(bg=fondo)
        texto.configure(bg=fondo, fg=TEXTO if dentro else TEXTO_SUAVE)

    def _crear_boton(self, padre, texto, comando, *, principal=False, compacto=False):
        """Crea un botón con contraste y foco de teclado visibles."""
        fondo = ACENTO if principal else PANEL_ELEVADO
        frente = FONDO_APP if principal else TEXTO
        return tk.Button(
            padre, text=texto, command=comando, bg=fondo, fg=frente,
            activebackground=ACENTO_HOVER if principal else BORDE,
            activeforeground=FONDO_APP if principal else TEXTO,
            relief="flat", borderwidth=0, cursor="hand2",
            padx=14 if not compacto else 10, pady=9 if not compacto else 6,
            font=("Segoe UI Semibold", 10 if not compacto else 9),
            takefocus=True, highlightthickness=1,
            highlightbackground=fondo, highlightcolor=ACENTO,
        )

    def _construir_contenido_inicio(self):
        self._construir_barra_superior()
        self._construir_hero()
        self._construir_ruta()
        self._construir_tarjetas()
        self._construir_pie()

    def _construir_barra_superior(self):
        fila = tk.Frame(self.page, bg=FONDO_APP)
        fila.pack(fill="x", pady=(0, 13))
        tk.Label(fila, text="Espacio de aprendizaje", bg=FONDO_APP,
                 fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(fila, text="Laboratorio de lenguajes formales", bg=FONDO_APP,
                 fg=TEXTO_SUAVE, font=("Segoe UI Semibold", 8)).pack(side="right")

    def _construir_hero(self):
        hero = tk.Frame(self.page, bg=FONDO_APP)
        hero.pack(fill="x", pady=(0, 17))
        hero.grid_columnconfigure(0, weight=6, uniform="hero")
        hero.grid_columnconfigure(1, weight=5, uniform="hero")

        texto = tk.Frame(hero, bg=FONDO_APP)
        texto.grid(row=0, column=0, sticky="nsew", padx=(0, 22))
        tk.Label(
            texto, text="Los autómatas, paso a paso", bg=FONDO_APP,
            fg=TEXTO, justify="left", anchor="w",
            font=("Segoe UI Semibold", 27, "bold"),
        ).pack(anchor="w", pady=(1, 6))
        tk.Label(
            texto,
            text="Escribe una cadena, observa qué memoria necesita cada máquina y sigue las reglas que la llevan a su respuesta.",
            bg=FONDO_APP, fg=TEXTO_SUAVE, justify="left", anchor="w",
            wraplength=550, font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 13))
        acciones = tk.Frame(texto, bg=FONDO_APP)
        acciones.pack(anchor="w")
        self._crear_boton(
            acciones, "▶  Explorar simuladores", self._ir_a_simuladores,
            principal=True,
        ).pack(side="left", padx=(0, 9))
        self._crear_boton(acciones, "Leer teoría", self._mostrar_teoria).pack(side="left")

        ilustracion = tk.Canvas(
            hero, bg=PANEL, height=160, highlightthickness=1,
            highlightbackground=BORDE,
        )
        ilustracion.grid(row=0, column=1, sticky="nsew")
        self.canvas_hero = ilustracion
        ilustracion.bind("<Configure>", self._dibujar_hero)
        self._dibujar_hero()

    def _dibujar_hero(self, evento=None):
        """Dibuja un AFN pequeño para presentar una transición reconocible."""
        canvas = evento.widget if evento else self.canvas_hero
        if canvas is None:
            return
        canvas.delete("all")
        ancho = max(canvas.winfo_width(), 330)
        alto = max(canvas.winfo_height(), 155)
        for x in range(14, ancho, 28):
            canvas.create_line(x, 0, x, alto, fill=FONDO_APP)
        for y in range(14, alto, 28):
            canvas.create_line(0, y, ancho, y, fill=FONDO_APP)

        canvas.create_text(
            18, 17, text="EJEMPLO · CADENAS QUE TERMINAN EN a",
            anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI Semibold", 8),
        )
        centro_y = int(alto * 0.53)
        q0_x, q1_x, radio = int(ancho * 0.34), int(ancho * 0.72), 25
        canvas.create_line(16, centro_y, q0_x-radio, centro_y,
                           fill=TEXTO, width=2, arrow=tk.LAST)
        canvas.create_line(q0_x+radio, centro_y, q1_x-radio-5, centro_y,
                           fill=ACENTO, width=2, arrow=tk.LAST)
        canvas.create_text((q0_x+q1_x)/2, centro_y-15, text="a",
                           fill=TEXTO, font=("Consolas", 10, "bold"))
        canvas.create_arc(q0_x-13, centro_y-48, q0_x+13, centro_y-20,
                          start=10, extent=320, style=tk.ARC,
                          outline=ACENTO, width=2)
        canvas.create_text(q0_x, centro_y-54, text="Σ", fill=TEXTO_SUAVE,
                           font=("Cambria Math", 9))
        canvas.create_oval(q0_x-radio, centro_y-radio, q0_x+radio, centro_y+radio,
                           fill=FONDO_APP, outline=ACENTO, width=2)
        canvas.create_oval(q1_x-radio, centro_y-radio, q1_x+radio, centro_y+radio,
                           fill=FONDO_APP, outline=ACENTO, width=2)
        canvas.create_oval(q1_x-radio+5, centro_y-radio+5,
                           q1_x+radio-5, centro_y+radio-5,
                           outline=TEXTO_SUAVE, width=1)
        canvas.create_text(q0_x, centro_y, text="q0", fill=TEXTO,
                           font=("Consolas", 11, "bold"))
        canvas.create_text(q1_x, centro_y, text="q1", fill=TEXTO,
                           font=("Consolas", 11, "bold"))
        canvas.create_text(
            18, alto-15, text="q0 recorre la cadena · q1 acepta si termina en a",
            anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8),
        )

    def _construir_ruta(self):
        ruta = tk.Frame(self.page, bg=PANEL, padx=16, pady=9)
        ruta.pack(fill="x", pady=(0, 12))
        cabecera = tk.Frame(ruta, bg=PANEL)
        cabecera.pack(fill="x", pady=(0, 6))
        tk.Label(cabecera, text="Ruta de aprendizaje", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 11, "bold")).pack(side="left")
        tk.Label(cabecera, text="De memoria finita a cinta extendible",
                 bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).pack(side="right")

        pasos_frame = tk.Frame(ruta, bg=PANEL)
        pasos_frame.pack(fill="x")
        pasos = [("03", "Estado"), ("02", "Pila"),
                 ("01", "Cinta acotada"), ("00", "Cinta extendible")]
        for columna in range(7):
            pasos_frame.grid_columnconfigure(
                columna, weight=1 if columna % 2 == 0 else 2,
            )
        for indice, (numero, nombre) in enumerate(pasos):
            paso = tk.Frame(pasos_frame, bg=PANEL)
            paso.grid(row=1, column=indice*2, sticky="w")
            color = COLOR_RUTA_POR_NIVEL[3-indice]
            tk.Label(paso, text=numero, bg=PANEL, fg=color,
                     font=("Segoe UI Semibold", 15, "bold")).pack(side="left", padx=(0, 8))
            tk.Label(paso, text=nombre, bg=PANEL, fg=TEXTO,
                     font=("Segoe UI", 9)).pack(side="left")
            if indice < len(pasos)-1:
                tk.Frame(pasos_frame, bg=BORDE, height=2).grid(
                    row=1, column=indice*2+1, sticky="ew", padx=9,
                )

    def _construir_tarjetas(self):
        titulo = tk.Frame(self.page, bg=FONDO_APP)
        titulo.pack(fill="x", pady=(0, 9))
        tk.Label(titulo, text="Elige un modelo", bg=FONDO_APP, fg=TEXTO,
                 font=("Segoe UI Semibold", 17, "bold")).pack(side="left")
        tk.Label(titulo, text="Cada nivel añade una forma distinta de memoria.",
                 bg=FONDO_APP, fg=TEXTO_SUAVE,
                 font=("Segoe UI", 9)).pack(side="right")

        self.section_cards = tk.Frame(self.page, bg=FONDO_APP)
        self.section_cards.pack(fill="x")
        for columna in range(2):
            self.section_cards.grid_columnconfigure(columna, weight=1, uniform="tarjetas")
        for indice, modulo in enumerate(MODULOS):
            fila, columna = divmod(indice, 2)
            tarjeta = self._crear_tarjeta(self.section_cards, modulo)
            tarjeta.grid(
                row=fila, column=columna, sticky="nsew",
                padx=(0, 8) if columna == 0 else (8, 0),
                pady=(0, 10),
            )

    def _crear_tarjeta(self, padre, modulo):
        nivel = modulo["nivel"]
        color = COLOR_POR_NIVEL[nivel]
        tarjeta = tk.Frame(
            padre, bg=PANEL, highlightthickness=1, highlightbackground=BORDE,
        )
        tk.Frame(tarjeta, bg=color, height=3).pack(fill="x")
        cuerpo = tk.Frame(tarjeta, bg=PANEL, padx=15, pady=12)
        cuerpo.pack(fill="both", expand=True)

        fila_superior = tk.Frame(cuerpo, bg=PANEL)
        fila_superior.pack(fill="x", pady=(0, 8))
        tk.Label(fila_superior, text=f"Nivel {nivel}", bg=color,
                 fg=TEXTO_ETIQUETA_NIVEL[nivel],
                 padx=8, pady=3, font=("Segoe UI Semibold", 8, "bold")).pack(side="left")
        tk.Label(fila_superior, text=modulo["memoria"], bg=PANEL_ELEVADO,
                 fg=TEXTO_SUAVE, padx=8, pady=4,
                 font=("Segoe UI", 8)).pack(side="right")

        centro = tk.Frame(cuerpo, bg=PANEL)
        centro.pack(fill="both", expand=True)
        izquierda = tk.Frame(centro, bg=PANEL)
        izquierda.pack(side="left", fill="both", expand=True, padx=(0, 7))
        tk.Label(izquierda, text=modulo["titulo"], bg=PANEL, fg=TEXTO,
                 justify="left", anchor="w", wraplength=275,
                 font=("Segoe UI Semibold", 14, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(izquierda, text=modulo["descripcion"], bg=PANEL, fg=TEXTO_SUAVE,
                 justify="left", anchor="w", wraplength=275,
                 font=("Segoe UI", 9)).pack(anchor="w")
        acciones = tk.Frame(izquierda, bg=PANEL)
        acciones.pack(fill="x", pady=(8, 0))
        tk.Label(acciones, text=modulo["ejemplo"], bg=CAMPO, fg=TEXTO,
                 padx=7, pady=5, font=("Segoe UI", 8)).pack(side="left")
        self._crear_boton(
            acciones, "▶ Abrir simulador",
            lambda n=nivel: self.mostrar_nivel(n),
            principal=True, compacto=True,
        ).pack(side="right")

        escala = min(1.32, max(0.95, self.ancho_ventana / 1240))
        ancho_dibujo = round(158 * escala)
        alto_dibujo = round(114 * escala)
        dibujo = tk.Canvas(centro, width=ancho_dibujo, height=alto_dibujo, bg=PANEL,
                           highlightthickness=0)
        dibujo.pack(side="right", padx=(4, 0))
        self.miniaturas[nivel] = (dibujo, color)
        self._dibujar_minimodelo(dibujo, nivel, color, escala)
        tarjeta.bind("<Enter>", lambda _e: tarjeta.configure(highlightbackground=color))
        tarjeta.bind("<Leave>", lambda _e: tarjeta.configure(highlightbackground=BORDE))
        return tarjeta

    def _redimensionar_portada(self, evento=None):
        """Ajusta las miniaturas al ancho de ventana sin desbordar las tarjetas."""
        if evento is not None and evento.widget is not self.ventana:
            return
        if self.page is None or not self.miniaturas:
            return
        ancho = max(self.ventana.winfo_width(), 1020)
        self.ancho_ventana = ancho
        escala = min(1.32, max(0.95, ancho / 1240))
        for nivel, (canvas, color) in self.miniaturas.items():
            canvas.configure(width=round(158*escala), height=round(114*escala))
            self._dibujar_minimodelo(canvas, nivel, color, escala)

    def _dibujar_minimodelo(self, canvas, nivel, color, escala=1):
        """Dibuja una miniatura distinta para cada tipo de memoria."""
        canvas.delete("all")
        if nivel == 3:
            y, q0, q1, radio = 60, 36, 122, 17
            canvas.create_line(3, y, q0-radio, y, fill=TEXTO_SUAVE, arrow=tk.LAST)
            canvas.create_line(q0+radio, y, q1-radio-2, y, fill=ACENTO,
                               width=1.7, arrow=tk.LAST)
            canvas.create_text((q0+q1)/2, y-12, text="a", fill=TEXTO,
                               font=("Consolas", 8, "bold"))
            canvas.create_arc(q0-13, y-42, q0+13, y-14, start=10,
                              extent=320, style=tk.ARC, outline=color, width=2)
            canvas.create_text(q0, y-46, text="Σ", fill=TEXTO_SUAVE,
                               font=("Cambria Math", 8))
            canvas.create_oval(q0-radio, y-radio, q0+radio, y+radio,
                               fill=FONDO_APP, outline=color, width=2)
            canvas.create_oval(q1-radio, y-radio, q1+radio, y+radio,
                               fill=FONDO_APP, outline=color, width=2)
            canvas.create_oval(q1-radio+4, y-radio+4, q1+radio-4, y+radio-4,
                               outline=TEXTO_SUAVE, width=1)
            canvas.create_text(q0, y, text="q0", fill=TEXTO,
                               font=("Consolas", 8, "bold"))
            canvas.create_text(q1, y, text="q1", fill=TEXTO,
                               font=("Consolas", 8, "bold"))
        elif nivel == 2:
            canvas.create_text(79, 12, text="PILA · LIFO", fill=TEXTO_SUAVE,
                               font=("Segoe UI Semibold", 8))
            for indice, simbolo in enumerate(("A", "A", "⊥")):
                y = 25 + indice*25
                relleno = color if indice == 0 else PANEL_ELEVADO
                canvas.create_rectangle(48, y, 110, y+21, fill=relleno,
                                       outline=BORDE, width=1)
                canvas.create_text(79, y+10, text=simbolo, fill=TEXTO,
                                   font=("Consolas", 9, "bold"))
            canvas.create_line(123, 79, 123, 39, fill=ACENTO,
                               width=1.8, arrow=tk.LAST)
            canvas.create_text(139, 57, text="sale", fill=TEXTO_SUAVE,
                               font=("Segoe UI", 7))
        elif nivel == 1:
            simbolos = ["⊢", "a", "b", "c", "⊣"]
            inicio, ancho, y = 7, 28, 42
            for indice, simbolo in enumerate(simbolos):
                x = inicio + indice*ancho
                activo = indice == 2
                canvas.create_rectangle(
                    x, y, x+ancho-2, y+30,
                    fill=SELECCION_ACTIVA if activo else PANEL_ELEVADO,
                    outline=color if activo else BORDE, width=2 if activo else 1,
                )
                canvas.create_text(x+(ancho-2)/2, y+15, text=simbolo,
                                   fill=TEXTO, font=("Consolas", 9, "bold"))
            canvas.create_line(inicio+2*ancho+13, y-15,
                               inicio+2*ancho+13, y-2,
                               fill=ACENTO, width=1.7, arrow=tk.LAST)
            canvas.create_text(77, 90, text="cinta de entrada", fill=TEXTO_SUAVE,
                               font=("Segoe UI", 7))
        else:
            simbolos = ["…", "□", "1", "+", "1", "□", "…"]
            inicio, ancho, y = 4, 22, 43
            for indice, simbolo in enumerate(simbolos):
                x = inicio + indice*ancho
                activo = indice == 3
                canvas.create_rectangle(
                    x, y, x+ancho-2, y+29,
                    fill=SELECCION_ACTIVA if activo else PANEL_ELEVADO,
                    outline=color if activo else BORDE, width=2 if activo else 1,
                )
                canvas.create_text(x+(ancho-2)/2, y+14, text=simbolo,
                                   fill=TEXTO, font=("Consolas", 8, "bold"))
            canvas.create_line(inicio+3*ancho+10, y-16,
                               inicio+3*ancho+10, y-2,
                               fill=ACENTO, width=1.7, arrow=tk.LAST)
            canvas.create_text(78, 90, text="cinta extendible", fill=TEXTO_SUAVE,
                               font=("Segoe UI", 7))
        if escala != 1:
            canvas.scale("all", 0, 0, escala, escala)

    def _construir_pie(self):
        pie = tk.Frame(self.page, bg=PANEL, padx=15, pady=10)
        pie.pack(fill="x", pady=(1, 0))
        tk.Label(pie, text="✦", bg=PANEL, fg=ACENTO,
                 font=("Segoe UI Symbol", 15, "bold")).pack(side="left", padx=(0, 9))
        tk.Label(pie, text="Consejo", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 9, "bold")).pack(side="left", padx=(0, 12))
        tk.Frame(pie, bg=BORDE, width=1, height=28).pack(side="left", padx=(0, 12))
        tk.Label(
            pie,
            text="Puedes usar letras o números: cada símbolo debe estar en el alfabeto del módulo.",
            bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8),
            wraplength=430, justify="left",
        ).pack(side="left", fill="x", expand=True)
        tk.Label(pie, text="Traza paso a paso   ·   Diagramas sincronizados",
                 bg=PANEL, fg=ACENTO, font=("Segoe UI Semibold", 8)).pack(
                     side="right", padx=(12, 0))

    def _habilitar_rueda(self, widget):
        """Permite desplazar la portada cuando el puntero está en una tarjeta."""
        widget.bind("<MouseWheel>", self._desplazar_menu, add="+")
        for hijo in widget.winfo_children():
            self._habilitar_rueda(hijo)

    def _desplazar_menu(self, evento):
        if self.scroller is not None:
            self.scroller.yview_scroll(-int(evento.delta/120), "units")
        return "break"

    def _ir_a_simuladores(self):
        """Desplaza la portada hasta las cuatro tarjetas de nivel."""
        if self.scroller is None or self.section_cards is None:
            return
        self.ventana.update_idletasks()
        altura = max(self.page.winfo_height(), 1)
        self.scroller.yview_moveto(self.section_cards.winfo_y()/altura)

    def _mostrar_teoria(self):
        elementos = [
            ("Nivel 3 · Regular · Estado finito",
             "Un autómata finito recuerda únicamente su estado actual. Su memoria no crece con la longitud de la entrada.",
             "Ejemplo: cadenas sobre {a,b} que terminan en a.", 3),
            ("Nivel 2 · Libre de contexto · Pila",
             "Un autómata de pila apila y retira marcas. La última marca que entra es la primera que sale.",
             "Ejemplo: aⁿbⁿ; para n=2, la cadena es aabb.", 2),
            ("Nivel 1 · Sensible al contexto · Cinta acotada",
             "La cinta guarda información a lo largo de la entrada. El cabezal se mueve sin cruzar los extremos.",
             "Ejemplo: aⁿbⁿcⁿ; para n=2, la cadena es aabbcc.", 1),
            ("Nivel 0 · Máquina de Turing",
             "Lee y escribe en una cinta que puede extenderse. Es un modelo general para ejecutar algoritmos.",
             "Ejemplo: reconocer el palíndromo 0110 o calcular 111+11.", 0),
        ]
        self._mostrar_ventana_lectura(
            "La jerarquía de Chomsky",
            "Cada nivel añade una forma de memoria y reconoce una clase más amplia de lenguajes.",
            elementos, texto_boton="Abrir simulador",
        )

    def _mostrar_ejercicios(self):
        elementos = [
            ("Nivel 3 · Termina en a",
             "¿La cadena baba termina con el símbolo final configurado?",
             "baba → aceptada", 3, "baba"),
            ("Nivel 2 · Iguala los bloques",
             "¿Hay dos a y luego dos b, en el orden correcto?",
             "aabb → aceptada", 2, "aabb"),
            ("Nivel 1 · Iguala tres cantidades",
             "¿Los bloques de a, b y c tienen la misma longitud?",
             "aabbcc → aceptada", 1, "aabbcc"),
            ("Nivel 0 · Comprueba un palíndromo",
             "¿Se lee igual de izquierda a derecha y al revés?",
             "0110 → aceptada", 0, "0110"),
        ]
        self._mostrar_ventana_lectura(
            "Ejercicios para probar",
            "Carga la cadena en un módulo y sigue sus pasos para comprobar la respuesta.",
            elementos, texto_boton="Probar esta cadena", cargar_cadena=True,
        )

    def _mostrar_recursos(self):
        elementos = [
            ("README.md · Guía de uso",
             "Instalación, ejecución, ejemplos de prueba y explicación breve de cada simulador.",
             "Inicio rápido: py main.py"),
            ("Implementación · Conceptos y reglas",
             "Describe las transiciones, la aceptación, las estructuras de memoria y los límites de simulación.",
             "documentacion/implementacion.md"),
            ("Personalizar los colores",
             "Los seis tonos y sus funciones visuales están centralizados para facilitar cambios.",
             "interfaz/parametrizacion_colores.py"),
        ]
        self._mostrar_ventana_lectura(
            "Recursos del proyecto",
            "Material local para aprender, ejecutar y revisar la aplicación.",
            elementos, texto_boton=None,
        )

    def _mostrar_acerca(self):
        elementos = [
            ("Chomsky Lab",
             "Laboratorio visual para estudiar autómatas y modelos de cómputo.",
             "Proyecto académico en Python y Tkinter."),
            ("Aprende con una ejecución visible",
             "Prueba cadenas y mira cómo cambia el estado, la pila o la cinta.",
             "AFN y AFD · AP · LBA · Máquina de Turing"),
            ("La respuesta explica su alcance",
             "Si una búsqueda alcanza su límite, la aplicación lo indica como no evaluado.",
             "Una simulación finita no decide cualquier Máquina de Turing."),
        ]
        self._mostrar_ventana_lectura(
            "Acerca del laboratorio",
            "Una herramienta de aprendizaje para visualizar la jerarquía de Chomsky.",
            elementos, texto_boton=None,
        )

    def _mostrar_ventana_lectura(self, titulo, introduccion, elementos, *,
                                 texto_boton, cargar_cadena=False):
        """Abre una ventana desplazable para teoría, recursos o ejercicios."""
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title(f"{titulo} | Chomsky Lab")
        dialogo.geometry("760x620")
        dialogo.minsize(620, 500)
        dialogo.configure(bg=FONDO_APP)
        dialogo.transient(self.ventana)
        dialogo.bind("<Escape>", lambda _e: dialogo.destroy())
        dialogo.update_idletasks()
        x = self.ventana.winfo_rootx() + (self.ventana.winfo_width()-760)//2
        y = self.ventana.winfo_rooty() + (self.ventana.winfo_height()-620)//2
        dialogo.geometry(f"760x620+{max(0, x)}+{max(0, y)}")

        cabecera = tk.Frame(dialogo, bg=FONDO_APP, padx=26, pady=22)
        cabecera.pack(fill="x")
        tk.Label(cabecera, text=titulo, bg=FONDO_APP, fg=TEXTO,
                 font=("Segoe UI Semibold", 22, "bold")).pack(anchor="w")
        tk.Label(cabecera, text=introduccion, bg=FONDO_APP, fg=TEXTO_SUAVE,
                 font=("Segoe UI", 10), wraplength=690,
                 justify="left").pack(anchor="w", pady=(7, 0))

        zona = tk.Frame(dialogo, bg=FONDO_APP, padx=20)
        zona.pack(fill="both", expand=True, pady=(0, 20))
        canvas = tk.Canvas(zona, bg=FONDO_APP, highlightthickness=0)
        barra = ttk.Scrollbar(zona, orient="vertical", command=canvas.yview,
                              style="Vertical.TScrollbar")
        canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        pagina = tk.Frame(canvas, bg=FONDO_APP)
        ventana_canvas = canvas.create_window((0, 0), window=pagina, anchor="nw")
        pagina.bind("<Configure>", lambda _e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda evento: canvas.itemconfigure(
            ventana_canvas, width=evento.width))

        for elemento in elementos:
            subtitulo, descripcion, ejemplo = elemento[:3]
            nivel = elemento[3] if len(elemento) > 3 else None
            cadena = elemento[4] if len(elemento) > 4 else None
            color = COLOR_POR_NIVEL.get(nivel, ACENTO)
            tarjeta = tk.Frame(pagina, bg=PANEL, highlightthickness=1,
                               highlightbackground=BORDE)
            tarjeta.pack(fill="x", pady=(0, 11))
            tk.Frame(tarjeta, bg=color, width=4).pack(side="left", fill="y")
            contenido = tk.Frame(tarjeta, bg=PANEL, padx=16, pady=13)
            contenido.pack(side="left", fill="both", expand=True)
            tk.Label(contenido, text=subtitulo, bg=PANEL, fg=TEXTO,
                     font=("Segoe UI Semibold", 12, "bold"),
                     justify="left", anchor="w").pack(anchor="w")
            tk.Label(contenido, text=descripcion, bg=PANEL, fg=TEXTO_SUAVE,
                     font=("Segoe UI", 9), wraplength=600,
                     justify="left", anchor="w").pack(anchor="w", pady=(4, 7))
            fila = tk.Frame(contenido, bg=PANEL)
            fila.pack(fill="x")
            tk.Label(fila, text=ejemplo, bg=CAMPO, fg=TEXTO,
                     font=("Consolas", 9), padx=9, pady=5,
                     anchor="w").pack(side="left")
            if texto_boton and nivel is not None:
                if cargar_cadena:
                    comando = lambda n=nivel, s=cadena, d=dialogo: self._probar_ejercicio(n, s, d)
                else:
                    comando = lambda n=nivel, d=dialogo: self._abrir_desde_dialogo(n, d)
                self._crear_boton(
                    fila, texto_boton, comando, principal=True, compacto=True,
                ).pack(side="right")

        canvas.bind("<MouseWheel>", lambda evento: canvas.yview_scroll(
            -int(evento.delta/120), "units"))

    def _abrir_desde_dialogo(self, nivel, dialogo):
        dialogo.destroy()
        self.mostrar_nivel(nivel)

    def _probar_ejercicio(self, nivel, cadena, dialogo):
        dialogo.destroy()
        self.mostrar_nivel(nivel)
        self.contenido.entrada_var.set(cadena)
        self.contenido.entrada.focus_set()

    def _ir_a_simuladores(self):
        """Desplaza la portada hasta las cuatro tarjetas de nivel."""
        if self.scroller is None or self.section_cards is None:
            return
        self.ventana.update_idletasks()
        altura = max(self.page.winfo_height(), 1)
        self.scroller.yview_moveto(self.section_cards.winfo_y()/altura)

    def mostrar_nivel(self, nivel):
        """Abre el simulador seleccionado y conserva el botón para volver."""
        self._limpiar()
        self.contenido = Simulador(self.ventana, nivel, self.mostrar_simuladores, self.mostrar_nivel)
        self.contenido.pack(fill="both", expand=True)

    def ejecutar(self):
        self.ventana.mainloop()


def mostrar_menu():
    Aplicacion().ejecutar()
