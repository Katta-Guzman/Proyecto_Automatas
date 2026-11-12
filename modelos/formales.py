"""Intérpretes de máquinas definidas por transiciones, independientes de Tkinter.

El AP y la LBA exploran configuraciones alcanzables. La MT es un reconocedor:
si alguna rama no termina o se agota el presupuesto, el resultado es inconcluso.
"""

from collections import deque


EPSILON = "ε"
BLANCO = "□"
IZQUIERDA = "⊢"
DERECHA = "⊣"
MAX_CONFIGURACIONES = 5000
MAX_PASOS = 1000
MAX_ENTRADA = 500


def _lista(texto, nombre, maximo, *, vacia=False, un_caracter=False):
    valores = tuple(p.strip() for p in texto.split(",")) if texto.strip() else ()
    if (not vacia and not valores) or len(valores) > maximo or any(not v for v in valores):
        raise ValueError(f"{nombre}: define entre {0 if vacia else 1} y {maximo} valores separados por comas.")
    if len(set(valores)) != len(valores):
        raise ValueError(f"{nombre}: hay valores repetidos.")
    if un_caracter and any(len(v) != 1 for v in valores):
        raise ValueError(f"{nombre}: cada símbolo debe tener un carácter.")
    if not un_caracter and any(len(v) > 10 or any(c.isspace() for c in v) for v in valores):
        raise ValueError(f"{nombre}: usa nombres de hasta 10 caracteres sin espacios.")
    return valores


def _comun(estados, alfabeto, inicial, finales):
    q = _lista(estados, "Estados", 8)
    sigma = _lista(alfabeto, "Alfabeto de entrada", 6, un_caracter=True)
    f = _lista(finales, "Finales", 8, vacia=True)
    inicial = inicial.strip()
    if inicial not in q or any(estado not in q for estado in f):
        raise ValueError("El inicial y todos los finales deben figurar en los estados.")
    if EPSILON in sigma:
        raise ValueError("ε no es un símbolo de entrada; representa una lectura vacía.")
    return q, sigma, inicial, frozenset(f)


def _partes(linea, numero, izquierda, derecha):
    if linea.count("->") != 1:
        raise ValueError(f"Línea {numero}: falta la flecha -> o hay más de una.")
    origen, destino = (p.strip() for p in linea.split("->"))
    l = tuple(p.strip() for p in origen.split(","))
    r = tuple(p.strip() for p in destino.split(","))
    if len(l) != izquierda or len(r) != derecha or any(not p for p in (*l, *r)):
        raise ValueError(f"Línea {numero}: se esperan {izquierda} campos antes y {derecha} después de ->.")
    return l, r


def crear_ap(estados, alfabeto, alfabeto_pila, inicial, finales, fondo, reglas):
    """AP no determinista. Una sustitución se escribe de base a tope."""
    q, sigma, q0, f = _comun(estados, alfabeto, inicial, finales)
    gamma = _lista(alfabeto_pila, "Alfabeto de pila", 8, un_caracter=True)
    fondo = fondo.strip()
    if fondo not in gamma or EPSILON in gamma:
        raise ValueError("El fondo debe estar en el alfabeto de pila; ε está reservado.")
    tabla = {}
    lista_reglas = []
    for numero, texto in enumerate(reglas.splitlines(), 1):
        linea = texto.strip()
        if not linea:
            continue
        (estado, lee, tope), (siguiente, reemplazo) = _partes(linea, numero, 3, 2)
        if estado not in q or siguiente not in q or lee not in (*sigma, EPSILON) or tope not in gamma:
            raise ValueError(f"Línea {numero}: estado, entrada o tope no declarados.")
        if reemplazo == EPSILON:
            reemplazo = ""
        if any(s not in gamma for s in reemplazo):
            raise ValueError(f"Línea {numero}: la sustitución usa símbolos fuera del alfabeto de pila.")
        if tope == fondo and (not reemplazo.startswith(fondo) or reemplazo.count(fondo) != 1):
            raise ValueError(f"Línea {numero}: conserva el marcador de fondo al sustituirlo.")
        if tope != fondo and fondo in reemplazo:
            raise ValueError(f"Línea {numero}: no dupliques el marcador de fondo.")
        clave = (estado, lee, tope)
        transicion = (siguiente, reemplazo)
        if transicion not in tabla.setdefault(clave, []):
            tabla[clave].append(transicion)
            lista_reglas.append((estado, lee, tope, siguiente, reemplazo))
    if len(lista_reglas) > 40:
        raise ValueError("Máximo 40 reglas para mantener legible el diagrama.")
    return {"tipo": "ap", "estados": q, "alfabeto": sigma, "pila_alfabeto": gamma,
            "inicial": q0, "finales": f, "fondo": fondo,
            "tabla": tabla, "reglas": tuple(lista_reglas)}


