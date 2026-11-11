"""Simulador de un DFA configurable que reconoce cadenas terminadas en un símbolo."""


def simular(cadena: str, alfabeto: str = "a,b", simbolo_final: str = "a") -> dict:
    """Procesa una cadena y devuelve aceptación y una traza de transiciones.

    ``alfabeto`` es una lista de símbolos de un carácter separados por comas.
    El lenguaje es ``(alfabeto - {simbolo_final})* simbolo_final``.
    """
    simbolos = [s.strip() for s in alfabeto.split(",") if s.strip()]
    if not simbolos or any(len(s) != 1 for s in simbolos):
        raise ValueError("Escribe símbolos de un carácter separados por coma, por ejemplo: a,b")
    if len(set(simbolos)) != len(simbolos):
        raise ValueError("El alfabeto no debe contener símbolos repetidos.")
    if len(simbolo_final) != 1 or simbolo_final not in simbolos:
        raise ValueError("El símbolo final debe pertenecer al alfabeto y tener un carácter.")

    estado = "q0"
    pasos = [{"pos": 0, "simbolo": "—", "desde": "inicio", "estado": estado,
              "accion": "Estado inicial; q1 es el único estado de aceptación."}]
    if len(cadena) > 500:
        mensaje = "Máximo 500 símbolos para conservar una traza interactiva ágil."
        pasos.append({"pos": 0, "simbolo": "—", "desde": estado, "estado": "rechazo", "accion": mensaje})
        return {"aceptada": False, "mensaje": mensaje, "pasos": pasos}
    for posicion, simbolo in enumerate(cadena, start=1):
        if simbolo not in simbolos:
            mensaje = f"Símbolo '{simbolo}' fuera del alfabeto en la posición {posicion}."
            pasos.append({"pos": posicion, "simbolo": simbolo, "desde": estado, "estado": "rechazo",
                          "accion": mensaje})
            return {"aceptada": False, "mensaje": mensaje, "pasos": pasos}
        anterior = estado
        estado = "q1" if simbolo == simbolo_final else "q0"
        pasos.append({"pos": posicion, "simbolo": simbolo, "desde": anterior, "estado": estado,
                      "accion": f"δ({anterior}, {simbolo}) = {estado}"})

    aceptada = estado == "q1"
    return {"aceptada": aceptada, "mensaje": "Cadena aceptada." if aceptada else
            "Cadena rechazada: debe terminar con el símbolo configurado.", "pasos": pasos}
