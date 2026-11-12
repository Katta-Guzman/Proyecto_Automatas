"""PDA determinista para X^nY^n, con X e Y configurables."""


def simular(cadena: str, simbolo_apilar: str = "a", simbolo_desapilar: str = "b") -> dict:
    """Apila por el primer bloque y desapila por el segundo, en orden LIFO."""
    simbolo_apilar = simbolo_apilar.strip()
    simbolo_desapilar = simbolo_desapilar.strip()
    if len(simbolo_apilar) != 1 or len(simbolo_desapilar) != 1:
        raise ValueError("Escribe un carácter por campo (a, b); usa n y Generar cadena para repetirlo.")
    if simbolo_apilar == simbolo_desapilar:
        raise ValueError("Los dos símbolos deben ser diferentes.")

    pila = ["⊥"]
    estado = "q₁"
    pasos = [{"pos": 0, "simbolo": "—", "pila": tuple(pila), "estado": estado,
              "accion": "Inicio: la pila contiene solo el marcador de base ⊥."}]
    if len(cadena) > 12 or cadena.count(simbolo_apilar) > 6:
        mensaje = "Máximo 12 símbolos y seis marcas apiladas para que la pila quepa en pantalla."
        pasos.append({"pos": 0, "simbolo": "—", "pila": tuple(pila), "estado": "límite", "accion": mensaje})
        return {"aceptada": None, "mensaje": mensaje + " No se evaluó la cadena.",
                "pasos": pasos, "limite": True}

    vio_segundo_bloque = False
    for posicion, simbolo in enumerate(cadena, start=1):
        if simbolo == simbolo_apilar and not vio_segundo_bloque:
            pila.append("A")
            estado = "q₁"
            accion = f"Lee '{simbolo}': apila una A para recordarlo."
        elif simbolo == simbolo_desapilar:
            vio_segundo_bloque = True
            estado = "q₂"
            if len(pila) == 1:
                accion = "No queda una A para emparejar este símbolo: rechazo."
                pasos.append({"pos": posicion, "simbolo": simbolo, "pila": tuple(pila),
                              "estado": "rechazo", "accion": accion})
                return {"aceptada": False, "mensaje": "Hay más símbolos del segundo tipo que del primero.", "pasos": pasos}
            pila.pop()
            accion = f"Lee '{simbolo}': desapila una A."
        elif simbolo == simbolo_apilar:
            accion = f"'{simbolo}' aparece después de empezar el segundo bloque: rechazo."
            pasos.append({"pos": posicion, "simbolo": simbolo, "pila": tuple(pila),
                          "estado": "rechazo", "accion": accion})
            return {"aceptada": False, "mensaje": "El bloque de símbolos para apilar debe ir primero.", "pasos": pasos}
        else:
            accion = f"'{simbolo}' no pertenece al alfabeto {{{simbolo_apilar}, {simbolo_desapilar}}}."
            pasos.append({"pos": posicion, "simbolo": simbolo, "pila": tuple(pila),
                          "estado": "rechazo", "accion": accion})
            return {"aceptada": False, "mensaje": accion, "pasos": pasos}

        pasos.append({"pos": posicion, "simbolo": simbolo, "pila": tuple(pila), "estado": estado, "accion": accion})

    aceptada = bool(cadena) and vio_segundo_bloque and len(pila) == 1
    if not cadena:
        mensaje = "Cadena vacía: este lenguaje requiere al menos un símbolo de cada tipo."
    elif not vio_segundo_bloque:
        mensaje = f"Falta el bloque de símbolos '{simbolo_desapilar}'."
    elif len(pila) > 1:
        mensaje = f"Quedaron {len(pila) - 1} A en la pila; faltan símbolos '{simbolo_desapilar}'."
    else:
        mensaje = "Aceptada: cada símbolo del primer bloque encontró pareja y la pila volvió a ⊥."
    pasos.append({"pos": len(cadena) + 1, "simbolo": "fin", "pila": tuple(pila),
                  "estado": "q_f" if aceptada else "rechazo", "accion": mensaje})
    return {"aceptada": aceptada, "mensaje": mensaje, "pasos": pasos}