def crear_cinta(tipo, estados, alfabeto, alfabeto_cinta, inicial, finales, reglas):
    """Valida una LBA o MT con reglas (estado,lee) -> (estado,escribe,mueve)."""
    if tipo not in ("lba", "mt"):
        raise ValueError("Tipo de máquina desconocido.")
    q, sigma, q0, f = _comun(estados, alfabeto, inicial, finales)
    gamma = _lista(alfabeto_cinta, "Alfabeto de cinta", 10, un_caracter=True)
    if any(s not in gamma for s in sigma):
        raise ValueError("El alfabeto de entrada debe estar incluido en el alfabeto de cinta.")
    if tipo == "mt" and BLANCO not in gamma:
        raise ValueError("La MT necesita el blanco □ en el alfabeto de cinta.")
    if tipo == "lba" and (IZQUIERDA not in gamma or DERECHA not in gamma):
        raise ValueError("La LBA necesita ⊢ y ⊣ en el alfabeto de cinta.")
    if any(s in sigma for s in (BLANCO, IZQUIERDA, DERECHA)):
        raise ValueError("Los delimitadores y el blanco no pueden ser símbolos de entrada.")
    tabla = {}
    lista_reglas = []
    for numero, texto in enumerate(reglas.splitlines(), 1):
        linea = texto.strip()
        if not linea:
            continue
        (estado, lee), (siguiente, escribe, mueve) = _partes(linea, numero, 2, 3)
        if estado not in q or siguiente not in q or lee not in gamma or escribe not in gamma:
            raise ValueError(f"Línea {numero}: estado o símbolo de cinta no declarado.")
        if mueve not in ("L", "R", "S"):
            raise ValueError(f"Línea {numero}: movimiento debe ser L, R o S.")
        if tipo == "lba" and lee in (IZQUIERDA, DERECHA) and escribe != lee:
            raise ValueError(f"Línea {numero}: no puedes borrar un delimitador de la LBA.")
        if tipo == "lba" and ((lee == IZQUIERDA and mueve == "L") or
                              (lee == DERECHA and mueve == "R")):
            raise ValueError(f"Línea {numero}: el cabezal no puede cruzar los delimitadores.")
        if tipo == "lba" and lee not in (IZQUIERDA, DERECHA) and escribe in (IZQUIERDA, DERECHA):
            raise ValueError(f"Línea {numero}: no puedes crear delimitadores nuevos.")
        clave = (estado, lee)
        transicion = (siguiente, escribe, mueve)
        if transicion not in tabla.setdefault(clave, []):
            tabla[clave].append(transicion)
            lista_reglas.append((estado, lee, siguiente, escribe, mueve))
    if len(lista_reglas) > 60:
        raise ValueError("Máximo 60 reglas para mantener legible el diagrama.")
    return {"tipo": tipo, "estados": q, "alfabeto": sigma, "alfabeto_cinta": gamma,
            "inicial": q0, "finales": f, "tabla": tabla, "reglas": tuple(lista_reglas)}


def _ruta(padres, final):
    ruta = []
    actual = final
    while actual is not None:
        anterior, leido, accion, regla = padres[actual]
        ruta.append((actual, leido, accion, regla))
        actual = anterior
    ruta.reverse()
    return ruta


