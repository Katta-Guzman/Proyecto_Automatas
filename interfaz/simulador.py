"""Pantallas guiadas para los cuatro modelos de cómputo."""

import math
import tkinter as tk
from tkinter import font as tkfont, ttk

from interfaz.parametrizacion_colores import (
    ACENTO, BORDE, CAMPO, ESTADO_ATENCION, ESTADO_ERROR, ESTADO_OK,
    FONDO_APP, GRILLA, PANEL, PANEL_ELEVADO, SELECCION, SELECCION_ACTIVA,
    TEXTO, TEXTO_SUAVE,
)
from modelos import formales, nivel0, nivel1, nivel2, nivel3

CONFIG = {
    3: {"titulo": "Autómata finito", "tipo": "Nivel 3 · Lenguajes regulares",
        "descripcion": "Un AFN puede seguir varios caminos. El AFD equivalente los reúne en conjuntos de estados.",
        "memoria": "Recuerda un estado o un conjunto de estados"},
    2: {"titulo": "Autómata de pila", "tipo": "Nivel 2 · Lenguajes libres de contexto",
        "descripcion": "La pila guarda marcas: entra una por cada símbolo del primer bloque y sale una por cada símbolo del segundo.",
        "memoria": "Pila: último en entrar, primero en salir"},
    1: {"titulo": "Cinta linealmente acotada", "tipo": "Nivel 1 · Lenguajes sensibles al contexto",
        "descripcion": "La máquina marca un símbolo de cada bloque por ronda. El cabezal se queda dentro de los bordes de la entrada.",
        "memoria": "Cinta del mismo tamaño que la entrada"},
    0: {"titulo": "Máquina de Turing", "tipo": "Nivel 0 · Cómputo general",
        "descripcion": "La máquina lee y escribe símbolos, y mueve el cabezal por una cinta que puede extenderse.",
        "memoria": "Cinta extendible"},
}


