"""AFN con transiciones ε y construcción completa del AFD por subconjuntos."""

from collections import deque

EPSILON = "ε"


def crear_desde_reglas(estados: str, alfabeto: str, inicial: str, finales: str,
                      reglas: str) -> dict:
    """Valida una definición textual de AFN-ε y la convierte en una máquina.

    Formato por línea: origen,símbolo -> destino1,destino2. Un destino vacío
    se omite; las transiciones ausentes significan conjunto vacío.
    """
    nombres = tuple(s.strip() for s in estados.split(","))
    simbolos = tuple(s.strip() for s in alfabeto.split(","))
    finales_lista = tuple(s.strip() for s in finales.split(",") if s.strip())
    inicial = inicial.strip()
    if (not nombres or len(nombres) > 8 or
            any(not s or len(s) > 10 or any(c.isspace() for c in s) for s in nombres)):
        raise ValueError("Define entre 1 y 8 estados con nombres de hasta 10 caracteres sin espacios.")
    if len(set(nombres)) != len(nombres):
        raise ValueError("Hay estados repetidos.")
    if inicial not in nombres or any(s not in nombres for s in finales_lista):
        raise ValueError("El estado inicial y todos los finales deben aparecer en la lista de estados.")
    if len(simbolos) > 6 or any(len(s) != 1 or s == EPSILON for s in simbolos):
        raise ValueError("Define entre 1 y 6 símbolos de un carácter; ε se reserva para transiciones vacías.")
    if len(set(simbolos)) != len(simbolos):
        raise ValueError("Hay símbolos repetidos en el alfabeto.")
    transiciones = {}
    for numero, texto in enumerate(reglas.splitlines(), 1):
        linea = texto.strip()
        if not linea:
            continue
        if linea.count("->") != 1:
            raise ValueError(f"Línea {numero}: usa origen,símbolo -> destino1,destino2.")
        izquierda, derecha = (parte.strip() for parte in linea.split("->"))
        partes = [parte.strip() for parte in izquierda.split(",")]
        destinos = [parte.strip() for parte in derecha.split(",")]
        if len(partes) != 2 or not destinos or any(not d for d in destinos):
            raise ValueError(f"Línea {numero}: la transición está incompleta.")
        origen, simbolo = partes
        if origen not in nombres or any(d not in nombres for d in destinos):
            raise ValueError(f"Línea {numero}: usa solo estados declarados.")
        if simbolo not in (*simbolos, EPSILON):
            raise ValueError(f"Línea {numero}: '{simbolo}' no está en el alfabeto ni es ε.")
        transiciones.setdefault((origen, simbolo), set()).update(destinos)
    return {"estados": nombres, "inicial": inicial, "finales": set(finales_lista),
            "alfabeto": simbolos, "transiciones": transiciones,
            "descripcion": "AFN-ε definido por el usuario."}


def etiqueta(estados):
    """Nombra un subconjunto del AFD de forma estable."""
    return "{" + ",".join(sorted(estados)) + "}" if estados else "∅"


def crear_maquina(alfabeto="a,b", simbolo_final="a", plantilla="final"):
    """Construye una de las dos plantillas como tabla de transiciones de AFN."""
    simbolos = tuple(s.strip() for s in alfabeto.split(","))
    if not simbolos or any(len(s) != 1 or s == EPSILON for s in simbolos):
        raise ValueError("Escribe símbolos únicos de un carácter separados por comas; ε está reservado.")
    if len(set(simbolos)) != len(simbolos):
        raise ValueError("El alfabeto no puede repetir símbolos.")
    if plantilla == "final":
        if simbolo_final not in simbolos:
            raise ValueError("El símbolo final debe pertenecer al alfabeto.")
        transiciones = {("q0", s): {"q0"} for s in simbolos}
        transiciones[("q0", simbolo_final)].add("q1")
        return {"estados": ("q0", "q1"), "inicial": "q0", "finales": {"q1"},
                "alfabeto": simbolos, "transiciones": transiciones,
                "descripcion": f"Acepta cadenas que terminan en {simbolo_final}."}
    if plantilla == "pares":
        if len(simbolos) != 2:
            raise ValueError("La plantilla de pares necesita exactamente dos símbolos, por ejemplo 0,1.")
        a, b = simbolos
        transiciones = {("q0", EPSILON): {"r1", "t1"}}
        for estado in ("r1", "r3", "t1", "t3"):
            for s in simbolos:
                transiciones[(estado, s)] = {estado}
        transiciones[("r1", b)].add("r2")
        transiciones[("r2", b)] = {"r3"}
        transiciones[("t1", a)].add("t2")
        transiciones[("t2", a)] = {"t3"}
        return {"estados": ("q0", "r1", "r2", "r3", "t1", "t2", "t3"),
                "inicial": "q0", "finales": {"r3", "t3"}, "alfabeto": simbolos,
                "transiciones": transiciones,
                "descripcion": f"Acepta cadenas que contienen {a+a} o {b+b} en cualquier posición."}
    raise ValueError("Selecciona una plantilla disponible.")


