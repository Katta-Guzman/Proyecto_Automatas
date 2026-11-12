"""LBA para X^nY^nZ^n, con símbolos de entrada configurables."""


MARCAS = ("X", "Y", "Z")
DELIMITADORES = ("⊢", "⊣")


def simular(cadena: str, simbolo_a: str = "a", simbolo_b: str = "b", simbolo_c: str = "c",
            patron: str = "iguales") -> dict:
    """Reconoce dos lenguajes de bloques con marcas dentro de una cinta acotada."""
    simbolos = tuple(s.strip() for s in (simbolo_a, simbolo_b, simbolo_c))
    if any(len(s) != 1 for s in simbolos):
        raise ValueError("Escribe un carácter por bloque (a, b, c); usa n y Generar cadena para repetirlo.")
    if len(set(simbolos)) != 3:
        raise ValueError("Los tres símbolos deben ser diferentes.")
    if any(s in (*MARCAS, *DELIMITADORES) for s in simbolos):
        raise ValueError("Reserva X, Y, Z, ⊢ y ⊣ para las marcas y los límites de la cinta.")
    if patron == "doble":
        return _simular_doble(cadena, simbolos)
    if patron != "iguales":
        raise ValueError("Elige un patrón disponible.")

    demasiado_larga = len(cadena) > 16
    cinta = ["⊢", "…", "⊣"] if demasiado_larga else ["⊢", *cadena, "⊣"]
    pasos = []
    cabeza = 1

    def guardar(estado: str, accion: str):
        pasos.append({"cinta": tuple(cinta), "cabeza": cabeza, "estado": estado, "accion": accion})

    guardar("inicio", "La cinta de trabajo está limitada por ⊢ y ⊣.")
    if demasiado_larga:
        return {"aceptada": None, "mensaje": "Máximo 16 símbolos para mantener la cinta visible; no se evaluó la cadena.",
                "pasos": pasos, "limite": True}
    if not cadena:
        return {"aceptada": False, "mensaje": "Escribe al menos un símbolo de cada tipo.", "pasos": pasos}

    # Comprueba el orden de los tres bloques antes de iniciar las rondas.
    fase = 0
    vistos = [False, False, False]
    while cabeza < len(cinta) - 1:
        simbolo = cinta[cabeza]
        if simbolo == simbolos[0] and fase == 0:
            vistos[0] = True
        elif simbolo == simbolos[1] and fase <= 1:
            if not vistos[0]:
                guardar("validar orden", "El segundo símbolo apareció antes que el primero.")
                return {"aceptada": False, "mensaje": "El orden de los tres bloques no es válido.", "pasos": pasos}
            fase, vistos[1] = 1, True
        elif simbolo == simbolos[2] and fase in (1, 2):
            if not vistos[1]:
                guardar("validar orden", "El tercer símbolo apareció antes que el segundo.")
                return {"aceptada": False, "mensaje": "El orden de los tres bloques no es válido.", "pasos": pasos}
            fase, vistos[2] = 2, True
        else:
            guardar("validar orden", f"'{simbolo}' rompe el orden de los bloques.")
            return {"aceptada": False, "mensaje": "La cadena debe ser un bloque de cada símbolo, en orden.", "pasos": pasos}
        guardar("validar orden", f"Lee '{simbolo}' y avanza el cabezal.")
        cabeza += 1
        guardar("validar orden", "Movimiento →.")

    if not all(vistos):
        guardar("validar orden", "Falta uno de los tres bloques.")
        return {"aceptada": False, "mensaje": "La cadena necesita los tres tipos de símbolo.", "pasos": pasos}

    while cabeza > 1:
        cabeza -= 1
        guardar("regresar", "Movimiento ← al inicio de la entrada.")

    marca_a, marca_b, marca_c = MARCAS
    while True:
        while cabeza < len(cinta) - 1 and cinta[cabeza] == marca_a:
            cabeza += 1
            guardar("buscar primero", f"{marca_a} ya marca un símbolo emparejado; avanza →.")

        if cabeza >= len(cinta) - 1 or cinta[cabeza] != simbolos[0]:
            sobrantes = [s for s in cinta[1:-1] if s in simbolos]
            if sobrantes:
                guardar("comprobar fin", "Quedan símbolos sin pareja: rechazo.")
                return {"aceptada": False, "mensaje": "Las cantidades de los tres símbolos no coinciden.", "pasos": pasos}
            guardar("aceptación", "Todos los símbolos quedaron emparejados.")
            return {"aceptada": True, "mensaje": "Aceptada: hay la misma cantidad de cada símbolo, en el orden indicado.", "pasos": pasos}

        cinta[cabeza] = marca_a
        guardar("marcar primero", f"Marca '{simbolos[0]}' como {marca_a}.")
        cabeza += 1
        guardar("buscar segundo", "Movimiento → para buscar una pareja del segundo bloque.")
        # En esta ronda puede haber símbolos del primer bloque aún sin marcar.
        # El cabezal los atraviesa hasta encontrar el siguiente símbolo del segundo bloque.
        while cabeza < len(cinta) - 1 and cinta[cabeza] in (simbolos[0], marca_b):
            cabeza += 1
            guardar("buscar segundo", "Avanza → hacia el siguiente símbolo del segundo bloque.")
        if cabeza >= len(cinta) - 1 or cinta[cabeza] != simbolos[1]:
            guardar("rechazo", f"No hay un '{simbolos[1]}' disponible para esta ronda.")
            return {"aceptada": False, "mensaje": f"Hay más '{simbolos[0]}' que '{simbolos[1]}'.", "pasos": pasos}
        cinta[cabeza] = marca_b
        guardar("marcar segundo", f"Marca '{simbolos[1]}' como {marca_b}.")
        cabeza += 1
        guardar("buscar tercero", "Movimiento → para buscar una pareja del tercer bloque.")
        # Igual que antes, atraviesa los símbolos pendientes del segundo bloque.
        while cabeza < len(cinta) - 1 and cinta[cabeza] in (simbolos[1], marca_c):
            cabeza += 1
            guardar("buscar tercero", "Avanza → hacia el siguiente símbolo del tercer bloque.")
        if cabeza >= len(cinta) - 1 or cinta[cabeza] != simbolos[2]:
            guardar("rechazo", f"No hay un '{simbolos[2]}' disponible para esta ronda.")
            return {"aceptada": False, "mensaje": f"Falta un '{simbolos[2]}' en una de las rondas.", "pasos": pasos}
        cinta[cabeza] = marca_c
        guardar("marcar tercero", f"Marca '{simbolos[2]}' como {marca_c}.")
        while cabeza > 1:
            cabeza -= 1
            guardar("regresar", "Movimiento ← para iniciar la siguiente ronda.")


