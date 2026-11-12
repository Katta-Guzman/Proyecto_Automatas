"""Máquinas de Turing para palíndromos configurables y suma unaria."""

import re


def simular(cadena: str, modo: str = "palindromo", simbolos_palindromo=("0", "1")) -> dict:
    """Ejecuta una cinta extendible para palíndromos o suma en unario."""
    cinta = {i: simbolo for i, simbolo in enumerate(cadena)}
    cabeza = 0
    pasos = []

    def leer(posicion):
        return cinta.get(posicion, "□")

    def guardar(estado, accion):
        pasos.append({"cinta": dict(cinta), "cabeza": cabeza, "estado": estado,
                      "simbolo": leer(cabeza), "accion": accion})

    guardar("inicio", "El cabezal comienza en la primera celda; la cinta puede extenderse a ambos lados.")
    if modo == "suma":
        if len(cadena) > 28:
            guardar("límite", "La traza de suma admite hasta 28 caracteres; no se evaluó la entrada.")
            return {"aceptada": None, "mensaje": "Máximo 28 caracteres para la suma; no se evaluó la cadena.",
                    "pasos": pasos, "salida": "", "alfabeto": "{1, +, □}", "limite": True}
        if re.fullmatch(r"1+\+1+", cadena) is None:
            guardar("rechazo", "Escribe dos números positivos en unario, por ejemplo 111+11.")
            return {"aceptada": False, "mensaje": "Formato esperado: unos + unos, sin espacios (ejemplo: 111+11).",
                    "pasos": pasos, "salida": "", "alfabeto": "{1, +, □}"}

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
        guardar("reemplazar +", "Escribe 1 sobre + y une los dos bloques.")
        salida = "".join(leer(i) for i in range(len(cadena)) if leer(i) != "□")
        guardar("aceptación", f"Resultado escrito en la cinta: {salida}.")
        return {"aceptada": True, "mensaje": f"Suma unaria aceptada: {len(salida)} unidades.",
                "pasos": pasos, "salida": salida, "alfabeto": "{1, +, □}"}

    if modo != "palindromo":
        return {"aceptada": False, "mensaje": "Elige un modo disponible.", "pasos": pasos,
                "salida": "", "alfabeto": "{0, 1, X, Y, □}"}

    simbolos = tuple(s.strip() for s in simbolos_palindromo)
    if len(simbolos) != 2 or any(len(s) != 1 for s in simbolos) or simbolos[0] == simbolos[1]:
        raise ValueError("Configura dos símbolos diferentes, separados por coma; por ejemplo: 0,1 o a,b.")
    if any(s in ("X", "Y", "□") for s in simbolos):
        raise ValueError("Reserva X, Y y □ para las marcas y el espacio vacío de la cinta.")
    alfabeto_cinta = f"{{{simbolos[0]}, {simbolos[1]}, X, Y, □}}"
    if len(cadena) > 24:
        guardar("límite", "La traza de palíndromo admite hasta 24 caracteres; no se evaluó la entrada.")
        return {"aceptada": None, "mensaje": "Máximo 24 caracteres para el palíndromo; no se evaluó la cadena.",
                "pasos": pasos, "salida": "", "alfabeto": alfabeto_cinta, "limite": True}
    if any(s not in simbolos for s in cadena):
        guardar("rechazo", "La entrada contiene símbolos fuera del alfabeto.")
        return {"aceptada": False, "mensaje": f"Usa solo {simbolos[0]} y {simbolos[1]}.",
                "pasos": pasos, "salida": "", "alfabeto": alfabeto_cinta}

    while True:
        while leer(cabeza) in ("X", "Y"):
            cabeza += 1
            guardar("buscar símbolo", "Ya está emparejado; avanza →.")
        simbolo = leer(cabeza)
        if simbolo == "□":
            guardar("aceptación", "No quedan símbolos sin emparejar.")
            return {"aceptada": True, "mensaje": "Aceptada: se lee igual de izquierda a derecha que de derecha a izquierda.",
                    "pasos": pasos, "salida": "", "alfabeto": alfabeto_cinta}

        marca = "X" if simbolo == simbolos[0] else "Y"
        cinta[cabeza] = marca
        guardar("marcar izquierda", f"Marca '{simbolo}' con {marca}.")
        cabeza += 1
        guardar("ir al final", "Movimiento → para buscar el extremo derecho.")
        while leer(cabeza) != "□":
            cabeza += 1
            guardar("ir al final", "Movimiento →.")
        cabeza -= 1
        guardar("buscar pareja", "Movimiento ← desde el blanco final.")

        while cabeza >= 0 and leer(cabeza) in ("X", "Y"):
            cabeza -= 1
            guardar("buscar pareja", "Ignora una marca anterior; movimiento ←.")
        pareja = leer(cabeza) if cabeza >= 0 else "□"
        if pareja == "□":
            guardar("aceptación", "No queda pareja sin marcar: el símbolo central coincide consigo mismo.")
            return {"aceptada": True, "mensaje": "Aceptada: la cadena es un palíndromo.", "pasos": pasos,
                    "salida": "", "alfabeto": alfabeto_cinta}
        if pareja != simbolo:
            guardar("rechazo", f"Los extremos no coinciden: '{simbolo}' y '{pareja}'.")
            return {"aceptada": False, "mensaje": "Rechazada: los símbolos de los extremos son diferentes.",
                    "pasos": pasos, "salida": "", "alfabeto": alfabeto_cinta}

        cinta[cabeza] = marca
        guardar("marcar pareja", f"Marca la pareja '{pareja}' con {marca}.")
        while cabeza >= 0:
            cabeza -= 1
            guardar("regresar", "Movimiento ← para volver al inicio.")
        cabeza = 0
        guardar("reiniciar", "Movimiento →; inicia otra ronda.")
