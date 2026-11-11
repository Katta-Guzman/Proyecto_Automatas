"""Máquinas de Turing de un cabezal para palíndromos binarios y suma unaria."""

import re


def simular(cadena: str, modo: str = "palindromo") -> dict:
    cinta = {i: simbolo for i, simbolo in enumerate(cadena)}
    cabeza = 0
    pasos = []

    def leer(posicion):
        return cinta.get(posicion, "□")

    def guardar(estado, accion):
        pasos.append({"cinta": dict(cinta), "cabeza": cabeza, "estado": estado,
                      "simbolo": leer(cabeza), "accion": accion})

    guardar("inicio", "Cabezal en la primera celda no blanca; la cinta puede crecer en ambos sentidos.")
    if modo == "suma":
        if len(cadena) > 28 or re.fullmatch(r"1+\+1+", cadena) is None:
            guardar("rechazo", "Formato inválido: ingresa dos enteros positivos en unario, por ejemplo 111+11.")
            return {"aceptada": False, "mensaje": "Formato esperado: 1+ + 1+ (por ejemplo, 111+11).", "pasos": pasos,
                    "salida": "", "alfabeto": "{1, +, □}"}

        while leer(cabeza) != "□":
            cabeza += 1
            guardar("buscar final", "Movimiento →.")
        cabeza -= 1
        guardar("ubicar último 1", "Movimiento ← desde el blanco final.")
        cinta.pop(cabeza, None)
        guardar("borrar uno", "Borra el último 1 del segundo sumando.")
        while leer(cabeza) != "+":
            cabeza -= 1
            guardar("buscar +", "Movimiento ← hacia el operador.")
        cinta[cabeza] = "1"
        guardar("reemplazar +", "Escribe 1 sobre +; así une ambos bloques unarios.")
        salida = "".join(leer(i) for i in range(len(cadena)) if leer(i) != "□")
        guardar("aceptación", f"Resultado en la cinta: {salida}.")
        return {"aceptada": True, "mensaje": f"Suma unaria aceptada. Resultado: {salida} ({len(salida)}).",
                "pasos": pasos, "salida": salida, "alfabeto": "{1, +, □}"}

    if modo != "palindromo":
        return {"aceptada": False, "mensaje": "Selecciona un modo de simulación válido.", "pasos": pasos,
                "salida": "", "alfabeto": "{0, 1, X, Y, □}"}
    if len(cadena) > 24 or any(s not in "01" for s in cadena):
        guardar("rechazo", "La entrada debe ser binaria y tener como máximo 24 símbolos.")
        return {"aceptada": False, "mensaje": "Este modo acepta entradas de 0 y 1 (máximo 24 símbolos).", "pasos": pasos,
                "salida": "", "alfabeto": "{0, 1, X, Y, □}"}

    while True:
        # Encuentra el símbolo sin marcar más a la izquierda.
        while leer(cabeza) in ("X", "Y"):
            cabeza += 1
            guardar("buscar izquierda", "Símbolo ya emparejado; movimiento →.")
        simbolo = leer(cabeza)
        if simbolo == "□":
            guardar("aceptación", "No quedan símbolos por emparejar.")
            return {"aceptada": True, "mensaje": "Cadena aceptada: es un palíndromo binario.", "pasos": pasos,
                    "salida": "", "alfabeto": "{0, 1, X, Y, □}"}

        marca = "X" if simbolo == "0" else "Y"
        cinta[cabeza] = marca
        guardar("marcar izquierda", f"Marca el {simbolo} más a la izquierda con {marca}.")
        cabeza += 1
        guardar("ir al final", "Movimiento → para buscar el extremo derecho.")
        while leer(cabeza) != "□":
            cabeza += 1
            guardar("ir al final", "Movimiento →.")
        cabeza -= 1
        guardar("buscar pareja", "Movimiento ← desde el blanco hasta la última celda de entrada.")

        while cabeza >= 0 and leer(cabeza) in ("X", "Y"):
            cabeza -= 1
            guardar("buscar pareja", "Ignora un símbolo ya emparejado; movimiento ←.")
        pareja = leer(cabeza) if cabeza >= 0 else "□"
        if pareja == "□":
            guardar("aceptación", "No hay pareja sin marcar; el centro impar coincide consigo mismo.")
            return {"aceptada": True, "mensaje": "Cadena aceptada: es un palíndromo binario.", "pasos": pasos,
                    "salida": "", "alfabeto": "{0, 1, X, Y, □}"}
        if pareja != simbolo:
            guardar("rechazo", f"La pareja esperada era {simbolo}, pero se encontró {pareja}.")
            return {"aceptada": False, "mensaje": "Cadena rechazada: los extremos no coinciden.", "pasos": pasos,
                    "salida": "", "alfabeto": "{0, 1, X, Y, □}"}

        cinta[cabeza] = marca
        guardar("marcar pareja", f"Marca la pareja {pareja} con {marca}.")
        while cabeza >= 0:
            cabeza -= 1
            guardar("regresar", "Movimiento ← para volver al inicio.")
        cabeza = 0
        guardar("reiniciar", "Movimiento →; inicia otra ronda.")