def _simular_doble(cadena, simbolos):
    """LBA para a bⁿ c²ⁿ: marca una b y dos c en cada vuelta."""
    a, b, c = simbolos
    cinta = ["⊢", *(cadena if len(cadena) <= 16 else "…"), "⊣"]
    cabeza = 1
    pasos = []

    def guardar(estado, accion):
        pasos.append({"cinta": tuple(cinta), "cabeza": cabeza,
                      "estado": estado, "accion": accion})

    guardar("inicio", "La cinta está limitada por ⊢ y ⊣.")
    if len(cadena) > 16:
        return {"aceptada": None, "mensaje": "Máximo 16 símbolos para mantener la cinta visible; no se evaluó la cadena.",
                "pasos": pasos, "limite": True}
    if len(cadena) < 4 or cinta[1] != a:
        guardar("rechazo", f"La cadena debe empezar con una sola '{a}'.")
        return {"aceptada": False, "mensaje": f"Se requiere una '{a}', al menos una '{b}' y dos '{c}'.",
                "pasos": pasos}
    cinta[1] = "X"
    guardar("marcar a", f"Marca la única '{a}' como X.")
    cabeza = 2
    guardar("validar orden", "Movimiento → para comprobar el bloque b.")
    fase = 0
    vistos = [False, False]
    while cabeza < len(cinta) - 1:
        simbolo = cinta[cabeza]
        if simbolo == b and fase == 0:
            vistos[0] = True
        elif simbolo == c and vistos[0]:
            fase = 1
            vistos[1] = True
        else:
            guardar("rechazo", f"'{simbolo}' rompe el orden a · bⁿ · c²ⁿ.")
            return {"aceptada": False, "mensaje": "Orden inválido: una a, después b y al final c.",
                    "pasos": pasos}
        guardar("validar orden", f"Lee '{simbolo}' dentro del bloque esperado.")
        cabeza += 1
        guardar("validar orden", "Movimiento →.")
    if not all(vistos):
        guardar("rechazo", "Falta el bloque b o el bloque c.")
        return {"aceptada": False, "mensaje": "Falta al menos un bloque.", "pasos": pasos}
    while cabeza > 2:
        cabeza -= 1
        guardar("regresar", "Movimiento ← hasta el primer b.")

    while True:
        while cinta[cabeza] == "Y":
            cabeza += 1
            guardar("buscar b", "Y ya emparejó una b; movimiento →.")
        if cinta[cabeza] != b:
            if c in cinta[2:-1]:
                guardar("rechazo", "Quedan c sin pareja después de agotar las b.")
                return {"aceptada": False, "mensaje": "Hay más c que el doble de b.", "pasos": pasos}
            guardar("aceptación", "Todas las b y c quedaron marcadas en proporción 1:2.")
            return {"aceptada": True, "mensaje": "Aceptada: una a, n letras b y 2n letras c.", "pasos": pasos}
        cinta[cabeza] = "Y"
        guardar("marcar b", f"Marca una '{b}' como Y: ahora buscará dos '{c}'.")
        cabeza += 1
        guardar("buscar c", "Movimiento → hacia el bloque c.")
        for numero in (1, 2):
            while cabeza < len(cinta) - 1 and cinta[cabeza] in (b, "Z"):
                cabeza += 1
                guardar("buscar c", "Avanza → sobre b pendiente o Z ya marcada.")
            if cabeza >= len(cinta) - 1 or cinta[cabeza] != c:
                guardar("rechazo", f"Falta la c número {numero} para esta b.")
                return {"aceptada": False, "mensaje": "Hay menos c que el doble de b.", "pasos": pasos}
            cinta[cabeza] = "Z"
            guardar("marcar c", f"Marca la c número {numero} de esta ronda como Z.")
            cabeza += 1
            guardar("buscar c", "Movimiento →.")
        while cabeza > 2:
            cabeza -= 1
            guardar("regresar", "Movimiento ← para emparejar la siguiente b.")
