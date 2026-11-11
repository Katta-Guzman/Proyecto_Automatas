"""Menú principal de la aplicación."""

import tkinter as tk
from tkinter import ttk

from interfaz.simulador import Simulador


FONDO = "#0b1220"
PANEL = "#121d2e"
TARJETA = "#17263a"
TEXTO = "#edf4ff"
SUAVE = "#a9b9cd"
ACENTO = "#38d6c0"


class Aplicacion:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Chomsky Lab | Simulador de autómatas")
        self.ventana.geometry("1180x760")
        self.ventana.minsize(980, 680)
        self.ventana.configure(bg=FONDO)
        self._configurar_estilos()
        self.contenido = None
        self.mostrar_inicio()

    def _configurar_estilos(self):
        estilo = ttk.Style(self.ventana)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=FONDO)
        estilo.configure("Panel.TFrame", background=PANEL)
        estilo.configure("Card.TFrame", background=TARJETA)
        estilo.configure("TLabel", background=FONDO, foreground=TEXTO, font=("Segoe UI", 10))
        estilo.configure("Muted.TLabel", background=FONDO, foreground=SUAVE, font=("Segoe UI", 10))
        estilo.configure("Panel.TLabel", background=PANEL, foreground=TEXTO, font=("Segoe UI", 10))
        estilo.configure("Title.TLabel", background=FONDO, foreground=TEXTO,
                         font=("Segoe UI Semibold", 25, "bold"))
        estilo.configure("Heading.TLabel", background=FONDO, foreground=TEXTO,
                         font=("Segoe UI Semibold", 15, "bold"))
        estilo.configure("CardTitle.TLabel", background=TARJETA, foreground=TEXTO,
                         font=("Segoe UI Semibold", 14, "bold"))
        estilo.configure("CardText.TLabel", background=TARJETA, foreground=SUAVE,
                         font=("Segoe UI", 10), wraplength=410, justify="left")
        estilo.configure("TButton", font=("Segoe UI Semibold", 10), padding=(12, 8),
                         background="#233650", foreground=TEXTO, borderwidth=0)
        estilo.map("TButton", background=[("active", "#304967"), ("disabled", "#253146")])
        estilo.configure("Accent.TButton", background=ACENTO, foreground="#06231f")
        estilo.map("Accent.TButton", background=[("active", "#73e7d5")])
        estilo.configure("TEntry", fieldbackground="#0b1625", foreground=TEXTO,
                         insertcolor=TEXTO, padding=8, borderwidth=1)
        estilo.configure("TCombobox", fieldbackground="#0b1625", foreground=TEXTO,
                         background="#233650", arrowcolor=TEXTO, padding=7)
        estilo.map("TCombobox", fieldbackground=[("readonly", "#0b1625")],
                   foreground=[("readonly", TEXTO)])
        estilo.configure("Treeview", background="#0b1625", fieldbackground="#0b1625",
                         foreground=TEXTO, rowheight=27, borderwidth=0, font=("Segoe UI", 9))
        estilo.configure("Treeview.Heading", background="#20324a", foreground=TEXTO,
                         font=("Segoe UI Semibold", 9, "bold"), relief="flat")
        estilo.map("Treeview", background=[("selected", "#135c58")], foreground=[("selected", "white")])

    def _limpiar(self):
        if self.contenido is not None:
            self.contenido.destroy()
        self.contenido = ttk.Frame(self.ventana, padding=30)
        self.contenido.pack(fill="both", expand=True)

    def mostrar_inicio(self):
        self._limpiar()
        ttk.Label(self.contenido, text="CHOMSKY LAB", foreground=ACENTO,
                  font=("Segoe UI Semibold", 10, "bold")).pack(anchor="w", pady=(8, 10))
        ttk.Label(self.contenido, text="Explora cuatro modelos de cómputo", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.contenido,
                  text="Selecciona un nivel para ejecutar una máquina y observar cada transición.",
                  style="Muted.TLabel").pack(anchor="w", pady=(8, 24))

        tarjetas = ttk.Frame(self.contenido)
        tarjetas.pack(fill="both", expand=True)
        tarjetas.columnconfigure(0, weight=1, uniform="card")
        tarjetas.columnconfigure(1, weight=1, uniform="card")
        tarjetas.rowconfigure(0, weight=1, uniform="row")
        tarjetas.rowconfigure(1, weight=1, uniform="row")

        modulos = [
            (3, "Autómata finito", "Memoria finita. Configura el alfabeto y reconoce cadenas que terminan en un símbolo elegido.", "DFA · lenguaje regular", "#38d6c0"),
            (2, "Autómata de pila", "Memoria LIFO. Observa cómo se apilan y desapilan marcas para reconocer aⁿbⁿ.", "PDA · lenguaje libre de contexto", "#8ab4ff"),
            (1, "Autómata linealmente acotado", "Cinta limitada a la entrada. Marca a, b y c por rondas para reconocer aⁿbⁿcⁿ.", "LBA · lenguaje sensible al contexto", "#ffbd69"),
            (0, "Máquina de Turing", "Cinta extendible y lectura/escritura. Prueba palíndromos binarios o una suma en unario.", "TM · lenguajes recursivamente enumerables", "#d8a4ff"),
        ]
        for indice, (nivel, titulo, descripcion, etiqueta, color) in enumerate(modulos):
            fila, columna = divmod(indice, 2)
            tarjeta = tk.Frame(tarjetas, bg=TARJETA, highlightthickness=1,
                               highlightbackground="#273a52", padx=22, pady=20)
            tarjeta.grid(row=fila, column=columna, sticky="nsew", padx=9, pady=9)
            tk.Label(tarjeta, text=f"NIVEL {nivel}", bg=TARJETA, fg=color,
                     font=("Segoe UI Semibold", 10, "bold")).pack(anchor="w")
            tk.Label(tarjeta, text=titulo, bg=TARJETA, fg=TEXTO,
                     font=("Segoe UI Semibold", 16, "bold")).pack(anchor="w", pady=(7, 6))
            tk.Label(tarjeta, text=descripcion, bg=TARJETA, fg=SUAVE,
                     font=("Segoe UI", 10), wraplength=450, justify="left").pack(anchor="w", pady=(0, 11))
            tk.Label(tarjeta, text=etiqueta, bg=TARJETA, fg="#d2deec",
                     font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(0, 13))
            ttk.Button(tarjeta, text="Abrir simulador  →", style="Accent.TButton",
                       command=lambda n=nivel: self.mostrar_nivel(n)).pack(anchor="w")

        ttk.Label(self.contenido, text="Proyecto educativo · Python 3 + Tkinter · Sin dependencias externas",
                  style="Muted.TLabel").pack(anchor="w", pady=(15, 0))

    def mostrar_nivel(self, nivel):
        if self.contenido is not None:
            self.contenido.destroy()
        self.contenido = Simulador(self.ventana, nivel, self.mostrar_inicio)
        self.contenido.pack(fill="both", expand=True)

    def ejecutar(self):
        self.ventana.mainloop()


def mostrar_menu():
    Aplicacion().ejecutar()