class Simulador(ttk.Frame):
    def __init__(self, master, nivel, volver):
        super().__init__(master, padding=(24, 18), style="TFrame")
        self.nivel = nivel
        self.volver = volver
        self.pasos = []
        self.indice = 0
        self.after_id = None
        self.reproduciendo = False
        self.maquina_afn = None
        self.afd = None
        self.veredicto_final = None
        self.velocidad_var = tk.StringVar(value="Normal")
        self.viewer_canvas = None

        self.alfabeto_var = tk.StringVar(value="a,b")
        self.final_var = tk.StringVar(value="a")
        self.apilar_var = tk.StringVar(value="a")
        self.desapilar_var = tk.StringVar(value="b")
        self.bloque_a_var = tk.StringVar(value="a")
        self.bloque_b_var = tk.StringVar(value="b")
        self.bloque_c_var = tk.StringVar(value="c")
        self.modo_var = tk.StringVar(value="Palíndromo")
        self.simbolos_tm_var = tk.StringVar(value="0,1")
        self.n_var = tk.StringVar(value="2")
        self.patron_n1_var = tk.StringVar(value="aⁿ bⁿ cⁿ")
        self.patron_n2_var = tk.StringVar(value="xⁿ yⁿ (guiado)")
        self.plantilla_var = tk.StringVar(value="Termina en símbolo")
        self.custom_config = {
            "estados": "q0,q1", "alfabeto": "0,1", "inicial": "q0", "finales": "q1",
            "reglas": "q0,0 -> q0\nq0,1 -> q0,q1",
        }
        self.custom_maquina = nivel3.crear_desde_reglas(**self.custom_config)
        self.formal_configs = {
            2: {"estados": "q0,q1,qf", "alfabeto": "a,b", "alfabeto_pila": "⊥,A",
                "inicial": "q0", "finales": "qf", "fondo": "⊥",
                "reglas": "q0,a,⊥ -> q0,⊥A\nq0,a,A -> q0,AA\nq0,b,A -> q1,ε\n"
                          "q1,b,A -> q1,ε\nq1,ε,⊥ -> qf,⊥"},
            1: {"estados": "q0,q1,q2,qf", "alfabeto": "a,b",
                "alfabeto_cinta": "a,b,⊢,⊣", "inicial": "q0", "finales": "qf",
                "reglas": "q0,a -> q1,a,R\nq1,b -> q2,b,R\nq2,⊣ -> qf,⊣,S"},
            0: {"estados": "q0,qf", "alfabeto": "1", "alfabeto_cinta": "1,□",
                "inicial": "q0", "finales": "qf",
                "reglas": "q0,1 -> q0,1,R\nq0,□ -> qf,1,S"},
        }
        self.formal_maquinas = {
            2: formales.crear_ap(**self.formal_configs[2]),
            1: formales.crear_cinta("lba", **self.formal_configs[1]),
            0: formales.crear_cinta("mt", **self.formal_configs[0]),
        }
        self.formal_editada = {0: False, 1: False, 2: False}
        self.entrada_var = tk.StringVar()
        self.ejemplo_var = tk.StringVar(value="Elige un ejemplo opcional")
        self.ejemplo_map = {}
        self._construir()

    def _construir(self):
        # El contenido puede superar la altura disponible en portátiles. El marco
        # interior crece normalmente y el lienzo exterior permite desplazarlo.
        self.scroller = tk.Canvas(self, bg=FONDO_APP, highlightthickness=0)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.scroller.yview)
        self.scroller.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.scroller.pack(side="left", fill="both", expand=True)
        self.page = ttk.Frame(self.scroller)
        ventana = self.scroller.create_window((0, 0), window=self.page, anchor="nw")
        self.page.bind("<Configure>", lambda _e: self.scroller.configure(
            scrollregion=self.scroller.bbox("all")))
        self.scroller.bind("<Configure>", lambda e: self.scroller.itemconfigure(
            ventana, width=e.width))
        self.scroller.bind("<MouseWheel>", self._desplazar)
        self.page.bind("<MouseWheel>", self._desplazar)

        cabecera = ttk.Frame(self.page)
        cabecera.pack(fill="x", pady=(0, 13))
        ttk.Button(cabecera, text="‹  Todos los niveles", style="Quiet.TButton",
                   command=self._volver).pack(side="left")
        titulo = ttk.Frame(cabecera)
        titulo.pack(side="left", padx=15)
        ttk.Label(titulo, text=CONFIG[self.nivel]["tipo"], foreground=ACENTO,
                  font=("Segoe UI Semibold", 9, "bold")).pack(anchor="w")
        ttk.Label(titulo, text=CONFIG[self.nivel]["titulo"], style="Heading.TLabel").pack(anchor="w", pady=(2, 0))
        tk.Label(cabecera, text=CONFIG[self.nivel]["memoria"], bg=PANEL, fg=TEXTO,
                 font=("Segoe UI", 9), padx=11, pady=7).pack(side="right", pady=7)

        nota = tk.Frame(self.page, bg=PANEL, padx=13, pady=8)
        nota.pack(fill="x", pady=(0, 13))
        tk.Label(nota, text="¿QUÉ ES UNA CADENA?", bg=PANEL, fg=ACENTO,
                 font=("Segoe UI Semibold", 9, "bold")).pack(anchor="w")
        tk.Label(nota, text="Una secuencia de símbolos, como 101a. Escribe la tuya: los ejemplos son opcionales.",
                 bg=PANEL, fg=TEXTO, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))
        self.ejemplo_rapido = tk.Label(nota, text="", bg=PANEL, fg=TEXTO,
                                        font=("Segoe UI Semibold", 9), anchor="w")
        self.ejemplo_rapido.pack(fill="x", pady=(4, 0))

        self.entrada_panel = tk.Frame(self.page, bg=PANEL, highlightthickness=1, highlightbackground=BORDE,
                                      padx=15, pady=11)
        self.entrada_panel.pack(fill="x", pady=(0, 10))
        self.izquierda = self.entrada_panel
        self._construir_entrada()

        cuerpo = ttk.Frame(self.page, height=390)
        cuerpo.pack(fill="x", pady=(0, 8))
        cuerpo.pack_propagate(False)
        cuerpo.columnconfigure(0, weight=5, minsize=510)
        cuerpo.columnconfigure(1, weight=6, minsize=460)
        cuerpo.rowconfigure(0, weight=1)
        self.grafico_panel = tk.Frame(cuerpo, bg=PANEL, highlightthickness=1,
                                      highlightbackground=BORDE, padx=12, pady=10)
        self.grafico_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        self.derecha = tk.Frame(cuerpo, bg=PANEL, highlightthickness=1, highlightbackground=BORDE,
                                padx=14, pady=12)
        self.derecha.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        self._construir_visual()
        self._construir_traza()
        self._dibujar_inicial()

    def _desplazar(self, evento):
        """Desplaza la página al usar la rueda sobre el marco principal."""
        self.scroller.yview_scroll(-int(evento.delta / 120), "units")

    def _construir_entrada(self):
        tk.Label(self.izquierda, text="Prueba una cadena", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 14, "bold")).pack(anchor="w")
        tk.Label(self.izquierda, text="Una cadena es una secuencia de símbolos. Escribe la tuya; no hace falta elegir un ejemplo.",
                 bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9), wraplength=1100,
                 justify="left").pack(anchor="w", pady=(2, 6))

        if self.nivel == 0:
            selector = tk.Frame(self.izquierda, bg=PANEL)
            selector.pack(fill="x", pady=(0, 5))
            tk.Label(selector, text="¿Qué quieres hacer?", bg=PANEL, fg=TEXTO,
                     font=("Segoe UI Semibold", 9)).pack(side="left", padx=(0, 10))
            self.modo_combo = ttk.Combobox(selector, textvariable=self.modo_var, state="readonly",
                                           values=("Palíndromo", "Suma unaria", "Definir mi MT"), width=27)
            self.modo_combo.pack(side="left")
            self.modo_combo.bind("<<ComboboxSelected>>", self._cambio_modo)
        elif self.nivel == 1:
            selector = tk.Frame(self.izquierda, bg=PANEL)
            selector.pack(fill="x", pady=(0, 5))
            tk.Label(selector, text="Patrón del lenguaje", bg=PANEL, fg=TEXTO,
                     font=("Segoe UI Semibold", 9)).pack(side="left", padx=(0, 10))
            patrones = ttk.Combobox(selector, textvariable=self.patron_n1_var, state="readonly",
                                     values=("aⁿ bⁿ cⁿ", "a bⁿ c²ⁿ", "Definir mi LBA"), width=22)
            patrones.pack(side="left")
            patrones.bind("<<ComboboxSelected>>", self._cambio_modo)
        elif self.nivel == 3:
            selector = tk.Frame(self.izquierda, bg=PANEL)
            selector.pack(fill="x", pady=(0, 5))
            tk.Label(selector, text="Tipo de AFN", bg=PANEL, fg=TEXTO,
                     font=("Segoe UI Semibold", 9)).pack(side="left", padx=(0, 10))
            plantilla = ttk.Combobox(selector, textvariable=self.plantilla_var, state="readonly",
                                      values=("Termina en símbolo", "Contiene dos iguales seguidos",
                                              "Definir mi AFN-ε"), width=34)
            plantilla.pack(side="left")
            plantilla.bind("<<ComboboxSelected>>", self._cambio_modo)
        elif self.nivel == 2:
            selector = tk.Frame(self.izquierda, bg=PANEL)
            selector.pack(fill="x", pady=(0, 5))
            tk.Label(selector, text="Tipo de autómata de pila", bg=PANEL, fg=TEXTO,
                     font=("Segoe UI Semibold", 9)).pack(side="left", padx=(0, 10))
            patron = ttk.Combobox(selector, textvariable=self.patron_n2_var, state="readonly",
                                   values=("xⁿ yⁿ (guiado)", "Definir mi AP"), width=28)
            patron.pack(side="left")
            patron.bind("<<ComboboxSelected>>", self._cambio_modo)

        self.parametros = tk.Frame(self.izquierda, bg=PANEL, padx=10, pady=8)
        self.parametros.pack(fill="x", pady=(0, 9))
        self._dibujar_parametros()

        fila_cadena = tk.Frame(self.izquierda, bg=PANEL)
        fila_cadena.pack(fill="x", pady=(0, 2))
        fila_cadena.columnconfigure(0, weight=3)
        fila_cadena.columnconfigure(1, weight=2)
        grupo_cadena = tk.Frame(fila_cadena, bg=PANEL)
        grupo_cadena.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        tk.Label(grupo_cadena, text="Cadena de entrada", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", pady=(0, 3))
        self.entrada = ttk.Entry(grupo_cadena, textvariable=self.entrada_var,
                                 font=("Consolas", 13), style="Input.TEntry")
        self.entrada.pack(fill="x", ipady=1)
        self.entrada.bind("<Return>", lambda _evento: self._simular())

        fila_ejemplo = tk.Frame(fila_cadena, bg=PANEL)
        fila_ejemplo.grid(row=0, column=1, sticky="ew")
        tk.Label(fila_ejemplo, text="Ejemplo opcional", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", pady=(0, 3))
        fila_selector = tk.Frame(fila_ejemplo, bg=PANEL)
        fila_selector.pack(fill="x")
        self.ejemplos = ttk.Combobox(fila_selector, textvariable=self.ejemplo_var, state="readonly")
        self.ejemplos.pack(side="left", fill="x", expand=True)
        self.ejemplos.bind("<<ComboboxSelected>>", self._seleccion_ejemplo)
        ttk.Button(fila_selector, text="Cargar ejemplo", style="Quiet.TButton",
                   command=self._cargar_ejemplo).pack(side="left", padx=(7, 0))
        self._actualizar_ejemplos()

        fila_botones = tk.Frame(self.izquierda, bg=PANEL)
        fila_botones.pack(fill="x", pady=(5, 3))
        ttk.Button(fila_botones, text="Simular cadena", style="Accent.TButton",
                   command=self._simular).pack(side="left")
        ttk.Button(fila_botones, text="Vaciar", style="Quiet.TButton",
                   command=self._vaciar).pack(side="left", padx=(8, 0))
        tk.Label(fila_botones,
                 text="Alfabeto: letras y números son válidos si los incluyes en los símbolos configurados.",
                 bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).pack(side="left", padx=(14, 0))
        self.resultado = tk.Label(self.izquierda, text="Listo. Puedes simular incluso una entrada vacía.",
                                  bg=PANEL_ELEVADO, fg=TEXTO_SUAVE, font=("Segoe UI Semibold", 9),
                                  padx=9, pady=6, anchor="w", justify="left", wraplength=1100)
        self.resultado.pack(fill="x", pady=(1, 4))

        self.concepto = tk.Label(self.izquierda, text="", bg=PANEL, fg=TEXTO,
                                 font=("Segoe UI", 8), padx=9, pady=5,
                                 anchor="w", justify="left", wraplength=1100)
        self.concepto.pack(fill="x", pady=(0, 1))
        self._actualizar_concepto()

    def _dibujar_parametros(self):
        for widget in self.parametros.winfo_children():
            widget.destroy()
        self.param_entries = []

        if self.nivel in (0, 1, 2) and self._es_formal():
            nombres = {2: "AP", 1: "LBA", 0: "MT"}
            nombre = nombres[self.nivel]
            maquina = self.formal_maquinas[self.nivel]
            tk.Label(self.parametros, text=f"{nombre} definido por transiciones", bg=PANEL,
                     fg=TEXTO, font=("Segoe UI Semibold", 9)).pack(anchor="w")
            tk.Label(self.parametros,
                     text=f"{len(maquina['estados'])} estados · {len(maquina['reglas'])} reglas · "
                          "puedes editar la definición completa.",
                     bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).pack(anchor="w", pady=(3, 5))
            ttk.Button(self.parametros, text=f"Editar reglas del {nombre}", style="Quiet.TButton",
                       command=self._editar_formal).pack(anchor="w")
            return

        if self.nivel == 3:
            if self.plantilla_var.get() == "Definir mi AFN-ε":
                tk.Label(self.parametros, text="Autómata definido por reglas", bg=PANEL, fg=TEXTO,
                         font=("Segoe UI Semibold", 9)).pack(anchor="w")
                tk.Label(self.parametros,
                         text="Estados, alfabeto, estado inicial, finales y transiciones editables.",
                         bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).pack(anchor="w", pady=(3, 5))
                ttk.Button(self.parametros, text="Editar reglas del AFN-ε", style="Quiet.TButton",
                           command=self._editar_afn).pack(anchor="w")
                return
            pares = self.plantilla_var.get() == "Contiene dos iguales seguidos"
            titulo = "Alfabeto del AFN ramificado (dos símbolos)" if pares else "Alfabeto y símbolo que debe quedar al final"
            tk.Label(self.parametros, text=titulo, bg=PANEL,
                     fg=TEXTO, font=("Segoe UI Semibold", 9)).grid(row=0, column=0, columnspan=2, sticky="w")
            self._campo_parametro(self.parametros, "Alfabeto (separa con comas)", self.alfabeto_var, 0, 1)
            if not pares:
                self._campo_parametro(self.parametros, "Final", self.final_var, 1, 1)
            explicacion = ("Dos caminos ε: uno detecta 00 y otro 11 (o los símbolos elegidos)."
                           if pares else "Ejemplo: a,b,1 permite mezclar letras y números.")
            tk.Label(self.parametros, text=explicacion,
                     bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
        elif self.nivel == 2:
            tk.Label(self.parametros, text="Elige dos símbolos distintos", bg=PANEL,
                     fg=TEXTO, font=("Segoe UI Semibold", 9)).grid(row=0, column=0, columnspan=2, sticky="w")
            self._campo_parametro(self.parametros, "Apila una marca por", self.apilar_var, 0, 1)
            self._campo_parametro(self.parametros, "Retira una marca por", self.desapilar_var, 1, 1)
            tk.Label(self.parametros, text="También puedes probar 0011: se apilan con 0 y se retiran con 1.",
                     bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8), wraplength=440,
                     justify="left").grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
            self._control_n(3, 2, 6)
        elif self.nivel == 1:
            tk.Label(self.parametros, text="Escribe un carácter por bloque; n controla las repeticiones", bg=PANEL,
                     fg=TEXTO, font=("Segoe UI Semibold", 9)).grid(row=0, column=0, columnspan=3, sticky="w")
            self._campo_parametro(self.parametros, "Símbolo a", self.bloque_a_var, 0, 1)
            self._campo_parametro(self.parametros, "Símbolo b", self.bloque_b_var, 1, 1)
            self._campo_parametro(self.parametros, "Símbolo c", self.bloque_c_var, 2, 1)
            nota = ("a bⁿ c²ⁿ: a aparece una vez; por cada b hay dos c. Este patrón también es libre de contexto."
                    if self.patron_n1_var.get() == "a bⁿ c²ⁿ" else
                    "aⁿ bⁿ cⁿ: los tres símbolos aparecen n veces; X, Y y Z son marcas de cinta.")
            tk.Label(self.parametros, text=nota,
                     bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8), wraplength=440,
                     justify="left").grid(row=2, column=0, columnspan=3, sticky="w", pady=(4, 0))
            self._control_n(3, 3, 5)
        elif self._modo_actual() == "palindromo":
            tk.Label(self.parametros, text="Dos símbolos que pueden aparecer en el palíndromo", bg=PANEL,
                     fg=TEXTO, font=("Segoe UI Semibold", 9)).grid(row=0, column=0, sticky="w")
            self._campo_parametro(self.parametros, "Separados por coma", self.simbolos_tm_var, 0, 1, colspan=1)
            tk.Label(self.parametros, text="Ejemplos: 0,1 o a,b. X e Y quedan reservadas para las marcas.",
                     bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).grid(row=2, column=0, sticky="w", pady=(4, 0))
        else:
            tk.Label(self.parametros, text="Usa 1 para cada unidad y + entre los dos sumandos.",
                     bg=PANEL, fg=TEXTO, font=("Segoe UI", 9), wraplength=430,
                     justify="left").pack(anchor="w")

    def _campo_parametro(self, parent, etiqueta, variable, columna, fila, colspan=1):
        marco = tk.Frame(parent, bg=PANEL)
        marco.grid(row=fila, column=columna, columnspan=colspan, sticky="ew",
                   padx=(0 if columna == 0 else 8, 5), pady=(5, 0))
        tk.Label(marco, text=etiqueta, bg=PANEL, fg=TEXTO_SUAVE,
                 font=("Segoe UI", 8)).pack(anchor="w")
        entrada = ttk.Entry(marco, textvariable=variable, font=("Consolas", 10), style="Input.TEntry")
        entrada.pack(fill="x", pady=(2, 0))
        entrada.bind("<KeyRelease>", self._parametro_cambiado)
        self.param_entries.append(entrada)
        parent.columnconfigure(columna, weight=1)

    def _editar_afn(self):
        """Edita una máquina completa; aplica los cambios solo tras validarlos."""
        ventana = tk.Toplevel(self)
        ventana.title("Definir AFN-ε | Chomsky Lab")
        ventana.geometry("760x620")
        ventana.minsize(600, 510)
        ventana.configure(bg=PANEL)
        ventana.transient(self.winfo_toplevel())
        marco = tk.Frame(ventana, bg=PANEL, padx=20, pady=16)
        marco.pack(fill="both", expand=True)
        tk.Label(marco, text="Define tu propio AFN-ε", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 18, "bold")).pack(anchor="w")
        tk.Label(marco, text="Los símbolos de entrada tienen un carácter. ε representa una transición sin leer entrada.",
                 bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 12))
        campos = {}
        for clave, titulo in (("estados", "Estados (separados por comas)"),
                              ("alfabeto", "Alfabeto (separado por comas)"),
                              ("inicial", "Estado inicial"), ("finales", "Estados finales (puede quedar vacío)")):
            fila = tk.Frame(marco, bg=PANEL)
            fila.pack(fill="x", pady=4)
            tk.Label(fila, text=titulo, bg=PANEL, fg=TEXTO, width=35,
                     anchor="w", font=("Segoe UI", 9)).pack(side="left")
            variable = tk.StringVar(value=self.custom_config[clave])
            ttk.Entry(fila, textvariable=variable, style="Input.TEntry").pack(side="left", fill="x", expand=True)
            campos[clave] = variable
        tk.Label(marco, text="Transiciones: origen,símbolo -> destino1,destino2", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 10, "bold")).pack(anchor="w", pady=(12, 3))
        tk.Label(marco, text="Una regla por línea. Ejemplo: q0,1 -> q0,q1     o     q0,ε -> q1",
                 bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))
        editor = tk.Text(marco, height=10, font=("Consolas", 11), bg=CAMPO, fg=TEXTO,
                         insertbackground=TEXTO, undo=True, wrap="none")
        editor.pack(fill="both", expand=True)
        editor.insert("1.0", self.custom_config["reglas"])
        error = tk.Label(marco, text="", bg=PANEL, fg=ESTADO_ERROR, font=("Segoe UI", 9),
                         anchor="w", justify="left", wraplength=690)
        error.pack(fill="x", pady=(8, 0))

        def aplicar():
            config = {clave: variable.get() for clave, variable in campos.items()}
            config["reglas"] = editor.get("1.0", "end-1c")
            try:
                maquina = nivel3.crear_desde_reglas(**config)
                nivel3.construir_afd(maquina)
            except ValueError as exc:
                error.configure(text=str(exc))
                return
            self.custom_config = config
            self.custom_maquina = maquina
            self._actualizar_concepto()
            self._invalidar_traza()
            self.resultado.configure(text="AFN-ε validado. Escribe una cadena y pulsa Simular cadena.", fg=ACENTO)
            ventana.destroy()

        botones = tk.Frame(marco, bg=PANEL)
        botones.pack(anchor="e", pady=(10, 0))
        ttk.Button(botones, text="Cancelar", style="Quiet.TButton",
                   command=ventana.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(botones, text="Validar y aplicar", style="Accent.TButton",
                   command=aplicar).pack(side="left")

    def _editar_formal(self):
        """Editor avanzado común para AP, LBA y MT, con validación atómica."""
        nivel = self.nivel
        nombre = {2: "AP", 1: "LBA", 0: "MT"}[nivel]
        config_original = self.formal_configs[nivel]
        ventana = tk.Toplevel(self)
        ventana.title(f"Definir {nombre} | Chomsky Lab")
        ventana.geometry("820x710")
        ventana.minsize(650, 580)
        ventana.configure(bg=PANEL)
        ventana.transient(self.winfo_toplevel())
        marco = tk.Frame(ventana, bg=PANEL, padx=20, pady=16)
        marco.pack(fill="both", expand=True)
        tk.Label(marco, text=f"Define tu {nombre} por transiciones", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 18, "bold")).pack(anchor="w")
        explicacion = (
            "AP: estado,entrada,tope -> siguiente,sustitución. ε no consume entrada o desapila; "
            "la sustitución se escribe desde la base hacia el tope."
            if nivel == 2 else
            "Cinta: estado,lee -> siguiente,escribe,mueve. Usa L (izquierda), R (derecha) o S (quieto)."
        )
        tk.Label(marco, text=explicacion, bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9),
                 justify="left", wraplength=760).pack(anchor="w", pady=(3, 12))
        titulos = {"estados": "Estados", "alfabeto": "Alfabeto de entrada",
                   "alfabeto_pila": "Alfabeto de pila", "alfabeto_cinta": "Alfabeto de cinta",
                   "inicial": "Estado inicial", "finales": "Estados finales",
                   "fondo": "Marcador de fondo"}
        campos = {}
        for clave, valor in config_original.items():
            if clave == "reglas":
                continue
            fila = tk.Frame(marco, bg=PANEL)
            fila.pack(fill="x", pady=3)
            tk.Label(fila, text=titulos[clave], bg=PANEL, fg=TEXTO, width=25,
                     anchor="w", font=("Segoe UI", 9)).pack(side="left")
            variable = tk.StringVar(value=valor)
            ttk.Entry(fila, textvariable=variable, style="Input.TEntry").pack(side="left", fill="x", expand=True)
            campos[clave] = variable
        tk.Label(marco, text="Reglas (una por línea)", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 10, "bold")).pack(anchor="w", pady=(12, 4))
        editor = tk.Text(marco, height=12, font=("Consolas", 11), bg=CAMPO, fg=TEXTO,
                         insertbackground=TEXTO, undo=True, wrap="none")
        editor.pack(fill="both", expand=True)
        editor.insert("1.0", config_original["reglas"])
        error = tk.Label(marco, text="", bg=PANEL, fg=ESTADO_ERROR, anchor="w",
                         justify="left", wraplength=760, font=("Segoe UI", 9))
        error.pack(fill="x", pady=(8, 0))

        def aplicar():
            config = {clave: variable.get() for clave, variable in campos.items()}
            config["reglas"] = editor.get("1.0", "end-1c")
            try:
                maquina = (formales.crear_ap(**config) if nivel == 2 else
                           formales.crear_cinta("lba" if nivel == 1 else "mt", **config))
            except ValueError as exc:
                error.configure(text=str(exc))
                return
            self.formal_configs[nivel] = config
            self.formal_maquinas[nivel] = maquina
            self.formal_editada[nivel] = self.formal_editada[nivel] or config != config_original
            self._dibujar_parametros()
            self._actualizar_ejemplos()
            self._actualizar_concepto()
            self._invalidar_traza()
            self.resultado.configure(text=f"{nombre} validado. Introduce una cadena y simula.", fg=ACENTO)
            ventana.destroy()

        botones = tk.Frame(marco, bg=PANEL)
        botones.pack(anchor="e", pady=(10, 0))
        ttk.Button(botones, text="Cancelar", style="Quiet.TButton",
                   command=ventana.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(botones, text="Validar y aplicar", style="Accent.TButton",
                   command=aplicar).pack(side="left")

    def _control_n(self, fila, columnas, maximo):
        """Genera xⁿyⁿ o xⁿyⁿzⁿ sin confundir n con el alfabeto."""
        control = tk.Frame(self.parametros, bg=PANEL)
        control.grid(row=fila, column=0, columnspan=columnas, sticky="w", pady=(8, 0))
        tk.Label(control, text="Repeticiones n =", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 9)).pack(side="left", padx=(0, 7))
        tk.Spinbox(control, from_=1, to=maximo, width=4, textvariable=self.n_var,
                   command=self._actualizar_concepto, font=("Consolas", 10)).pack(side="left")
        ttk.Button(control, text="Generar cadena", style="Quiet.TButton",
                   command=self._generar_con_n).pack(side="left", padx=(8, 0))
        tk.Label(control, text=f"Elige de 1 a {maximo}; se repite cada símbolo n veces.",
                 bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 8)).pack(side="left", padx=(10, 0))

    def _generar_con_n(self):
        """Copia la cadena generada a la entrada y permite editarla antes de simular."""
        maximo = 6 if self.nivel == 2 else 5
        try:
            n = int(self.n_var.get())
        except ValueError:
            n = 0
        simbolos = self._simbolos_configurados()
        if not 1 <= n <= maximo:
            self.resultado.configure(text=f"Elige n entre 1 y {maximo}.", fg=ESTADO_ERROR)
            return
        if any(len(s) != 1 for s in simbolos) or len(set(simbolos)) != len(simbolos):
            self.resultado.configure(text="Cada bloque necesita un símbolo distinto de un carácter.", fg=ESTADO_ERROR)
            return
        if self.nivel == 1 and self.patron_n1_var.get() == "a bⁿ c²ⁿ":
            cadena = simbolos[0] + simbolos[1] * n + simbolos[2] * (2 * n)
        else:
            cadena = "".join(s * n for s in simbolos)
        self.entrada_var.set(cadena)
        self.resultado.configure(text=f"Cadena generada: {cadena}. Pulsa Simular cadena para ver cada paso.", fg=ACENTO)
        self.entrada.focus_set()
        self._actualizar_concepto()

    def _construir_visual(self):
        cabecera = tk.Frame(self.grafico_panel, bg=PANEL)
        cabecera.pack(fill="x", pady=(0, 6))
        tk.Label(cabecera, text="Estructura de la máquina", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 12, "bold")).pack(side="left")
        ttk.Button(cabecera, text="⤢ Ampliar diagrama", style="Quiet.TButton",
                   command=self._abrir_diagrama).pack(side="right")
        marco = tk.Frame(self.grafico_panel, bg=PANEL_ELEVADO, highlightthickness=1, highlightbackground=BORDE)
        marco.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(marco, bg=PANEL_ELEVADO, highlightthickness=0, height=300)
        if self.nivel in (1, 3):
            scrollbar = ttk.Scrollbar(marco, orient="horizontal", command=self.canvas.xview)
            scrollbar.pack(side="bottom", fill="x")
            self.canvas.configure(xscrollcommand=scrollbar.set)
        if self.nivel in (0, 1, 2, 3):
            vertical = ttk.Scrollbar(marco, orient="vertical", command=self.canvas.yview)
            vertical.pack(side="right", fill="y")
            self.canvas.configure(yscrollcommand=vertical.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.after_idle(self._refrescar_grafico))

    def _refrescar_grafico(self):
        """Redibuja al cambiar el tamaño para que la máquina ocupe el ancho real."""
        if self.winfo_exists() and self.canvas.winfo_exists():
            if self.pasos:
                self._dibujar_paso(self.pasos[self.indice])
            else:
                self._dibujar_inicial()

    def _abrir_diagrama(self):
        """Abre una vista independiente y grande del mismo paso de la traza."""
        if self.viewer_canvas is not None and self.viewer_canvas.winfo_exists():
            self.viewer_canvas.winfo_toplevel().lift()
            return
        ventana = tk.Toplevel(self)
        ventana.title("Chomsky Lab | Diagrama ampliado")
        ventana.geometry("1180x780")
        ventana.minsize(720, 500)
        ventana.configure(bg=FONDO_APP)
        tk.Label(ventana, text="Diagrama ampliado · sigue los pasos de la simulación",
                 bg=FONDO_APP, fg=TEXTO, font=("Segoe UI Semibold", 15, "bold"),
                 padx=15, pady=10).pack(anchor="w")
        marco = tk.Frame(ventana, bg=PANEL_ELEVADO)
        marco.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        vertical = ttk.Scrollbar(marco, orient="vertical")
        horizontal = ttk.Scrollbar(marco, orient="horizontal")
        vertical.pack(side="right", fill="y")
        horizontal.pack(side="bottom", fill="x")
        self.viewer_canvas = tk.Canvas(marco, bg=PANEL_ELEVADO, highlightthickness=0,
                                       xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        self.viewer_canvas.pack(side="left", fill="both", expand=True)
        vertical.configure(command=self.viewer_canvas.yview)
        horizontal.configure(command=self.viewer_canvas.xview)
        self.viewer_canvas.bind("<Configure>", lambda _e: self.after_idle(self._render_viewer))
        ventana.protocol("WM_DELETE_WINDOW", lambda: self._cerrar_viewer(ventana))
        self._render_viewer()

    def _cerrar_viewer(self, ventana):
        self.viewer_canvas = None
        ventana.destroy()

    def _render_viewer(self):
        """Dibuja la misma configuración en la ventana ampliada."""
        if self.viewer_canvas is None or not self.viewer_canvas.winfo_exists():
            return
        original = self.canvas
        self.canvas = self.viewer_canvas
        try:
            if self.pasos:
                self._dibujar_paso(self.pasos[self.indice])
            else:
                self._dibujar_inicial()
        finally:
            self.canvas = original

    def _ajustar_canvas(self, ancho_base, alto_base):
        """Escala figuras y fuentes; mantiene scroll si el dibujo supera la altura."""
        c = self.canvas
        ancho_visible = c.winfo_width()
        escala = min(2.0, max(1.0, (ancho_visible - 24) / ancho_base)) if ancho_visible > 1 else 1.0
        if escala != 1.0:
            c.scale("all", 0, 0, escala, escala)
            for item in c.find_all():
                if c.type(item) != "text":
                    continue
                fuente = c.itemcget(item, "font")
                if fuente:
                    actual = tkfont.Font(font=fuente)
                    c.itemconfigure(item, font=(actual.actual("family"),
                                                 max(8, round(actual.actual("size") * escala)),
                                                 actual.actual("weight")))
        c.configure(scrollregion=(0, 0, ancho_base * escala, alto_base * escala))

    def _construir_traza(self):
        tk.Label(self.derecha, text="Recorrido de la máquina", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 15, "bold")).pack(anchor="w")
        tk.Label(self.derecha, text="Cada fila muestra qué leyó y cómo cambió la memoria.",
                 bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 8))
        self.paso_label = tk.Label(self.derecha, text="Aún no hay pasos. Escribe una cadena y pulsa Simular.",
                                   bg=PANEL, fg=TEXTO_SUAVE, font=("Segoe UI", 9), padx=9, pady=7, anchor="w")
        self.paso_label.pack(fill="x", pady=(0, 8))

        marco = tk.Frame(self.derecha, bg=PANEL)
        marco.pack(fill="both", expand=True)
        columnas = ("numero", "lee", "estado", "accion")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", selectmode="browse")
        for clave, titulo in (("numero", "Paso"), ("lee", "Lee"), ("estado", "Estado / conjunto"),
                              ("accion", "Qué pasó")):
            self.tabla.heading(clave, text=titulo)
        self.tabla.column("numero", width=54, minwidth=46, stretch=False, anchor="center")
        self.tabla.column("lee", width=70, minwidth=52, stretch=False, anchor="center")
        self.tabla.column("estado", width=145, minwidth=105, stretch=False)
        self.tabla.column("accion", width=285, minwidth=150, stretch=True)
        scroll_y = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(self.derecha, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(fill="x")
        self.tabla.bind("<<TreeviewSelect>>", self._seleccion_traza)

        self.detalle = tk.Label(self.derecha, text="Elige una fila para leer la explicación del paso.",
                                bg=PANEL, fg=TEXTO, font=("Segoe UI", 9), justify="left",
                                anchor="nw", padx=10, pady=9, wraplength=610, height=3)
        self.detalle.pack(fill="x", pady=(8, 9))
        controles = tk.Frame(self.derecha, bg=PANEL)
        controles.pack(fill="x")
        self.anterior = ttk.Button(controles, text="‹ Anterior", style="Quiet.TButton",
                                   command=lambda: self._navegar(-1), state="disabled")
        self.anterior.pack(side="left")
        self.siguiente = ttk.Button(controles, text="Siguiente ›", style="Quiet.TButton",
                                    command=lambda: self._navegar(1), state="disabled")
        self.siguiente.pack(side="left", padx=7)
        self.play = ttk.Button(controles, text="▶ Reproducir", style="Accent.TButton",
                               command=self._reproducir, state="disabled")
        self.play.pack(side="left")
        self.detener = ttk.Button(controles, text="Detener", style="Quiet.TButton",
                                  command=self._detener, state="disabled")
        self.detener.pack(side="left", padx=7)
        ttk.Combobox(controles, textvariable=self.velocidad_var, state="readonly", width=8,
                     values=("Lenta", "Normal", "Rápida")).pack(side="left", padx=(7, 0))

    def _modo_actual(self):
        if self.modo_var.get() == "Definir mi MT":
            return "formal"
        return "suma" if self.modo_var.get() == "Suma unaria" else "palindromo"

    def _es_formal(self):
        return ((self.nivel == 2 and self.patron_n2_var.get() == "Definir mi AP") or
                (self.nivel == 1 and self.patron_n1_var.get() == "Definir mi LBA") or
                (self.nivel == 0 and self._modo_actual() == "formal"))

    def _parametro_cambiado(self, _evento=None):
        self._actualizar_ejemplos()
        self._actualizar_concepto()
        self._invalidar_traza()

    def _cambio_modo(self, _evento=None):
        if self.nivel == 3 and self.plantilla_var.get() == "Contiene dos iguales seguidos" and self.alfabeto_var.get() == "a,b":
            self.alfabeto_var.set("0,1")
        self._dibujar_parametros()
        self._actualizar_ejemplos()
        self._actualizar_concepto()
        self._invalidar_traza()
        self._dibujar_inicial()

    def _invalidar_traza(self):
        """Evita mostrar pasos de una máquina configurada con reglas anteriores."""
        self._detener()
        self.maquina_afn = None
        self.afd = None
        self.veredicto_final = None
        self.pasos = []
        self.indice = 0
        if hasattr(self, "tabla"):
            self.tabla.delete(*self.tabla.get_children())
            for boton in (self.anterior, self.siguiente, self.play, self.detener):
                boton.configure(state="disabled")
            self.paso_label.configure(text="Configuración actualizada. Simula para ver los pasos nuevos.")
            self.resultado.configure(text="Configuración actualizada; tu cadena sigue en el campo de entrada.", fg=TEXTO_SUAVE)
            self._dibujar_inicial()

    def _simbolos_configurados(self):
        if self.nivel == 3:
            return [s.strip() for s in self.alfabeto_var.get().split(",") if s.strip()]
        if self._es_formal():
            return list(self.formal_maquinas[self.nivel]["alfabeto"])
        if self.nivel == 2:
            return [self.apilar_var.get().strip(), self.desapilar_var.get().strip()]
        if self.nivel == 1:
            return [self.bloque_a_var.get().strip(), self.bloque_b_var.get().strip(), self.bloque_c_var.get().strip()]
        if self._modo_actual() == "palindromo":
            return [s.strip() for s in self.simbolos_tm_var.get().split(",") if s.strip()]
        return []

    def _actualizar_ejemplos(self):
        """Regenera sugerencias al cambiar símbolos; conserva intacta la entrada."""
        if not hasattr(self, "ejemplos"):
            return
        opciones = []
        if self._es_formal():
            opciones = []
        elif self.nivel == 3:
            simbolos = self._simbolos_configurados()
            if self.plantilla_var.get() == "Definir mi AFN-ε":
                opciones = []
            elif self.plantilla_var.get() == "Contiene dos iguales seguidos":
                if len(simbolos) == 2 and len(set(simbolos)) == 2:
                    a, b = simbolos
                    opciones = [(f"Acepta · {a}{a}", a+a, True),
                                (f"Acepta · {a}{b}{b}{a}", a+b+b+a, True),
                                (f"Rechaza · {a}{b}{a}{b}", a+b+a+b, False)]
            else:
                final = self.final_var.get().strip()
                otros = [s for s in simbolos if s != final]
                if len(final) == 1 and final in simbolos:
                    opciones.extend([(f"Acepta · {final}", final, True), (f"Acepta · {final}{final}", final * 2, True)])
                    if otros:
                        opciones.append((f"Rechaza · {otros[0]}", otros[0], False))
                    else:
                        opciones.append(("Rechaza · ε (vacía)", "ε", False))
        elif self.nivel == 2:
            a, b = self.apilar_var.get().strip(), self.desapilar_var.get().strip()
            if len(a) == len(b) == 1 and a != b:
                opciones = [(f"Acepta · {a}{b}", a + b, True), (f"Acepta · {a*2}{b*2}", a*2 + b*2, True),
                            (f"Rechaza · {a*2}{b}", a*2 + b, False), (f"Rechaza · {b}{a}", b + a, False)]
        elif self.nivel == 1:
            a, b, c = (s.strip() for s in (self.bloque_a_var.get(), self.bloque_b_var.get(), self.bloque_c_var.get()))
            if all(len(s) == 1 for s in (a, b, c)) and len({a, b, c}) == 3:
                if self.patron_n1_var.get() == "a bⁿ c²ⁿ":
                    opciones = [(f"Acepta · {a+b+c*2}", a+b+c*2, True),
                                (f"Acepta · {a+b*2+c*4}", a+b*2+c*4, True),
                                (f"Rechaza · {a+b*2+c*3}", a+b*2+c*3, False),
                                (f"Rechaza · {a*2+b+c*2}", a*2+b+c*2, False)]
                else:
                    opciones = [(f"Acepta · {a}{b}{c}", a+b+c, True),
                                (f"Acepta · {a*2}{b*2}{c*2}", a*2+b*2+c*2, True),
                                (f"Rechaza · {a*2}{b}{c*2}", a*2+b+c*2, False),
                                (f"Rechaza · {a}{c}{b}", a+c+b, False)]
        elif self._modo_actual() == "palindromo":
            simbolos = self._simbolos_configurados()
            if len(simbolos) == 2 and simbolos[0] != simbolos[1]:
                a, b = simbolos
                opciones = [(f"Acepta · {a}", a, True), (f"Acepta · {a}{b}{a}", a+b+a, True),
                            (f"Acepta · {a}{b}{b}{a}", a+b+b+a, True),
                            (f"Rechaza · {a}{b}", a+b, False), ("Acepta · ε (vacía)", "ε", True)]
        else:
            opciones = [("Acepta · 111+11", "111+11", True), ("Acepta · 1+1", "1+1", True),
                        ("Acepta · 1111+111", "1111+111", True), ("Rechaza · 11+01", "11+01", False)]

        self.ejemplo_map = {etiqueta: (cadena, acepta) for etiqueta, cadena, acepta in opciones}
        valores = ["Elige un ejemplo opcional", *self.ejemplo_map.keys()]
        self.ejemplos.configure(values=valores)
        self.ejemplo_var.set(valores[0])

    def _seleccion_ejemplo(self, _evento=None):
        seleccionado = self.ejemplo_var.get()
        if seleccionado in self.ejemplo_map:
            cadena, acepta = self.ejemplo_map[seleccionado]
            texto = "Al pulsar Cargar ejemplo, se copiará al campo de entrada."
            self.resultado.configure(text=f"Ejemplo seleccionado ({'normalmente acepta' if acepta else 'normalmente rechaza'}): {cadena}.",
                                     fg=ACENTO if acepta else ESTADO_ATENCION)
            self.detalle.configure(text=texto)

    def _cargar_ejemplo(self):
        seleccionado = self.ejemplo_var.get()
        if seleccionado not in self.ejemplo_map:
            self.resultado.configure(text="Elige un ejemplo de la lista o escribe tu propia cadena.", fg=TEXTO_SUAVE)
            return
        cadena, acepta = self.ejemplo_map[seleccionado]
        self.entrada_var.set("" if cadena == "ε" else cadena)
        self.entrada.focus_set()
        self.resultado.configure(text=f"Ejemplo cargado ({'de aceptación' if acepta else 'de rechazo'}). Puedes editarlo.",
                                 fg=ACENTO if acepta else ESTADO_ATENCION)

    def _actualizar_concepto(self):
        if not hasattr(self, "concepto"):
            return
        if self.nivel == 3:
            if self.plantilla_var.get() == "Definir mi AFN-ε":
                m = self.custom_maquina
                text = (f"AFN-ε propio: {len(m['estados'])} estados, {len(m['alfabeto'])} símbolos, "
                        f"inicial {m['inicial']}. Se calcula el AFD por subconjuntos alcanzables.")
            else:
                text = ("AFN-ε → AFD: sigue ambas ramas; cada estado del AFD es el conjunto de estados alcanzables."
                        if self.plantilla_var.get() == "Contiene dos iguales seguidos" else
                        "AFN → AFD: el AFN mantiene las rutas posibles; el AFD las representa como un conjunto de estados.")
        elif self._es_formal():
            maquina = self.formal_maquinas[self.nivel]
            if self.nivel == 2:
                text = ("AP propio: las reglas δ(estado, entrada/ε, tope) cambian el estado y la pila. "
                        "Se acepta en un estado final tras consumir la entrada.")
            else:
                limite = "entre ⊢ y ⊣" if self.nivel == 1 else "sobre una cinta extendible"
                text = (f"{maquina['tipo'].upper()} propia: cada regla lee, escribe y mueve el cabezal "
                        f"{limite}; se acepta al alcanzar un estado final.")
        elif self.nivel == 2:
            a, b = self.apilar_var.get().strip() or "?", self.desapilar_var.get().strip() or "?"
            text = (f"La forma buscada es {a}ⁿ{b}ⁿ: misma cantidad, primero {a} y después {b}."
                    if len(a) == len(b) == 1 else
                    "Escribe un carácter en cada campo y usa n para indicar cuántas veces se repite.")
        elif self.nivel == 1:
            a = self.bloque_a_var.get().strip() or "?"
            b = self.bloque_b_var.get().strip() or "?"
            c = self.bloque_c_var.get().strip() or "?"
            patron = self.patron_n1_var.get()
            regla = (f"La forma buscada es {a}{b}ⁿ{c}²ⁿ: una {a}, n símbolos {b} y 2n símbolos {c}. "
                     "Este patrón también es libre de contexto."
                     if patron == "a bⁿ c²ⁿ" else
                     f"La forma buscada es {a}ⁿ{b}ⁿ{c}ⁿ: tres bloques ordenados y con la misma cantidad.")
            text = (regla
                    if all(len(s) == 1 for s in (a, b, c)) else
                    "Escribe a, b y c como símbolos de un carácter; el control n genera las repeticiones.")
        elif self._modo_actual() == "suma":
            text = "En unario, 111 representa 3. La entrada 111+11 representa 3 + 2 y la cinta termina como 11111."
        else:
            simbolos = self._simbolos_configurados()
            muestra = " y ".join(simbolos) if len(simbolos) == 2 else "dos símbolos"
            text = f"Un palíndromo se lee igual en ambos sentidos. Este modo permite usar {muestra}."
        self.concepto.configure(text=text)
        # El ejemplo superior se actualiza al editar el alfabeto, sin modificar la cadena escrita.
        if self.nivel == 3:
            if self.plantilla_var.get() == "Definir mi AFN-ε":
                simbolos = ", ".join(self.custom_maquina["alfabeto"])
                ejemplo = f"Ejemplo rápido: prueba una cadena con símbolos de {{{simbolos}}}; decide tu tabla de reglas."
            elif self.plantilla_var.get() == "Contiene dos iguales seguidos":
                simbolos = self._simbolos_configurados()
                a, b = (simbolos + ["0", "1"])[:2]
                ejemplo = f"Ejemplo rápido: {a+b+b+a} acepta porque contiene {b+b}; {a+b+a+b} rechaza."
            else:
                f = self.final_var.get().strip() or "a"
                ejemplo = f"Ejemplo rápido: '{f}' se acepta si está en el alfabeto y es el último símbolo."
        elif self._es_formal():
            simbolos = ", ".join(self.formal_maquinas[self.nivel]["alfabeto"])
            if not self.formal_editada[self.nivel]:
                muestra = {2: "aabb se acepta con las reglas de muestra.",
                           1: "ab se acepta con las reglas de muestra.",
                           0: "111 se transforma en 1111 con las reglas de muestra."}[self.nivel]
                ejemplo = f"Ejemplo inicial: {muestra}"
            else:
                ejemplo = f"Usa símbolos de {{{simbolos}}}; el resultado depende de las reglas δ que definiste."
        elif self.nivel == 2:
            a, b = self.apilar_var.get().strip() or "a", self.desapilar_var.get().strip() or "b"
            n = min(int(self.n_var.get()), 6) if self.n_var.get().isdigit() else 2
            ejemplo = (f"Ejemplo rápido: n={n} genera {a*n+b*n}; la pila guarda {n} marcas."
                       if len(a) == len(b) == 1 else "Ejemplo: escribe a y b; n=2 generará aabb.")
        elif self.nivel == 1:
            a, b, c = (v.get().strip() for v in (self.bloque_a_var, self.bloque_b_var, self.bloque_c_var))
            n = min(int(self.n_var.get()), 5) if self.n_var.get().isdigit() else 2
            muestra = a + b*n + c*(2*n) if self.patron_n1_var.get() == "a bⁿ c²ⁿ" else a*n+b*n+c*n
            ejemplo = (f"Ejemplo rápido: n={n} genera {muestra}; cada ronda marca los símbolos correspondientes."
                       if all(len(s) == 1 for s in (a, b, c)) else
                       "Ejemplo: escribe a, b y c como símbolos sueltos; n genera las repeticiones.")
        elif self._modo_actual() == "suma":
            ejemplo = "Ejemplo rápido: 111+11 → 11111 (3 + 2 = 5 en unario)."
        else:
            a, b = (self._simbolos_configurados() + ["0", "1"])[:2]
            ejemplo = f"Ejemplo rápido: {a+b+a} → se lee igual al derecho y al revés."
        self.ejemplo_rapido.configure(text=ejemplo)

    def _simular(self):
        """Pide la traza al modelo y prepara una fila por configuración."""
        self._detener()
        cadena = self.entrada_var.get()
        try:
            if self.nivel == 3:
                if self.plantilla_var.get() == "Definir mi AFN-ε":
                    resultado = nivel3.simular(cadena, maquina=self.custom_maquina)
                else:
                    plantilla = "pares" if self.plantilla_var.get() == "Contiene dos iguales seguidos" else "final"
                    resultado = nivel3.simular(cadena, self.alfabeto_var.get(), self.final_var.get(), plantilla)
            elif self._es_formal():
                maquina = self.formal_maquinas[self.nivel]
                resultado = (formales.simular_ap(cadena, maquina) if self.nivel == 2 else
                             formales.simular_cinta(cadena, maquina))
            elif self.nivel == 2:
                resultado = nivel2.simular(cadena, self.apilar_var.get(), self.desapilar_var.get())
            elif self.nivel == 1:
                patron = "doble" if self.patron_n1_var.get() == "a bⁿ c²ⁿ" else "iguales"
                resultado = nivel1.simular(cadena, self.bloque_a_var.get(), self.bloque_b_var.get(),
                                           self.bloque_c_var.get(), patron)
            else:
                simbolos = self._simbolos_configurados() if self._modo_actual() == "palindromo" else ("0", "1")
                resultado = nivel0.simular(cadena, self._modo_actual(), simbolos)
        except ValueError as error:
            self.pasos = []
            self.veredicto_final = None
            self.indice = 0
            self.tabla.delete(*self.tabla.get_children())
            self.resultado.configure(text=f"Revisa la configuración: {error}", fg=ESTADO_ERROR)
            self.paso_label.configure(text="No se inició la simulación.")
            self.detalle.configure(text="Corrige los símbolos de la configuración y vuelve a simular.")
            for boton in (self.anterior, self.siguiente, self.play, self.detener):
                boton.configure(state="disabled")
            self._dibujar_inicial()
            return

        self.pasos = resultado["pasos"]
        if self.nivel == 3:
            self.maquina_afn, self.afd = resultado["maquina"], resultado["afd"]
        self.indice = 0
        self.tabla.delete(*self.tabla.get_children())
        for numero, paso in enumerate(self.pasos):
            if self.nivel == 3:
                lee, estado, accion = paso.get("simbolo", "—"), paso.get("estado", ""), paso.get("accion", "")
            elif self.nivel == 2:
                lee, estado, accion = paso.get("simbolo", ""), paso.get("estado", ""), paso.get("accion", "")
            elif self.nivel == 1:
                cabeza, cinta = paso.get("cabeza", 0), paso.get("cinta", ())
                lee = (paso.get("simbolo", "") if self._es_formal() else
                       cinta[cabeza] if 0 <= cabeza < len(cinta) else "")
                estado, accion = paso.get("estado", ""), paso.get("accion", "")
            else:
                lee, estado, accion = paso.get("simbolo", ""), paso.get("estado", ""), paso.get("accion", "")
            self.tabla.insert("", "end", iid=str(numero), values=(numero, lee, estado, accion))

        estado = ("— NO EVALUADA" if resultado.get("aceptada") is None else
                  "✓ ACEPTADA" if resultado["aceptada"] else "✕ RECHAZADA")
        color = ESTADO_ATENCION if resultado.get("aceptada") is None else ESTADO_OK if resultado["aceptada"] else ESTADO_ERROR
        detalle = resultado["mensaje"]
        if detalle.lower().startswith(("aceptada:", "rechazada:")):
            detalle = detalle.split(":", 1)[1].strip()
        mensaje = f"{estado} · {detalle}"
        if resultado.get("salida"):
            mensaje += f"  Resultado en cinta: {resultado['salida']}"
        self.veredicto_final = (mensaje, color, bool(resultado.get("limite")))
        self.anterior.configure(state="normal" if len(self.pasos) > 1 else "disabled")
        self.siguiente.configure(state="normal" if len(self.pasos) > 1 else "disabled")
        self.play.configure(state="normal" if len(self.pasos) > 1 else "disabled")
        self._mostrar_paso(0)
        # Tras iniciar la ejecución, enseña automáticamente el diagrama y la traza.
        self.after_idle(lambda: self.scroller.yview_moveto(1.0))
        if len(self.pasos) > 1 and not resultado.get("limite"):
            self.after_idle(self._reproducir)

    def _mostrar_paso(self, indice):
        """Sincroniza la selección de la tabla, la explicación y el dibujo."""
        if not self.pasos:
            return
        self.indice = max(0, min(indice, len(self.pasos) - 1))
        paso = self.pasos[self.indice]
        self.paso_label.configure(text=f"Paso {self.indice + 1} de {len(self.pasos)}")
        if self.veredicto_final:
            mensaje, color, limite = self.veredicto_final
            if self.indice == len(self.pasos) - 1 or limite:
                self.resultado.configure(text=mensaje, fg=color)
            else:
                self.resultado.configure(
                    text=f"En ejecución · configuración {self.indice + 1} de {len(self.pasos)}. "
                         "Sigue la traza para ver el veredicto.", fg=ACENTO)
        iid = str(self.indice)
        self.tabla.selection_set(iid)
        self.tabla.focus(iid)
        self.tabla.see(iid)
        self.detalle.configure(text=paso.get("accion", ""))
        self._dibujar_paso(paso)
        self._render_viewer()
        self.anterior.configure(state="normal" if self.indice > 0 else "disabled")
        self.siguiente.configure(state="normal" if self.indice < len(self.pasos) - 1 else "disabled")
        self.play.configure(state="disabled" if self.reproduciendo else ("normal" if len(self.pasos) > 1 else "disabled"))
        self.detener.configure(state="normal" if self.reproduciendo else "disabled")

    def _seleccion_traza(self, _evento=None):
        seleccion = self.tabla.selection()
        if seleccion:
            try:
                indice = int(seleccion[0])
            except ValueError:
                return
            if indice != self.indice:
                self._detener()
                self._mostrar_paso(indice)

    def _navegar(self, delta):
        self._detener()
        self._mostrar_paso(self.indice + delta)

    def _reproducir(self):
        if not self.pasos:
            return
        if self.indice >= len(self.pasos) - 1:
            self._mostrar_paso(0)
        self.reproduciendo = True
        self.detener.configure(state="normal")
        self.play.configure(state="disabled")
        self.after_id = self.after(self._demora(), self._avanzar_animacion)

    def _demora(self):
        """Tiempo por configuración; el usuario puede ajustarlo durante el recorrido."""
        return {"Lenta": 650, "Normal": 330, "Rápida": 110}.get(self.velocidad_var.get(), 330)

    def _avanzar_animacion(self):
        if self.indice >= len(self.pasos) - 1:
            self._detener()
            return
        self.after_id = None
        self._mostrar_paso(self.indice + 1)
        if self.indice < len(self.pasos) - 1:
            self.after_id = self.after(self._demora(), self._avanzar_animacion)
        else:
            self._detener()

    def _detener(self):
        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None
        self.reproduciendo = False
        if hasattr(self, "play"):
            self.play.configure(state="normal" if len(self.pasos) > 1 else "disabled")
        if hasattr(self, "detener"):
            self.detener.configure(state="disabled")

    def _vaciar(self):
        self._detener()
        self.entrada_var.set("")
        self.ejemplo_var.set("Elige un ejemplo opcional")
        self.pasos = []
        self.veredicto_final = None
        self.indice = 0
        self.tabla.delete(*self.tabla.get_children())
        self.resultado.configure(text="Campo vacío. Pulsa Simular cadena si quieres probar ε.", fg=TEXTO_SUAVE)
        self.paso_label.configure(text="Aún no hay pasos.")
        self.detalle.configure(text="Una cadena vacía también es una entrada válida para consultar.")
        for boton in (self.anterior, self.siguiente, self.play, self.detener):
            boton.configure(state="disabled")
        self._dibujar_inicial()

    def _volver(self):
        self._detener()
        self.destroy()
        self.volver()

    def _dibujar_inicial(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        self._regla_activa = None
        if self.nivel == 3:
            if self.plantilla_var.get() == "Contiene dos iguales seguidos":
                self._dibujar_afn_ramificado({"activos": ("q0", "r1", "t1"), "aristas": ()})
            elif self.plantilla_var.get() == "Definir mi AFN-ε":
                activos = nivel3.clausura_epsilon(self.custom_maquina, {self.custom_maquina["inicial"]})
                self._dibujar_afn_propio({"activos": tuple(activos), "aristas": ()})
            else:
                self._dibujar_afn_afd(("q0",))
        elif self.nivel == 2:
            if self._es_formal():
                m = self.formal_maquinas[2]
                self._dibujar_pila((m["fondo"],), m["inicial"])
            else:
                self._dibujar_pila(("⊥",), "q₁")
        elif self.nivel == 1:
            self._dibujar_cinta_lba(("⊢", "…", "⊣"), 1,
                                    self.formal_maquinas[1]["inicial"] if self._es_formal() else "inicio")
        else:
            self._dibujar_cinta_tm({}, 0,
                                   self.formal_maquinas[0]["inicial"] if self._es_formal() else "inicio",
                                   self._alfabeto_tm())

    def _dibujar_paso(self, paso):
        self.canvas.delete("all")
        self._regla_activa = paso.get("regla")
        if self.nivel == 3:
            if self.plantilla_var.get() == "Contiene dos iguales seguidos":
                self._dibujar_afn_ramificado(paso)
            elif self.plantilla_var.get() == "Definir mi AFN-ε":
                self._dibujar_afn_propio(paso)
            else:
                self._dibujar_afn_afd(paso.get("activos", ("q0",)))
        elif self.nivel == 2:
            self._dibujar_pila(paso.get("pila", ("⊥",)), paso.get("estado", "q₁"))
        elif self.nivel == 1:
            self._dibujar_cinta_lba(paso.get("cinta", ()), paso.get("cabeza", 0),
                                    paso.get("estado", "inicio"))
        else:
            self._dibujar_cinta_tm(paso.get("cinta", {}), paso.get("cabeza", 0),
                                   paso.get("estado", ""), self._alfabeto_tm())

    def _pintar_grilla(self, canvas, ancho=500, alto=260):
        ancho = max(ancho, canvas.winfo_width())
        alto = max(alto, canvas.winfo_height())
        for x in range(0, ancho, 24):
            canvas.create_line(x, 0, x, alto, fill=GRILLA, tags="grilla")
        for y in range(0, alto, 24):
            canvas.create_line(0, y, ancho, y, fill=GRILLA, tags="grilla")
        canvas.tag_lower("grilla")

    def _dibujar_afn_afd(self, activos):
        """Dibuja el AFN y los dos subconjuntos alcanzables del AFD."""
        c = self.canvas
        self._pintar_grilla(c, 500, 270)
        activos = set(activos)
        final = self.final_var.get().strip() or "f"
        tkfont = ("Segoe UI", 8)
        c.create_text(13, 15, text="AFN", anchor="w", fill=TEXTO,
                      font=("Segoe UI Semibold", 10, "bold"))
        c.create_text(255, 15, text="AFD · subconjuntos", anchor="w", fill=TEXTO,
                      font=("Segoe UI Semibold", 10, "bold"))
        c.create_line(239, 28, 239, 190, fill=BORDE, width=1)

        # AFN: q0 has a Σ loop and may guess that the current final symbol is last.
        self._estado(c, 73, 111, "q0", "q0" in activos)
        self._estado(c, 176, 111, "q1", "q1" in activos, aceptar=True)
        c.create_line(29, 111, 45, 111, fill=TEXTO, width=1.6, arrow=tk.LAST)
        c.create_line(62, 85, 51, 57, 70, 47, 91, 57, 84, 85,
                      smooth=True, splinesteps=18, fill=ACENTO, width=1.7, arrow=tk.LAST)
        c.create_text(71, 39, text="Σ", fill=ACENTO, font=tkfont)
        c.create_line(99, 111, 149, 111, fill=ACENTO, width=1.7, arrow=tk.LAST)
        c.create_text(124, 96, text=final, fill=ACENTO, font=tkfont)
        c.create_text(125, 158, text="q0 puede seguir leyendo; q1 acepta al final", fill=TEXTO_SUAVE,
                      font=("Segoe UI", 7))

        # Subset construction produces only {q0} and {q0, q1} for this language.
        self._estado(c, 294, 111, "{q0}", "q0" in activos, ancho=56)
        self._estado(c, 415, 111, "{q0,q1}", "q1" in activos, aceptar=True, ancho=78)
        c.create_line(258, 111, 266, 111, fill=TEXTO, width=1.6, arrow=tk.LAST)
        c.create_line(285, 84, 275, 57, 293, 47, 311, 57, 303, 84,
                      smooth=True, splinesteps=18, fill=ACENTO, width=1.5, arrow=tk.LAST)
        c.create_text(294, 39, text=f"Σ−{{{final}}}", fill=ACENTO, font=tkfont)
        c.create_line(322, 105, 374, 105, fill=ACENTO, width=1.6, arrow=tk.LAST)
        c.create_text(348, 91, text=final, fill=ACENTO, font=tkfont)
        c.create_line(375, 123, 322, 123, fill=SELECCION, width=1.5, arrow=tk.LAST)
        c.create_text(348, 139, text=f"Σ−{{{final}}}", fill=SELECCION, font=tkfont)
        c.create_line(403, 82, 395, 56, 416, 47, 437, 56, 428, 82,
                      smooth=True, splinesteps=18, fill=ACENTO, width=1.5, arrow=tk.LAST)
        c.create_text(416, 39, text=final, fill=ACENTO, font=tkfont)

        estados = "{" + ", ".join(sorted(activos)) + "}"
        c.create_text(14, 190, text=f"AFN activo: {estados}     Estado equivalente del AFD: {estados}",
                      anchor="w", fill=TEXTO, font=("Segoe UI Semibold", 8))
        c.create_text(14, 222, text="El AFD guarda en un solo estado el conjunto de caminos posibles del AFN.",
                      anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
        c.create_text(14, 246, text=f"Círculo doble = acepta · símbolo final configurado: {final}",
                      anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
        self._ajustar_canvas(500, 280)

    def _dibujar_afn_ramificado(self, paso):
        """Muestra las dos ramas ε y la tabla completa de estados del AFD."""
        c = self.canvas
        activos = set(paso.get("activos", ()))
        aristas = set(paso.get("aristas", ()))
        simbolos = self._simbolos_configurados()
        a, b = (simbolos + ["0", "1"])[:2]
        self._pintar_grilla(c, 500, 780)
        c.create_text(12, 17, text="AFN-ε · dos caminos en paralelo", anchor="w", fill=TEXTO,
                      font=("Segoe UI Semibold", 10, "bold"))
        posiciones = {"q0": (55, 180), "r1": (173, 85), "r2": (302, 85), "r3": (432, 85),
                      "t1": (173, 273), "t2": (302, 273), "t3": (432, 273)}
        c.create_line(10, 180, 27, 180, arrow=tk.LAST, fill=TEXTO, width=2)

        def flecha(origen, destino, simbolo, inicio, fin):
            activa = (origen, simbolo, destino) in aristas
            color = ESTADO_ATENCION if activa else ACENTO
            c.create_line(*inicio, *fin, arrow=tk.LAST, fill=color, width=2.5 if activa else 1.5)
            mx = (inicio[0] + fin[0]) / 2
            my = (inicio[1] + fin[1]) / 2 - (12 if inicio[1] == fin[1] else 7)
            c.create_text(mx, my, text=simbolo, fill=color, font=("Consolas", 9, "bold"))

        flecha("q0", "r1", "ε", (77, 162), (149, 104))
        flecha("q0", "t1", "ε", (77, 198), (149, 254))
        for fila, origen, medio, final, simbolo in ((85, "r1", "r2", "r3", b),
                                                     (273, "t1", "t2", "t3", a)):
            flecha(origen, medio, simbolo, (202, fila), (273, fila))
            flecha(medio, final, simbolo, (331, fila), (403, fila))
            for estado in (origen, final):
                x, y = posiciones[estado]
                color = ESTADO_ATENCION if any(ini == estado and dest == estado for ini, _, dest in aristas) else ACENTO
                c.create_arc(x-24, y-58, x+24, y-8, start=12, extent=322,
                             style="arc", outline=color, width=2)
                c.create_line(x+22, y-19, x+18, y-24, arrow=tk.LAST, fill=color)
                c.create_text(x, y-64, text=f"{a},{b}", fill=color, font=("Consolas", 8))
        for estado, (x, y) in posiciones.items():
            self._estado(c, x, y, estado, estado in activos, aceptar=estado in ("r3", "t3"), ancho=55)

        c.create_text(12, 338, text=f"AFN activo: {nivel3.etiqueta(activos)} · círculo doble = estado final",
                      anchor="w", fill=TEXTO, font=("Segoe UI Semibold", 8))
        c.create_text(12, 372, text="AFD · tabla completa de subconjuntos alcanzables", anchor="w", fill=TEXTO,
                      font=("Segoe UI Semibold", 10, "bold"))
        c.create_text(14, 400, text="Estado del AFD", anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8, "bold"))
        c.create_text(245, 400, text=f"lee {a}", anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8, "bold"))
        c.create_text(365, 400, text=f"lee {b}", anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8, "bold"))
        try:
            maquina = getattr(self, "maquina_afn", None) or nivel3.crear_maquina(self.alfabeto_var.get(), plantilla="pares")
            afd = getattr(self, "afd", None) or nivel3.construir_afd(maquina)
        except ValueError:
            c.create_text(14, 430, text="Corrige el alfabeto para construir la tabla.", anchor="w", fill=ESTADO_ERROR)
            self._ajustar_canvas(500, 470)
            return
        y = 426
        for subconjunto in afd["estados"]:
            nombre = nivel3.etiqueta(subconjunto)
            actual = subconjunto == frozenset(activos)
            if actual:
                c.create_rectangle(8, y-11, 490, y+15, fill=SELECCION_ACTIVA, outline="")
            marca = "★ " if subconjunto in afd["finales"] else "  "
            c.create_text(14, y, text=marca + nombre, anchor="w", fill=TEXTO, font=("Consolas", 8, "bold"))
            for x, simbolo in ((245, a), (365, b)):
                destino = afd["tabla"][(subconjunto, simbolo)]
                c.create_text(x, y, text="→ " + nivel3.etiqueta(destino), anchor="w", fill=TEXTO,
                              font=("Consolas", 8))
            y += 30
        c.create_text(14, y+10, text="★ indica aceptación: el subconjunto contiene r3 o t3.",
                      anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
        self._ajustar_canvas(500, max(780, y+50))

    def _dibujar_afn_propio(self, paso):
        """Genera el grafo y la tabla AFD desde las reglas escritas por el usuario."""
        c = self.canvas
        maquina = self.custom_maquina
        afd = self.afd or nivel3.construir_afd(maquina)
        activos = frozenset(paso.get("activos", ()))
        aristas_activas = set(paso.get("aristas", ()))
        estados = maquina["estados"]
        filas = (len(estados) + 3) // 4
        tabla_y = 170 + filas * 120
        ancho = max(610, 190 + 125 * len(maquina["alfabeto"]))
        alto = tabla_y + 84 + 29 * len(afd["estados"])
        self._pintar_grilla(c, ancho, alto)
        c.create_text(18, 20, text="AFN-ε · definición formal", anchor="w", fill=TEXTO,
                      font=("Segoe UI Semibold", 11, "bold"))
        c.create_text(18, 44,
                      text=f"Q = {nivel3.etiqueta(estados)}    Σ = {nivel3.etiqueta(maquina['alfabeto'])}    "
                           f"q₀ = {maquina['inicial']}    F = {nivel3.etiqueta(maquina['finales'])}",
                      anchor="w", fill=TEXTO_SUAVE, font=("Consolas", 8))
        posiciones = {estado: (76 + (indice % 4) * 140, 150 + (indice // 4) * 140)
                      for indice, estado in enumerate(estados)}
        agrupadas = {}
        for (origen, simbolo), destinos in maquina["transiciones"].items():
            for destino in destinos:
                agrupadas.setdefault((origen, destino), []).append(simbolo)
        for (origen, destino), simbolos in sorted(agrupadas.items()):
            x1, y1 = posiciones[origen]
            x2, y2 = posiciones[destino]
            activa = any((origen, s, destino) in aristas_activas for s in simbolos)
            color = ESTADO_ATENCION if activa else ACENTO
            etiqueta = ",".join(sorted(simbolos))
            if origen == destino:
                c.create_arc(x1-25, y1-60, x1+25, y1-11, start=15, extent=315,
                             style="arc", outline=color, width=2.5 if activa else 1.5)
                c.create_line(x1+23, y1-22, x1+19, y1-26, arrow=tk.LAST, fill=color)
                c.create_text(x1, y1-67, text=etiqueta, fill=color, font=("Consolas", 8, "bold"))
                continue
            dx, dy = x2-x1, y2-y1
            distancia = math.hypot(dx, dy)
            ux, uy = dx/distancia, dy/distancia
            separacion = 15 if (destino, origen) in agrupadas else 0
            px, py = -uy*separacion, ux*separacion
            inicio = (x1+ux*32+px, y1+uy*28+py)
            fin = (x2-ux*32+px, y2-uy*28+py)
            medio = ((inicio[0]+fin[0])/2+px, (inicio[1]+fin[1])/2+py)
            c.create_line(*inicio, *medio, *fin, smooth=True, arrow=tk.LAST,
                          fill=color, width=2.5 if activa else 1.5)
            c.create_text(medio[0], medio[1]-12, text=etiqueta, fill=color,
                          font=("Consolas", 8, "bold"))
        inicio_x, inicio_y = posiciones[maquina["inicial"]]
        c.create_line(inicio_x-62, inicio_y, inicio_x-33, inicio_y,
                      arrow=tk.LAST, fill=TEXTO, width=1.7)
        for estado, (x, y) in posiciones.items():
            self._estado(c, x, y, estado, estado in activos,
                         aceptar=estado in maquina["finales"], ancho=60)

        c.create_text(18, tabla_y-28,
                      text=f"Activos: {nivel3.etiqueta(activos)} · doble círculo = final · resaltado = transición leída",
                      anchor="w", fill=TEXTO, font=("Segoe UI", 9))
        c.create_text(18, tabla_y, text="AFD equivalente · subconjuntos alcanzables",
                      anchor="w", fill=TEXTO, font=("Segoe UI Semibold", 11, "bold"))
        encabezado = tabla_y+29
        c.create_rectangle(10, encabezado-13, ancho-10, encabezado+14,
                           fill=PANEL_ELEVADO, outline="")
        c.create_text(20, encabezado, text="Estado", anchor="w", fill=TEXTO,
                      font=("Consolas", 9, "bold"))
        for columna, simbolo in enumerate(maquina["alfabeto"]):
            c.create_text(190+125*columna, encabezado, text=f"lee {simbolo}", anchor="w",
                          fill=TEXTO, font=("Consolas", 9, "bold"))
        for fila, subconjunto in enumerate(afd["estados"]):
            y = encabezado+31+fila*29
            if subconjunto == activos:
                c.create_rectangle(10, y-13, ancho-10, y+14, fill=SELECCION_ACTIVA, outline="")
            marca = "★ " if subconjunto in afd["finales"] else "  "
            c.create_text(20, y, text=marca+nivel3.etiqueta(subconjunto), anchor="w",
                          fill=TEXTO, font=("Consolas", 8, "bold"))
            for columna, simbolo in enumerate(maquina["alfabeto"]):
                destino = afd["tabla"][(subconjunto, simbolo)]
                c.create_text(190+125*columna, y,
                              text="→ "+nivel3.etiqueta(destino), anchor="w",
                              fill=TEXTO, font=("Consolas", 8))
        self._ajustar_canvas(ancho, alto)

    def _estado(self, canvas, x, y, texto, activo, aceptar=False, ancho=54):
        alto = 50
        color_fondo = SELECCION_ACTIVA if activo else PANEL
        color_borde = ESTADO_ATENCION if activo else BORDE
        canvas.create_oval(x - ancho/2, y - alto/2, x + ancho/2, y + alto/2,
                           fill=color_fondo, outline=color_borde, width=2 if activo else 1.2)
        if aceptar:
            canvas.create_oval(x - ancho/2 + 4, y - alto/2 + 4,
                               x + ancho/2 - 4, y + alto/2 - 4,
                               outline=color_borde, width=1)
        canvas.create_text(x, y, text=texto, fill=TEXTO, font=("Consolas", 8, "bold"))

    def _diagrama_control(self, etapas, activo):
        """Resume visualmente la fase de control que acompaña a pila o cinta."""
        c = self.canvas
        c.create_text(15, 285, text="RUTA DE CONTROL · fase activa", anchor="w", fill=TEXTO,
                      font=("Segoe UI Semibold", 9, "bold"))
        separacion = 400 / max(1, len(etapas) - 1)
        for indice, nombre in enumerate(etapas):
            x = 50 + indice * separacion
            if indice:
                anterior = 50 + (indice - 1) * separacion
                c.create_line(anterior + 32, 329, x - 32, 329,
                              fill=ACENTO, width=1.5, arrow=tk.LAST)
            seleccionado = indice == activo
            c.create_oval(x-30, 307, x+30, 351,
                          fill=SELECCION_ACTIVA if seleccionado else PANEL,
                          outline=ESTADO_ATENCION if seleccionado else ACENTO,
                          width=2 if seleccionado else 1.2)
            c.create_text(x, 329, text=nombre, fill=TEXTO, font=("Segoe UI", 7, "bold"))

    def _diagrama_formal(self, estado_activo):
        """Dibuja estados y todas las reglas; resalta la transición ejecutada."""
        c = self.canvas
        maquina = self.formal_maquinas[self.nivel]
        estados = maquina["estados"]
        filas = (len(estados) + 3) // 4
        ancho = 620
        tabla_y = 410 + filas * 135
        alto = tabla_y + 70 + 26 * len(maquina["reglas"])
        c.create_text(15, 278, text="GRAFO DE CONTROL · transiciones definidas", anchor="w",
                      fill=TEXTO, font=("Segoe UI Semibold", 10, "bold"))
        c.create_text(15, 301,
                      text="Círculo doble = final · resaltado = estado o regla activa · tabla inferior = δ completa",
                      anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
        posiciones = {estado: (68 + (i % 4) * 145, 400 + (i // 4) * 135)
                      for i, estado in enumerate(estados)}
        grupos = {}
        for regla in maquina["reglas"]:
            origen, destino = regla[0], regla[3] if self.nivel == 2 else regla[2]
            grupos.setdefault((origen, destino), []).append(regla)
        for (origen, destino), reglas in sorted(grupos.items()):
            x1, y1 = posiciones[origen]
            x2, y2 = posiciones[destino]
            activa = self._regla_activa in reglas
            color = ESTADO_ATENCION if activa else ACENTO
            etiqueta = ",".join(sorted({r[1] for r in reglas}))
            if len(etiqueta) > 12:
                etiqueta = f"{len(reglas)} reglas"
            if origen == destino:
                c.create_arc(x1-24, y1-58, x1+24, y1-9, start=15, extent=315,
                             style="arc", outline=color, width=2.5 if activa else 1.5)
                c.create_line(x1+22, y1-20, x1+18, y1-24, fill=color, arrow=tk.LAST)
                c.create_text(x1, y1-65, text=etiqueta, fill=color, font=("Consolas", 8))
                continue
            dx, dy = x2-x1, y2-y1
            distancia = math.hypot(dx, dy)
            ux, uy = dx/distancia, dy/distancia
            separacion = 13 if (destino, origen) in grupos else 0
            px, py = -uy*separacion, ux*separacion
            inicio = (x1+ux*33+px, y1+uy*27+py)
            fin = (x2-ux*33+px, y2-uy*27+py)
            c.create_line(*inicio, *fin, fill=color, width=2.5 if activa else 1.5,
                          arrow=tk.LAST)
            c.create_text((inicio[0]+fin[0])/2, (inicio[1]+fin[1])/2-11,
                          text=etiqueta, fill=color, font=("Consolas", 8))
        x0, y0 = posiciones[maquina["inicial"]]
        c.create_line(x0-60, y0, x0-34, y0, fill=TEXTO, arrow=tk.LAST)
        for estado, (x, y) in posiciones.items():
            self._estado(c, x, y, estado, estado == estado_activo,
                         aceptar=estado in maquina["finales"], ancho=62)
        c.create_text(15, tabla_y-4, text="FUNCIÓN DE TRANSICIÓN δ", anchor="w", fill=TEXTO,
                      font=("Segoe UI Semibold", 10, "bold"))
        for indice, regla in enumerate(maquina["reglas"]):
            y = tabla_y + 26 + indice*26
            if regla == self._regla_activa:
                c.create_rectangle(9, y-12, ancho-10, y+12, fill=SELECCION_ACTIVA, outline="")
            if self.nivel == 2:
                q, lee, tope, p, reemplazo = regla
                texto = f"δ({q}, {lee}, {tope}) → ({p}, {reemplazo or 'ε'})"
            else:
                q, lee, p, escribe, mueve = regla
                texto = f"δ({q}, {lee}) → ({p}, {escribe}, {mueve})"
            c.create_text(18, y, text=texto, anchor="w", fill=TEXTO,
                          font=("Consolas", 9))
        return ancho, alto

    def _dibujar_pila(self, pila, estado):
        c = self.canvas
        self._pintar_grilla(c, 500, 260)
        c.create_text(15, 17, text=f"Estado actual: {estado}", anchor="w", fill=TEXTO,
                      font=("Segoe UI Semibold", 9, "bold"))
        c.create_text(245, 40, text="Tope de la pila", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
        c.create_line(245, 45, 245, 58, fill=ESTADO_ATENCION, width=1.7, arrow=tk.LAST)
        for indice, simbolo in enumerate(reversed(pila)):
            y1 = 63 + indice * 25
            y2 = y1 + 22
            c.create_rectangle(207, y1, 283, y2, fill=SELECCION_ACTIVA if indice == 0 else PANEL_ELEVADO,
                               outline=ESTADO_ATENCION if indice == 0 else BORDE, width=1.5)
            c.create_text(245, (y1+y2)/2, text=simbolo, fill=TEXTO,
                          font=("Consolas", 10, "bold"))
        if self._es_formal():
            c.create_text(15, 244, text="El tope está arriba; las reglas deciden qué se apila o se retira.",
                          anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
            self._ajustar_canvas(*self._diagrama_formal(estado))
        else:
            c.create_text(15, 244, text="⊥ es la base. Las A guardan cuántos símbolos faltan emparejar.",
                          anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
            activo = 0 if estado == "q₁" else 1 if estado == "q₂" else 2
            self._diagrama_control(("apilar", "retirar", "decidir"), activo)
            self._ajustar_canvas(500, 370)

    def _dibujar_cinta_lba(self, cinta, cabeza, estado):
        c = self.canvas
        self._pintar_grilla(c, 500, 250)
        c.create_text(14, 17, text="El cabezal puede moverse a izquierda y derecha dentro de la cinta.",
                      anchor="w", fill=TEXTO, font=("Segoe UI", 8))
        if not cinta:
            return
        celda, x0, y = 37, 13, 91
        for indice, simbolo in enumerate(cinta):
            x1 = x0 + indice * celda
            activo = indice == cabeza
            c.create_rectangle(x1, y, x1 + celda - 2, y + 42,
                               fill=SELECCION_ACTIVA if activo else PANEL,
                               outline=ESTADO_ATENCION if activo else BORDE, width=2 if activo else 1)
            c.create_text(x1 + (celda-2)/2, y+21, text=simbolo, fill=TEXTO,
                          font=("Consolas", 10, "bold"))
            c.create_text(x1 + (celda-2)/2, y+56, text=str(indice), fill=TEXTO_SUAVE,
                          font=("Consolas", 7))
        centro = x0 + cabeza*celda + (celda-2)/2
        c.create_line(centro, y-20, centro, y-3, fill=ESTADO_ATENCION, width=1.7, arrow=tk.LAST)
        if self._es_formal():
            texto_marcas = "La cinta solo cambia por las reglas de escritura declaradas."
        else:
            a, b, d = (self.bloque_a_var.get(), self.bloque_b_var.get(), self.bloque_c_var.get())
            texto_marcas = f"X marca {a}   ·   Y marca {b}   ·   Z marca {d}"
        c.create_text(14, 177, text=texto_marcas, anchor="w", fill=TEXTO,
                      font=("Segoe UI", 8))
        c.create_text(14, 214, text="⊢ y ⊣ son límites fijos; el cabezal no los cruza.",
                      anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
        if self._es_formal():
            self._ajustar_canvas(*self._diagrama_formal(estado))
            return
        if estado in ("aceptación", "rechazo", "comprobar fin"):
            activo = 3
        elif estado == "regresar":
            activo = 2
        elif estado.startswith(("buscar", "marcar")):
            activo = 1
        else:
            activo = 0
        self._diagrama_control(("validar", "emparejar", "regresar", "decidir"), activo)
        self._ajustar_canvas(max(500, x0 + len(cinta)*celda + 10), 370)

    def _alfabeto_tm(self):
        if self._es_formal():
            return "{" + ", ".join(self.formal_maquinas[0]["alfabeto_cinta"]) + "}"
        if self._modo_actual() == "suma":
            return "{1, +, □}"
        simbolos = self._simbolos_configurados()
        return "{" + ", ".join([*simbolos, "X", "Y", "□"]) + "}"

    def _dibujar_cinta_tm(self, cinta, cabeza, estado, alfabeto):
        c = self.canvas
        self._pintar_grilla(c, 500, 250)
        c.create_text(14, 17, text=f"Estado: {estado}     Alfabeto de cinta: {alfabeto}",
                      anchor="w", fill=TEXTO, font=("Segoe UI", 8))
        celda, cantidad = 38, 11
        primer_indice = cabeza - cantidad // 2
        x0, y = 14, 91
        for offset in range(cantidad):
            indice = primer_indice + offset
            simbolo = cinta.get(indice, "□")
            x1 = x0 + offset*celda
            activo = indice == cabeza
            c.create_rectangle(x1, y, x1+celda-2, y+43,
                               fill=SELECCION_ACTIVA if activo else PANEL,
                               outline=ESTADO_ATENCION if activo else BORDE, width=2 if activo else 1)
            c.create_text(x1+(celda-2)/2, y+21, text=simbolo, fill=TEXTO,
                          font=("Consolas", 10, "bold"))
            c.create_text(x1+(celda-2)/2, y+57, text=str(indice), fill=TEXTO_SUAVE,
                          font=("Consolas", 7))
        centro = x0 + (cabeza-primer_indice)*celda + (celda-2)/2
        c.create_line(centro, y-20, centro, y-3, fill=ESTADO_ATENCION, width=1.7, arrow=tk.LAST)
        texto = "La ventana acompaña al cabezal; las celdas □ están vacías."
        c.create_text(14, 184, text=texto, anchor="w", fill=TEXTO_SUAVE, font=("Segoe UI", 8))
        if self._es_formal():
            self._ajustar_canvas(*self._diagrama_formal(estado))
            return
        if estado in ("aceptación", "rechazo"):
            activo = 3
        elif estado.startswith(("marcar", "borrar", "reemplazar")):
            activo = 2
        elif estado.startswith(("buscar", "ir", "ubicar")):
            activo = 1
        else:
            activo = 0
        self._diagrama_control(("leer", "buscar", "escribir", "decidir"), activo)
        self._ajustar_canvas(500, 370)

    def _simbolos_tm_actuales(self):
        return tuple(s.strip() for s in self.simbolos_tm_var.get().split(",") if s.strip())
