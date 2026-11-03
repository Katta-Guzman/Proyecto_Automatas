import tkinter as tk
from tkinter import messagebox


def abrir_nivel(nivel):
    messagebox.showinfo(
        "Simulador",
        f"Seleccionaste el Nivel {nivel}\n"
        "Próximamente implementaremos este simulador"
    )


def mostrar_menu():
    ventana = tk.Tk()
    ventana.title("Jerarquía de Chomsky")
    ventana.geometry("550x450")
    ventana.configure(bg="#eaf2f8")

    titulo = tk.Label(
        ventana,
        text="SIMULADOR JERARQUÍA DE CHOMSKY",
        font=("Times New Roman", 16, "bold"),
        bg="#eaf2f8"
    )
    titulo.pack(pady=30)

    niveles = [
        ("Nivel 3 - Autómata Finito", 3),
        ("Nivel 2 - Autómata de Pila", 2),
        ("Nivel 1 - Autómata Linealmente Acotado", 1),
        ("Nivel 0 - Máquina de Turing", 0)
    ]

    for texto, nivel in niveles:
        boton = tk.Button(
            ventana,
            text=texto,
            font=("Times New Roman", 12),
            width=35,
            height=2,
            command=lambda n=nivel: abrir_nivel(n)
        )
        boton.pack(pady=8)

    ventana.mainloop()