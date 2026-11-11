"""PDA determinista para L = {a^n b^n | n >= 1}."""


def simular(cadena: str) -> dict:
    pila = ["⊥"]
    estado = "q_a"
    pasos = [{"pos": 0, "simbolo": "—", "pila": tuple(pila), "estado": estado,
              "accion": "Pila inicializada con el marcador ⊥."}]
    vio_b = False
    if len(cadena) > 12 or cadena.count("a") > 6:
        mensaje = "Máximo 12 símbolos (hasta seis a y seis b) para mostrar la pila en pantalla."
        pasos.append({"pos": 0, "simbolo": "—", "pila": tuple(pila), "estado": "rechazo", "accion": mensaje})
        return {"aceptada": False, "mensaje": mensaje, "pasos": pasos}

    for posicion, simbolo in enumerate(cadena, start=1):
        accion = ""
        if simbolo == "a" and not vio_b:
            pila.append("A")
            estado = "q_a"
            accion = "Lee a: apila A."
        elif simbolo == "b":
            vio_b = True
            estado = "q_b"
            if len(pila) > 1:
                pila.pop()
                accion = "Lee b: desapila A."
            else:
                accion = "Lee b sin A disponible: rechazo."
                pasos.append({"pos": posicion, "simbolo": simbolo, "pila": tuple(pila), "estado": "rechazo",
                              "accion": accion})
                return {"aceptada": False, "mensaje": "Hay más b que a; la pila se quedó sin A.", "pasos": pasos}
        elif simbolo == "a":
            accion = "a después de comenzar los b: orden inválido."
            pasos.append({"pos": posicion, "simbolo": simbolo, "pila": tuple(pila), "estado": "rechazo",
                          "accion": accion})
            return {"aceptada": False, "mensaje": "Las a deben aparecer antes que las b.", "pasos": pasos}
        else:
            accion = f"Símbolo '{simbolo}' fuera del alfabeto {{a, b}}."
            pasos.append({"pos": posicion, "simbolo": simbolo, "pila": tuple(pila), "estado": "rechazo",
                          "accion": accion})
            return {"aceptada": False, "mensaje": accion, "pasos": pasos}

        pasos.append({"pos": posicion, "simbolo": simbolo, "pila": tuple(pila), "estado": estado, "accion": accion})

    aceptada = bool(cadena) and vio_b and len(pila) == 1
    if not cadena:
        mensaje = "Cadena vacía: este simulador requiere n ≥ 1."
    elif not vio_b:
        mensaje = "No se leyó ninguna b."
    elif len(pila) != 1:
        mensaje = f"Quedaron {len(pila) - 1} símbolo(s) A en la pila."
    else:
        mensaje = "Cadena aceptada: la pila volvió al marcador ⊥."
    pasos.append({"pos": len(cadena) + 1, "simbolo": "fin", "pila": tuple(pila),
                  "estado": "q_f" if aceptada else "rechazo", "accion": mensaje})
    return {"aceptada": aceptada, "mensaje": mensaje, "pasos": pasos}
