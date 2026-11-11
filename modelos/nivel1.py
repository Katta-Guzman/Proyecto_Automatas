"""Simulador de una LBA para L = {a^n b^n c^n | n >= 1}.

La máquina marca en rondas una a, una b y una c. Solo modifica las celdas de
entrada situadas entre los delimitadores fijos ⊢ y ⊣.
"""


def simular(cadena: str) -> dict:
    demasiado_larga = len(cadena) > 16
    cinta = ["⊢", "…", "⊣"] if demasiado_larga else ["⊢", *cadena, "⊣"]
    pasos = []
    cabeza = 1

    def guardar(estado: str, accion: str):
        pasos.append({"cinta": tuple(cinta), "cabeza": cabeza, "estado": estado, "accion": accion})

    guardar("inicio", "La cinta queda limitada por ⊢ y ⊣.")
    if demasiado_larga:
        return {"aceptada": False, "mensaje": "Máximo 16 símbolos para mantener la traza interactiva ágil.", "pasos": pasos}
    if not cadena:
        return {"aceptada": False, "mensaje": "Se requiere al menos una a, una b y una c.", "pasos": pasos}

    # Comprueba a+ b+ c+ con un cabezal que recorre la cinta hacia la derecha.
    fase = "a"
    vio_a = vio_b = vio_c = False
    while cabeza < len(cinta) - 1:
        simbolo = cinta[cabeza]
        if simbolo == "a" and fase == "a":
            vio_a = True
        elif simbolo == "b" and fase in ("a", "b"):
            if not vio_a:
                guardar("validación", "b antes de cualquier a: rechazo.")
                return {"aceptada": False, "mensaje": "El orden debe ser a* b* c*.", "pasos": pasos}
            fase, vio_b = "b", True
        elif simbolo == "c" and fase in ("b", "c"):
            if not vio_b:
                guardar("validación", "c antes de cualquier b: rechazo.")
                return {"aceptada": False, "mensaje": "El orden debe ser a* b* c*.", "pasos": pasos}
            fase, vio_c = "c", True
        else:
            guardar("validación", f"Símbolo u orden inválido en '{simbolo}': rechazo.")
            return {"aceptada": False, "mensaje": "La cadena debe tener el orden a+ b+ c+.", "pasos": pasos}
        guardar("validar orden", f"Lee {simbolo}; avanza el cabezal.")
        cabeza += 1
        guardar("validar orden", "Movimiento →.")

    if not (vio_a and vio_b and vio_c):
        guardar("validar orden", "Falta uno de los bloques a, b o c: rechazo.")
        return {"aceptada": False, "mensaje": "La cadena debe contener los tres bloques a+ b+ c+.", "pasos": pasos}

    # Reubica el cabezal al inicio de la zona de entrada.
    while cabeza > 1:
        cabeza -= 1
        guardar("regresar", "Movimiento ← hasta el inicio de la entrada.")

    while True:
        # Encuentra la siguiente a sin marcar.
        while cabeza < len(cinta) - 1 and cinta[cabeza] == "X":
            guardar("buscar a", "a ya marcada; avanza →.")
            cabeza += 1
            guardar("buscar a", "Movimiento →.")

        if cabeza >= len(cinta) - 1 or cinta[cabeza] != "a":
            sobrantes = [s for s in cinta[1:-1] if s in ("a", "b", "c")]
            if sobrantes:
                guardar("comprobar fin", "Quedan símbolos sin marcar: rechazo.")
                return {"aceptada": False, "mensaje": "Las cantidades de a, b y c no coinciden.", "pasos": pasos}
            guardar("aceptación", "Todos los símbolos están marcados; acepta.")
            return {"aceptada": True, "mensaje": "Cadena aceptada: se marcaron cantidades iguales de a, b y c.", "pasos": pasos}

        cinta[cabeza] = "X"
        guardar("marcar a", "Escribe X sobre la siguiente a.")
        cabeza += 1
        guardar("buscar b", "Movimiento → para encontrar una b sin marcar.")
        while cabeza < len(cinta) - 1 and cinta[cabeza] == "Y":
            guardar("buscar b", "b ya marcada; avanza →.")
            cabeza += 1
            guardar("buscar b", "Movimiento →.")
        if cabeza >= len(cinta) - 1 or cinta[cabeza] != "b":
            guardar("rechazo", "No existe una b disponible para esta a.")
            return {"aceptada": False, "mensaje": "Hay más a que b.", "pasos": pasos}
        cinta[cabeza] = "Y"
        guardar("marcar b", "Escribe Y sobre una b.")
        cabeza += 1
        guardar("buscar c", "Movimiento → para encontrar una c sin marcar.")
        while cabeza < len(cinta) - 1 and cinta[cabeza] == "Z":
            guardar("buscar c", "c ya marcada; avanza →.")
            cabeza += 1
            guardar("buscar c", "Movimiento →.")
        if cabeza >= len(cinta) - 1 or cinta[cabeza] != "c":
            guardar("rechazo", "No existe una c disponible para esta ronda.")
            return {"aceptada": False, "mensaje": "Hay más a y b que c.", "pasos": pasos}
        cinta[cabeza] = "Z"
        guardar("marcar c", "Escribe Z sobre una c.")
        while cabeza > 1:
            cabeza -= 1
            guardar("regresar", "Movimiento ← para iniciar la siguiente ronda.")