def simular_ap(cadena, maquina):
    """Explora rutas de un AP no determinista, incluidas transiciones ε."""
    if len(cadena) > MAX_ENTRADA:
        fondo = maquina["fondo"]
        mensaje = f"Máximo {MAX_ENTRADA} símbolos; la entrada no se evaluó."
        pasos = [{"pos": 0, "simbolo": EPSILON, "pila": (fondo,),
                  "estado": maquina["inicial"], "accion": mensaje, "regla": None}]
        return {"aceptada": None, "mensaje": mensaje, "pasos": pasos, "limite": True}
    inicial = (maquina["inicial"], 0, (maquina["fondo"],))
    for posicion, simbolo in enumerate(cadena, 1):
        if simbolo not in maquina["alfabeto"]:
            mensaje = f"Rechazada: '{simbolo}' no pertenece al alfabeto en la posición {posicion}."
            pasos = [
                {"pos": 0, "simbolo": "—", "pila": inicial[2], "estado": inicial[0],
                 "accion": "Configuración inicial del AP.", "regla": None},
                {"pos": posicion, "simbolo": simbolo, "pila": inicial[2], "estado": "rechazo",
                 "accion": mensaje, "regla": None},
            ]
            return {"aceptada": False, "mensaje": mensaje, "pasos": pasos, "limite": False}
    pendientes = deque([inicial])
    padres = {inicial: (None, EPSILON, "Pila inicial con marcador de fondo.", None)}
    profundidad = {inicial: 0}
    mejor = inicial
    inconclusa = False
    aceptacion = None
    while pendientes:
        actual = pendientes.popleft()
        estado, posicion, pila = actual
        if posicion > mejor[1] or profundidad[actual] > profundidad[mejor]:
            mejor = actual
        if posicion == len(cadena) and estado in maquina["finales"]:
            aceptacion = actual
            break
        if profundidad[actual] >= MAX_PASOS:
            inconclusa = True
            continue
        lecturas = [EPSILON]
        if posicion < len(cadena):
            lecturas.append(cadena[posicion])
        for lee in lecturas:
            for siguiente, reemplazo in maquina["tabla"].get((estado, lee, pila[-1]), ()):
                nueva_pila = pila[:-1] + tuple(reemplazo)
                if len(nueva_pila) > 64:
                    inconclusa = True
                    continue
                nuevo = (siguiente, posicion + (lee != EPSILON), nueva_pila)
                if nuevo in padres:
                    continue
                if len(padres) >= MAX_CONFIGURACIONES:
                    inconclusa = True
                    pendientes.clear()
                    break
                accion = (f"δ({estado}, {lee}, {pila[-1]}) → ({siguiente}, "
                          f"{reemplazo or EPSILON}); pila: {''.join(pila)} → {''.join(nueva_pila)}.")
                regla = (estado, lee, pila[-1], siguiente, reemplazo)
                padres[nuevo] = (actual, lee, accion, regla)
                profundidad[nuevo] = profundidad[actual] + 1
                pendientes.append(nuevo)
            if inconclusa and len(padres) >= MAX_CONFIGURACIONES:
                break
    final = aceptacion if aceptacion is not None else mejor
    pasos = []
    for (estado, posicion, pila), leido, accion, regla in _ruta(padres, final):
        pasos.append({"pos": posicion, "simbolo": leido, "pila": pila,
                      "estado": estado, "accion": accion, "regla": regla})
    if aceptacion is not None:
        aceptada, titulo = True, "Aceptada: llegó a un estado final tras consumir toda la entrada."
    elif inconclusa:
        aceptada, titulo = None, "No evaluada: se alcanzó el presupuesto de búsqueda del AP."
    else:
        aceptada, titulo = False, "Rechazada: se agotaron todas las configuraciones alcanzables sin aceptación."
    pasos.append({"pos": final[1], "simbolo": "fin", "pila": final[2],
                  "estado": "aceptación" if aceptada else "límite" if aceptada is None else "rechazo",
                  "accion": titulo + f" Configuraciones exploradas: {len(padres)}.", "regla": None})
    return {"aceptada": aceptada, "mensaje": titulo, "pasos": pasos,
            "limite": aceptada is None, "exploradas": len(padres)}


def _lectura_cinta(tipo, cinta, cabeza):
    return cinta[cabeza] if tipo == "lba" else dict(cinta).get(cabeza, BLANCO)


def _configuracion_es_ancestro(padres, candidata, actual):
    """Comprueba si repetir esta configuración cierra un ciclo de una ruta."""
    while actual is not None:
        if actual == candidata:
            return True
        actual = padres[actual][0]
    return False


