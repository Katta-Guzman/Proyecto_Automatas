"""Vistas interactivas para los cuatro simuladores."""

import tkinter as tk
from tkinter import ttk, messagebox

from modelos import nivel0, nivel1, nivel2, nivel3


FONDO = "#0b1220"
PANEL = "#121d2e"
TEXTO = "#edf4ff"
SUAVE = "#a9b9cd"
ACENTO = "#38d6c0"
VERDE = "#48d597"
ROJO = "#ff7373"

CONFIG = {
    3: {"titulo": "Autómata finito determinista", "subtitulo": "Nivel 3 · Lenguajes regulares",
        "descripcion": "Este DFA acepta las cadenas no vacías cuyo último símbolo coincide con el símbolo final configurado.",
        "ejemplos": ["a", "ba", "baba", "baa", "ε"]},
    2: {"titulo": "Autómata de pila", "subtitulo": "Nivel 2 · Lenguajes libres de contexto",
        "descripcion": "Reconoce L = {aⁿbⁿ | n ≥ 1}. Apila una A por cada a y desapila una A por cada b.",
        "ejemplos": ["ab", "aabb", "aaabbb", "aab", "abba"]},
    1: {"titulo": "Autómata linealmente acotado", "subtitulo": "Nivel 1 · Lenguajes sensibles al contexto",
        "descripcion": "Reconoce L = {aⁿbⁿcⁿ | n ≥ 1}. La máquina usa una cinta limitada por ⊢ y ⊣.",
        "ejemplos": ["abc", "aabbcc", "aaabbbccc", "aabcc", "aabbc"]},
    0: {"titulo": "Máquina de Turing", "subtitulo": "Nivel 0 · Cómputo general",
        "descripcion": "Elige entre reconocer palíndromos binarios o sumar dos enteros representados en unario.",
        "ejemplos": ["0110", "010", "0101", "ε"]},
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
        self.modo_var = tk.StringVar(value="palindromo")
        self.alfabeto_var = tk.StringVar(value="a,b")
        self.final_var = tk.StringVar(value="a")
        self.entrada_var = tk.StringVar()
        self._construir()

    def _construir(self):
        cabecera = ttk.Frame(self)
        cabecera.pack(fill="x", pady=(0, 14))
        ttk.Button(cabecera, text="←  Menú", command=self._volver).pack(side="left")
        titulo = ttk.Frame(cabecera)
        titulo.pack(side="left", padx=18)
        ttk.Label(titulo, text=CONFIG[self.nivel]["subtitulo"], foreground=ACENTO,
                  font=("Segoe UI Semibold", 9, "bold")).pack(anchor="w")
        ttk.Label(titulo, text=CONFIG[self.nivel]["titulo"], style="Heading.TLabel").pack(anchor="w", pady=(2, 0))

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=5, minsize=390)
        cuerpo.columnconfigure(1, weight=6, minsize=440)
        cuerpo.rowconfigure(0, weight=1)
        self.izquierda = tk.Frame(cuerpo, bg=PANEL, padx=16, pady=14)
        self.izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.derecha = tk.Frame(cuerpo, bg=PANEL, padx=14, pady=14)
        self.derecha.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._construir_formulario()
        self._construir_visualizacion()
        self._construir_traza()
        ttk.Label(self, text="Los ejemplos se cargan con un clic; puedes editarlos antes de simular.",
                  foreground=SUAVE).pack(anchor="w", pady=(10, 0))

    def _construir_formulario(self):
        tk.Label(self.izquierda, text="ENTRADA", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 10, "bold")).pack(anchor="w")
        tk.Label(self.izquierda, text=CONFIG[self.nivel]["descripcion"], bg=PANEL, fg=SUAVE,
                 font=("Segoe UI", 9), wraplength=450, justify="left").pack(anchor="w", pady=(5, 10))

        if self.nivel == 0:
            tk.Label(self.izquierda, text="Modelo de Turing", bg=PANEL, fg=TEXTO,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 4))
            modo = ttk.Combobox(self.izquierda, textvariable=self.modo_var, state="readonly",
                                values=("palindromo", "suma"))
            modo.pack(fill="x", pady=(0, 7))
            modo.bind("<<ComboboxSelected>>", self._cambio_modo)
            self.modo_texto = tk.Label(self.izquierda, bg=PANEL, fg=SUAVE, font=("Segoe UI", 9),
                                       justify="left", wraplength=440)
            self.modo_texto.pack(anchor="w", pady=(0, 8))
        if self.nivel == 3:
            fila = ttk.Frame(self.izquierda, style="Panel.TFrame")
            fila.pack(fill="x", pady=(0, 8))
            ttk.Label(fila, text="Alfabeto (separado por coma)", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(fila, text="Símbolo final", style="Panel.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
            ttk.Entry(fila, textvariable=self.alfabeto_var, width=20).grid(row=1, column=0, sticky="ew", pady=(4, 0))
            ttk.Entry(fila, textvariable=self.final_var, width=13).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 0))
            fila.columnconfigure(0, weight=1)
            fila.columnconfigure(1, weight=1)

        fila_entrada = ttk.Frame(self.izquierda, style="Panel.TFrame")
        fila_entrada.pack(fill="x", pady=(0, 7))
        ttk.Label(fila_entrada, text="Cadena", style="Panel.TLabel").pack(anchor="w", pady=(0, 4))
        self.entrada = ttk.Entry(fila_entrada, textvariable=self.entrada_var)
        self.entrada.pack(fill="x")
        self.entrada.bind("<Return>", lambda _evento: self._simular())

        fila_ejemplo = ttk.Frame(self.izquierda, style="Panel.TFrame")
        fila_ejemplo.pack(fill="x", pady=(0, 10))
        ttk.Label(fila_ejemplo, text="Ejemplos", style="Panel.TLabel").pack(side="left", padx=(0, 8))
        self.ejemplo_var = tk.StringVar()
        self.ejemplos = ttk.Combobox(fila_ejemplo, textvariable=self.ejemplo_var, state="readonly")
        self.ejemplos.pack(side="left", fill="x", expand=True)
        self.ejemplos.bind("<<ComboboxSelected>>", self._cargar_ejemplo)
        self._actualizar_ejemplos()

        botones = ttk.Frame(self.izquierda, style="Panel.TFrame")
        botones.pack(fill="x", pady=(0, 9))
        ttk.Button(botones, text="Simular", style="Accent.TButton", command=self._simular).pack(side="left")
        ttk.Button(botones, text="Limpiar", command=self._limpiar).pack(side="left", padx=8)
        self.resultado = tk.Label(self.izquierda, text="Listo para simular.", bg="#0d1928", fg=SUAVE,
                                  font=("Segoe UI Semibold", 9), padx=10, pady=8, anchor="w", justify="left")
        self.resultado.pack(fill="x", pady=(0, 10))
        tk.Label(self.izquierda, text="VISUALIZACIÓN", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 10, "bold")).pack(anchor="w", pady=(0, 5))

    def _construir_visualizacion(self):
        marco = tk.Frame(self.izquierda, bg="#0b1625", highlightthickness=1,
                         highlightbackground="#26384f")
        marco.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(marco, bg="#0b1625", highlightthickness=0, height=260)
        self.canvas.pack(fill="both", expand=True)
        if self.nivel == 1:
            scroll = ttk.Scrollbar(marco, orient="horizontal", command=self.canvas.xview)
            scroll.pack(fill="x", side="bottom")
            self.canvas.configure(xscrollcommand=scroll.set)
        self._dibujar_inicial()

    def _construir_traza(self):
        tk.Label(self.derecha, text="TRAZA DE EJECUCIÓN", bg=PANEL, fg=TEXTO,
                 font=("Segoe UI Semibold", 10, "bold")).pack(anchor="w")
        self.paso_label = tk.Label(self.derecha, text="Ejecuta una entrada para ver los pasos.",
                                   bg=PANEL, fg=SUAVE, font=("Segoe UI", 9))
        self.paso_label.pack(anchor="w", pady=(4, 8))
        marco = tk.Frame(self.derecha, bg=PANEL)
        marco.pack(fill="both", expand=True)
        columnas = ("numero", "lee", "estado", "accion")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", selectmode="browse")
        self.tabla.heading("numero", text="#")
        self.tabla.heading("lee", text="Lee")
        self.tabla.heading("estado", text="Estado")
        self.tabla.heading("accion", text="Transición / acción")
        self.tabla.column("numero", width=46, minwidth=42, stretch=False, anchor="center")
        self.tabla.column("lee", width=54, minwidth=48, stretch=False, anchor="center")
        self.tabla.column("estado", width=115, minwidth=95, stretch=False)
        self.tabla.column("accion", width=250, minwidth=170, stretch=True)
        scroll_y = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(self.derecha, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(fill="x")
        self.tabla.bind("<<TreeviewSelect>>", self._seleccion_traza)
        self.detalle = tk.Label(self.derecha, text="Selecciona una fila para leer la acción completa.",
                                bg="#0d1928", fg=SUAVE, font=("Segoe UI", 9), justify="left",
                                anchor="nw", padx=10, pady=9, wraplength=650, height=3)
        self.detalle.pack(fill="x", pady=(8, 8))
        controles = ttk.Frame(self.derecha, style="Panel.TFrame")
        controles.pack(fill="x")
        self.anterior = ttk.Button(controles, text="← Anterior", command=lambda: self._navegar(-1), state="disabled")
        self.anterior.pack(side="left")
        self.siguiente = ttk.Button(controles, text="Siguiente →", command=lambda: self._navegar(1), state="disabled")
        self.siguiente.pack(side="left", padx=7)
        self.play = ttk.Button(controles, text="▶ Reproducir", command=self._reproducir, state="disabled")
        self.play.pack(side="left")
        self.detener = ttk.Button(controles, text="■ Detener", command=self._detener, state="disabled")
        self.detener.pack(side="left", padx=7)

    def _cambio_modo(self, _evento=None):
        self._actualizar_ejemplos()
        if self.modo_var.get() == "suma":
            self.modo_texto.configure(text="Suma dos números positivos en unario: cada 1 vale una unidad. Ejemplo: 111+11 → 11111.")
        else:
            self.modo_texto.configure(text="Reconoce cadenas binarias que se leen igual en ambos sentidos. Ejemplos: 0110, 010.")

    def _actualizar_ejemplos(self):
        if self.nivel == 0 and self.modo_var.get() == "suma":
            valores = ["111+11", "1+1", "1111+111"]
        else:
            valores = CONFIG[self.nivel]["ejemplos"]
        self.ejemplos.configure(values=valores)
        self.ejemplo_var.set("")
        if self.nivel == 0 and hasattr(self, "modo_texto"):
            self._cambio_modo_texto()

    def _cambio_modo_texto(self):
        if self.modo_var.get() == "suma":
            self.modo_texto.configure(text="Suma dos números positivos en unario: cada 1 vale una unidad. Ejemplo: 111+11 → 11111.")
        else:
            self.modo_texto.configure(text="Reconoce cadenas binarias que se leen igual en ambos sentidos. Ejemplos: 0110, 010.")

    def _cargar_ejemplo(self, _evento=None):
        valor = self.ejemplo_var.get()
        self.entrada_var.set("" if valor == "ε" else valor)
        self.entrada.focus_set()

    def _simular(self):
        self._detener()
        cadena = self.entrada_var.get()
        try:
            if self.nivel == 3:
                resultado = nivel3.simular(cadena, self.alfabeto_var.get(), self.final_var.get())
            elif self.nivel == 2:
                resultado = nivel2.simular(cadena)
            elif self.nivel == 1:
                resultado = nivel1.simular(cadena)
            else:
                resultado = nivel0.simular(cadena, self.modo_var.get())
        except ValueError as error:
            messagebox.showerror("Configuración inválida", str(error), parent=self.winfo_toplevel())
            return

        self.pasos = resultado["pasos"]
        self.indice = 0
        self.tabla.delete(*self.tabla.get_children())
        for numero, paso in enumerate(self.pasos):
            if self.nivel == 3:
                lee = paso.get("simbolo", "—")
                estado = paso.get("estado", "")
                accion = paso.get("accion", "")
            elif self.nivel == 2:
                lee, estado, accion = paso.get("simbolo", ""), paso.get("estado", ""), paso.get("accion", "")
            elif self.nivel == 1:
                cabeza = paso.get("cabeza", 0)
                cinta = paso.get("cinta", ())
                lee = cinta[cabeza] if 0 <= cabeza < len(cinta) else ""
                estado, accion = paso.get("estado", ""), paso.get("accion", "")
            else:
                lee, estado, accion = paso.get("simbolo", ""), paso.get("estado", ""), paso.get("accion", "")
            self.tabla.insert("", "end", iid=str(numero), values=(numero, lee, estado, accion))

        color = VERDE if resultado["aceptada"] else ROJO
        icono = "✓ ACEPTADA" if resultado["aceptada"] else "✕ RECHAZADA"
        extra = f"\nSalida: {resultado['salida']}" if resultado.get("salida") else ""
        self.resultado.configure(text=f"{icono}  ·  {resultado['mensaje']}{extra}", fg=color)
        self.anterior.configure(state="normal" if len(self.pasos) > 1 else "disabled")
        self.siguiente.configure(state="normal" if len(self.pasos) > 1 else "disabled")
        self.play.configure(state="normal" if len(self.pasos) > 1 else "disabled")
        self.detener.configure(state="normal" if len(self.pasos) > 1 else "disabled")
        self._mostrar_paso(0)

    def _mostrar_paso(self, indice):
        if not self.pasos:
            return
        self.indice = max(0, min(indice, len(self.pasos) - 1))
        paso = self.pasos[self.indice]
        self.paso_label.configure(text=f"Paso {self.indice + 1} de {len(self.pasos)}")
        iid = str(self.indice)
        self.tabla.selection_set(iid)
        self.tabla.focus(iid)
        self.tabla.see(iid)
        self.detalle.configure(text=paso.get("accion", ""))
        self._dibujar_paso(paso)
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
                self._mostrar_paso(indice)

    def _navegar(self, delta):
        self._mostrar_paso(self.indice + delta)

    def _reproducir(self):
        if not self.pasos:
            return
        if self.indice >= len(self.pasos) - 1:
            self._mostrar_paso(0)
        self.reproduciendo = True
        self.detener.configure(state="normal")
        self.play.configure(state="disabled")
        self._avanzar_animacion()

    def _avanzar_animacion(self):
        if self.indice >= len(self.pasos) - 1:
            self._detener()
            return
        self.after_id = None
        self._mostrar_paso(self.indice + 1)
        if self.indice < len(self.pasos) - 1:
            self.after_id = self.after(420, self._avanzar_animacion)
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

    def _limpiar(self):
        self._detener()
        self.entrada_var.set("")
        self.pasos = []
        self.indice = 0
        self.tabla.delete(*self.tabla.get_children())
        self.resultado.configure(text="Listo para simular.", fg=SUAVE)
        self.paso_label.configure(text="Ejecuta una entrada para ver los pasos.")
        self.detalle.configure(text="Selecciona una fila para leer la acción completa.")
        for boton in (self.anterior, self.siguiente, self.play, self.detener):
            boton.configure(state="disabled")
        self._dibujar_inicial()

    def _volver(self):
        self._detener()
        self.destroy()
        self.volver()

    def _dibujar_inicial(self):
        self.canvas.delete("all")
        ancho = max(430, self.canvas.winfo_width())
        alto = max(240, self.canvas.winfo_height())
        if self.nivel == 3:
            self._dibujar_dfa("q0")
        elif self.nivel == 2:
            self._dibujar_pila(("⊥",), "q_a")
        elif self.nivel == 1:
            self._dibujar_cinta_lba(("⊢", "…", "⊣"), 1)
        else:
            self._dibujar_cinta_tm({}, 0, "inicio", "{0, 1, X, Y, □}" if self.modo_var.get() == "palindromo" else "{1, +, □}")

    def _dibujar_paso(self, paso):
        self.canvas.delete("all")
        if self.nivel == 3:
            self._dibujar_dfa(paso.get("estado", "q0"))
        elif self.nivel == 2:
            self._dibujar_pila(paso.get("pila", ("⊥",)), paso.get("estado", "q_a"))
        elif self.nivel == 1:
            self._dibujar_cinta_lba(paso.get("cinta", ()), paso.get("cabeza", 0))
        else:
            alfabeto = "{0, 1, X, Y, □}" if self.modo_var.get() == "palindromo" else "{1, +, □}"
            self._dibujar_cinta_tm(paso.get("cinta", {}), paso.get("cabeza", 0), paso.get("estado", ""), alfabeto)

    def _dibujar_dfa(self, actual):
        c = self.canvas
        c.create_text(18, 20, text=f"Estado activo: {actual}     Aceptación: q1", anchor="w", fill=SUAVE,
                      font=("Segoe UI", 9))
        c.create_line(28, 132, 80, 132, fill=SUAVE, width=2, arrow=tk.LAST)
        c.create_oval(80, 92, 160, 172, fill="#176b63" if actual == "q0" else "#142439",
                      outline=ACENTO if actual == "q0" else "#52677f", width=3 if actual == "q0" else 2)
        c.create_text(120, 132, text="q0", fill=TEXTO, font=("Segoe UI Semibold", 14, "bold"))
        c.create_oval(285, 92, 365, 172, fill="#176b63" if actual == "q1" else "#142439",
                      outline=ACENTO if actual == "q1" else "#52677f", width=3 if actual == "q1" else 2)
        c.create_oval(290, 97, 360, 167, outline=ACENTO if actual == "q1" else "#52677f", width=1)
        c.create_text(325, 132, text="q1", fill=TEXTO, font=("Segoe UI Semibold", 14, "bold"))
        c.create_line(160, 117, 285, 117, fill="#8ab4ff", width=2, arrow=tk.LAST)
        c.create_text(222, 102, text="símbolo final", fill="#8ab4ff", font=("Segoe UI", 8))
        c.create_line(285, 151, 160, 151, fill="#ffbd69", width=2, arrow=tk.LAST)
        c.create_text(222, 168, text="otro símbolo", fill="#ffbd69", font=("Segoe UI", 8))
        c.create_text(120, 205, text="Σ − {final} ↺", fill=SUAVE, font=("Segoe UI", 9))
        c.create_text(325, 205, text="{final} ↺", fill=SUAVE, font=("Segoe UI", 9))
        c.create_text(220, 244, text="q1 es final: la última lectura fue el símbolo configurado.", fill=SUAVE,
                      font=("Segoe UI", 8))

    def _dibujar_pila(self, pila, estado):
        c = self.canvas
        c.create_text(18, 20, text=f"Estado: {estado}     Tope de pila ↓", anchor="w", fill=SUAVE,
                      font=("Segoe UI", 9))
        c.create_line(205, 40, 205, 56, fill=ACENTO, width=2, arrow=tk.LAST)
        c.create_text(205, 242, text="La base ⊥ permanece hasta el final.", fill=SUAVE,
                      font=("Segoe UI", 8))
        for indice, simbolo in enumerate(reversed(pila)):
            y1 = 58 + indice * 25
            y2 = y1 + 22
            color = "#176b63" if indice == 0 else "#17263a"
            borde = ACENTO if indice == 0 else "#52677f"
            c.create_rectangle(168, y1, 242, y2, fill=color, outline=borde, width=2)
            c.create_text(205, (y1 + y2) / 2, text=simbolo, fill=TEXTO,
                          font=("Segoe UI Semibold", 11, "bold"))

    def _dibujar_cinta_lba(self, cinta, cabeza):
        c = self.canvas
        c.create_text(14, 18, text="Cinta de longitud fija · el cabezal no cruza ⊢ ni ⊣",
                      anchor="w", fill=SUAVE, font=("Segoe UI", 9))
        if not cinta:
            return
        celda = 34
        inicio_x = 16
        y = 105
        for indice, simbolo in enumerate(cinta):
            x1 = inicio_x + indice * celda
            c.create_rectangle(x1, y, x1 + celda - 2, y + 42,
                               fill="#176b63" if indice == cabeza else "#15243a",
                               outline=ACENTO if indice == cabeza else "#465b74", width=2 if indice == cabeza else 1)
            c.create_text(x1 + (celda - 2) / 2, y + 21, text=simbolo, fill=TEXTO,
                          font=("Segoe UI Semibold", 11, "bold"))
            c.create_text(x1 + (celda - 2) / 2, y + 58, text=str(indice), fill=SUAVE,
                          font=("Segoe UI", 8))
        centro = inicio_x + cabeza * celda + (celda - 2) / 2
        c.create_line(centro, y - 21, centro, y - 3, fill=ACENTO, width=2, arrow=tk.LAST)
        c.create_text(15, 198, text="Marcas: X = a procesada   Y = b procesada   Z = c procesada",
                      anchor="w", fill=SUAVE, font=("Segoe UI", 8))
        c.configure(scrollregion=(0, 0, inicio_x + len(cinta) * celda + 12, 230))

    def _dibujar_cinta_tm(self, cinta, cabeza, estado, alfabeto):
        c = self.canvas
        c.create_text(14, 18, text=f"Estado: {estado}     Alfabeto de cinta: {alfabeto}",
                      anchor="w", fill=SUAVE, font=("Segoe UI", 9))
        celda, cantidad = 38, 11
        primer_indice = cabeza - cantidad // 2
        inicio_x, y = 14, 105
        for offset in range(cantidad):
            indice = primer_indice + offset
            simbolo = cinta.get(indice, "□")
            x1 = inicio_x + offset * celda
            c.create_rectangle(x1, y, x1 + celda - 2, y + 44,
                               fill="#176b63" if indice == cabeza else "#15243a",
                               outline=ACENTO if indice == cabeza else "#465b74", width=2 if indice == cabeza else 1)
            c.create_text(x1 + (celda - 2) / 2, y + 21, text=simbolo, fill=TEXTO,
                          font=("Segoe UI Semibold", 11, "bold"))
            c.create_text(x1 + (celda - 2) / 2, y + 61, text=str(indice), fill=SUAVE,
                          font=("Segoe UI", 8))
        centro = inicio_x + (cabeza - primer_indice) * celda + (celda - 2) / 2
        c.create_line(centro, y - 21, centro, y - 3, fill=ACENTO, width=2, arrow=tk.LAST)
        c.create_text(14, 202, text="La ventana se desplaza con el cabezal; las celdas □ pueden extenderse.",
                      anchor="w", fill=SUAVE, font=("Segoe UI", 8))