def clausura_epsilon(maquina, estados):
    """Sigue toda flecha ε alcanzable, incluso si hay ciclos, sin leer entrada."""
    cierre = set(estados)
    pendientes = list(cierre)
    while pendientes:
        origen = pendientes.pop()
        for destino in maquina["transiciones"].get((origen, EPSILON), ()):
            if destino not in cierre:
                cierre.add(destino)
                pendientes.append(destino)
    return frozenset(cierre)


def mover(maquina, estados, simbolo):
    """Une todos los destinos posibles tras leer un símbolo."""
    destinos = set()
    aristas = []
    for origen in sorted(estados):
        for destino in sorted(maquina["transiciones"].get((origen, simbolo), ())):
            destinos.add(destino)
            aristas.append((origen, simbolo, destino))
    return frozenset(destinos), tuple(aristas)


def construir_afd(maquina):
    """Explora por anchura todos los subconjuntos alcanzables y su tabla δ."""
    inicial = clausura_epsilon(maquina, {maquina["inicial"]})
    pendientes = deque([inicial])
    visitados = {inicial}
    tabla = {}
    while pendientes:
        actual = pendientes.popleft()
        for simbolo in maquina["alfabeto"]:
            bruto, _ = mover(maquina, actual, simbolo)
            siguiente = clausura_epsilon(maquina, bruto)
            tabla[(actual, simbolo)] = siguiente
            if siguiente not in visitados:
                visitados.add(siguiente)
                if len(visitados) > 256:
                    raise ValueError("El AFD supera 256 subconjuntos alcanzables. Simplifica el AFN para visualizarlo.")
                pendientes.append(siguiente)
    return {"inicial": inicial,
            "estados": tuple(sorted(visitados, key=lambda s: (len(s), etiqueta(s)))),
            "finales": frozenset(s for s in visitados if s & maquina["finales"]),
            "tabla": tabla}


def simular(cadena: str, alfabeto: str = "a,b", simbolo_final: str = "a", plantilla: str = "final",
            maquina=None) -> dict:
    """Calcula las configuraciones del AFN y el AFD equivalente para toda la entrada."""
    maquina = maquina if maquina is not None else crear_maquina(alfabeto, simbolo_final, plantilla)
    afd = construir_afd(maquina)
    activos = afd["inicial"]
    pasos = [{"pos": 0, "simbolo": EPSILON, "activos": tuple(sorted(activos)),
              "estado": etiqueta(activos), "aristas": (),
              "accion": f"Inicio: clausura ε de {{{maquina['inicial']}}} = {etiqueta(activos)}."}]
    if len(cadena) > 500:
        mensaje = "Máximo 500 símbolos para mantener la animación fluida."
        pasos.append({"pos": 0, "simbolo": "—", "activos": tuple(sorted(activos)),
                      "estado": "límite", "aristas": (), "accion": mensaje})
        return {"aceptada": None, "mensaje": mensaje + " No se evaluó la cadena.", "pasos": pasos,
                "maquina": maquina, "afd": afd, "limite": True}

    for posicion, simbolo in enumerate(cadena, 1):
        if simbolo not in maquina["alfabeto"]:
            mensaje = f"'{simbolo}' no pertenece al alfabeto; posición {posicion}."
            pasos.append({"pos": posicion, "simbolo": simbolo, "activos": tuple(sorted(activos)),
                          "estado": "rechazo", "aristas": (), "accion": mensaje})
            return {"aceptada": False, "mensaje": mensaje, "pasos": pasos,
                    "maquina": maquina, "afd": afd}
        bruto, aristas = mover(maquina, activos, simbolo)
        siguientes = clausura_epsilon(maquina, bruto)
        pasos.append({"pos": posicion, "simbolo": simbolo, "activos": tuple(sorted(siguientes)),
                      "estado": etiqueta(siguientes), "aristas": aristas,
                      "accion": (f"Lee '{simbolo}': desde {etiqueta(activos)} llega a {etiqueta(bruto)}; "
                                 f"clausura ε = {etiqueta(siguientes)}. El AFD llega al mismo conjunto.")})
        activos = siguientes

    aceptada = bool(activos & maquina["finales"])
    mensaje = ("Aceptada: el conjunto activo contiene un estado final."
               if aceptada else "Rechazada: ningún estado activo es final al terminar.")
    pasos.append({"pos": len(cadena) + 1, "simbolo": "fin", "activos": tuple(sorted(activos)),
                  "estado": "aceptación" if aceptada else "rechazo", "aristas": (), "accion": mensaje})
    return {"aceptada": aceptada, "mensaje": mensaje, "pasos": pasos,
            "maquina": maquina, "afd": afd}