def simular_cinta(cadena, maquina):
    """Explora la LBA finita o la MT; conserva una ruta testigo en la traza."""
    tipo = maquina["tipo"]
    if len(cadena) > MAX_ENTRADA:
        if tipo == "lba":
            cinta = (IZQUIERDA, "…", DERECHA)
            cabeza = 1
        else:
            cinta, cabeza = {}, 0
        mensaje = f"Máximo {MAX_ENTRADA} símbolos; la entrada no se evaluó."
        pasos = [{"cinta": cinta, "cabeza": cabeza, "estado": maquina["inicial"],
                  "simbolo": "—", "accion": mensaje, "regla": None}]
        return {"aceptada": None, "mensaje": mensaje, "pasos": pasos, "limite": True,
                "alfabeto": "{" + ", ".join(maquina["alfabeto_cinta"]) + "}"}
    if tipo == "lba":
        cinta = (IZQUIERDA, *cadena, DERECHA)
        inicial = (maquina["inicial"], 1, cinta)
    else:
        cinta = tuple((i, s) for i, s in enumerate(cadena))
        inicial = (maquina["inicial"], 0, cinta)
    for posicion, simbolo in enumerate(cadena, 1):
        if simbolo not in maquina["alfabeto"]:
            mensaje = f"Rechazada: '{simbolo}' no pertenece al alfabeto en la posición {posicion}."
            memoria = inicial[2] if tipo == "lba" else dict(inicial[2])
            pasos = [
                {"cinta": memoria, "cabeza": inicial[1], "estado": inicial[0],
                 "simbolo": "—", "accion": "Configuración inicial de la máquina.", "regla": None},
                {"cinta": memoria, "cabeza": inicial[1], "estado": "rechazo",
                 "simbolo": simbolo, "accion": mensaje, "regla": None},
            ]
            return {"aceptada": False, "mensaje": mensaje, "pasos": pasos, "limite": False,
                    "alfabeto": "{" + ", ".join(maquina["alfabeto_cinta"]) + "}"}
    pendientes = deque([inicial])
    padres = {inicial: (None, "—", "Configuración inicial.", None)}
    profundidad = {inicial: 0}
    mejor = inicial
    aceptacion = None
    inconclusa = False
    while pendientes:
        actual = pendientes.popleft()
        estado, cabeza, cinta = actual
        if profundidad[actual] > profundidad[mejor]:
            mejor = actual
        if estado in maquina["finales"]:
            aceptacion = actual
            break
        if profundidad[actual] >= MAX_PASOS:
            inconclusa = True
            continue
        lee = _lectura_cinta(tipo, cinta, cabeza)
        for siguiente, escribe, movimiento in maquina["tabla"].get((estado, lee), ()):
            nueva_cabeza = cabeza + {"L": -1, "R": 1, "S": 0}[movimiento]
            if tipo == "lba" and not 0 <= nueva_cabeza < len(cinta):
                continue
            if tipo == "lba":
                nueva_cinta = list(cinta)
                nueva_cinta[cabeza] = escribe
                nueva_cinta = tuple(nueva_cinta)
            else:
                temporal = dict(cinta)
                if escribe == BLANCO:
                    temporal.pop(cabeza, None)
                else:
                    temporal[cabeza] = escribe
                nueva_cinta = tuple(sorted(temporal.items()))
            nuevo = (siguiente, nueva_cabeza, nueva_cinta)
            if nuevo in padres:
                if tipo == "mt" and _configuracion_es_ancestro(padres, nuevo, actual):
                    inconclusa = True
                continue
            if len(padres) >= MAX_CONFIGURACIONES:
                inconclusa = True
                pendientes.clear()
                break
            accion = (f"δ({estado}, {lee}) → ({siguiente}, {escribe}, {movimiento}): "
                      f"lee {lee}, escribe {escribe} y mueve {movimiento}.")
            regla = (estado, lee, siguiente, escribe, movimiento)
            padres[nuevo] = (actual, lee, accion, regla)
            profundidad[nuevo] = profundidad[actual] + 1
            pendientes.append(nuevo)
    final = aceptacion if aceptacion is not None else mejor
    pasos = []
    for (estado, cabeza, cinta), leido, accion, regla in _ruta(padres, final):
        contenido = cinta if tipo == "lba" else dict(cinta)
        pasos.append({"cinta": contenido, "cabeza": cabeza, "estado": estado,
                      "simbolo": leido, "accion": accion, "regla": regla})
    if aceptacion is not None:
        aceptada, titulo = True, "Aceptada: se alcanzó un estado final."
    elif inconclusa:
        aceptada, titulo = None, "No evaluada: hubo un ciclo o se alcanzó el presupuesto de búsqueda."
    else:
        aceptada, titulo = False, "Rechazada: todas las rutas se detuvieron sin llegar a un estado final."
    contenido = final[2] if tipo == "lba" else dict(final[2])
    pasos.append({"cinta": contenido, "cabeza": final[1],
                  "estado": "aceptación" if aceptada else "límite" if aceptada is None else "rechazo",
                  "simbolo": "fin", "accion": titulo + f" Configuraciones exploradas: {len(padres)}.",
                  "regla": None})
    return {"aceptada": aceptada, "mensaje": titulo, "pasos": pasos,
            "limite": aceptada is None, "exploradas": len(padres),
            "alfabeto": "{" + ", ".join(maquina["alfabeto_cinta"]) + "}"}
