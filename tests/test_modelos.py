"""Pruebas de lenguajes y de las configuraciones que muestra la interfaz.

Usan solo unittest para que el proyecto siga sin dependencias adicionales.
"""

import itertools
import unittest

from modelos import formales, nivel0, nivel1, nivel2, nivel3


def cadenas(alfabeto, longitud_maxima):
    for longitud in range(longitud_maxima + 1):
        for simbolos in itertools.product(alfabeto, repeat=longitud):
            yield "".join(simbolos)


class LenguajesTest(unittest.TestCase):
    def test_afn_termina_en_simbolo_y_afd_coinciden(self):
        for cadena in cadenas("ab1", 5):
            resultado = nivel3.simular(cadena, "a,b,1", "1")
            self.assertEqual(resultado["aceptada"], cadena.endswith("1"), cadena)
            estado = resultado["afd"]["inicial"]
            for simbolo in cadena:
                estado = resultado["afd"]["tabla"][(estado, simbolo)]
            self.assertEqual(estado in resultado["afd"]["finales"], resultado["aceptada"], cadena)

    def test_afn_con_epsilon_y_dos_ramas(self):
        for cadena in cadenas("01", 7):
            resultado = nivel3.simular(cadena, "0,1", plantilla="pares")
            self.assertEqual(resultado["aceptada"], "00" in cadena or "11" in cadena, cadena)

    def test_afn_definido_por_reglas(self):
        maquina = nivel3.crear_desde_reglas(
            "q0,q1,q2", "0,1", "q0", "q2",
            "q0,ε -> q1\nq1,0 -> q1\nq1,1 -> q1,q2")
        self.assertEqual(nivel3.clausura_epsilon(maquina, {"q0"}), {"q0", "q1"})
        for cadena in cadenas("01", 6):
            resultado = nivel3.simular(cadena, maquina=maquina)
            self.assertEqual(resultado["aceptada"], cadena.endswith("1"), cadena)
        with self.assertRaisesRegex(ValueError, "Línea 1"):
            nivel3.crear_desde_reglas("q0", "a", "q0", "q0", "q0,b -> q0")

    def test_pila_xnyn_y_traza_lifo(self):
        for cadena in cadenas("ab", 6):
            resultado = nivel2.simular(cadena)
            esperado = any(cadena == "a" * n + "b" * n for n in range(1, 4))
            self.assertEqual(resultado["aceptada"], esperado, cadena)
            self.assertTrue(all(paso["pila"][0] == "⊥" for paso in resultado["pasos"]))
        self.assertTrue(nivel2.simular("1122", "1", "2")["aceptada"])

    def test_lba_tres_bloques_y_cinta_acotada(self):
        for cadena in cadenas("abc", 6):
            resultado = nivel1.simular(cadena)
            esperado = any(cadena == "a" * n + "b" * n + "c" * n for n in range(1, 3))
            self.assertEqual(resultado["aceptada"], esperado, cadena)
            for paso in resultado["pasos"]:
                self.assertEqual(paso["cinta"][0], "⊢")
                self.assertEqual(paso["cinta"][-1], "⊣")
                self.assertEqual(len(paso["cinta"]), len(cadena) + 2)
                self.assertTrue(1 <= paso["cabeza"] <= len(cadena) + 1)
        self.assertTrue(nivel1.simular("112233", "1", "2", "3")["aceptada"])

    def test_lba_patron_doble(self):
        for cadena in cadenas("abc", 6):
            esperado = any(cadena == "a" + "b" * n + "c" * (2 * n) for n in range(1, 3))
            self.assertEqual(nivel1.simular(cadena, patron="doble")["aceptada"], esperado, cadena)
        self.assertTrue(nivel1.simular("abbcccc", patron="doble")["aceptada"])

    def test_turing_palindromo_y_suma(self):
        for cadena in cadenas("01", 7):
            resultado = nivel0.simular(cadena)
            self.assertEqual(resultado["aceptada"], cadena == cadena[::-1], cadena)
            for paso in resultado["pasos"]:
                self.assertEqual(paso["simbolo"], paso["cinta"].get(paso["cabeza"], "□"))
        for a in range(1, 5):
            for b in range(1, 5):
                entrada = "1" * a + "+" + "1" * b
                self.assertEqual(nivel0.simular(entrada, modo="suma")["salida"], "1" * (a + b))

    def test_limite_no_es_rechazo(self):
        resultados = (nivel3.simular("a" * 501), nivel2.simular("a" * 13),
                      nivel1.simular("a" * 17), nivel1.simular("a" * 17, patron="doble"),
                      nivel0.simular("0" * 25), nivel0.simular("1" * 29, modo="suma"))
        for resultado in resultados:
            self.assertIsNone(resultado["aceptada"])
            self.assertTrue(resultado["limite"])

    def test_ap_definido_por_transiciones(self):
        maquina = formales.crear_ap(
            "q0,q1,qf", "a,b", "⊥,A", "q0", "qf", "⊥",
            "q0,a,⊥ -> q0,⊥A\nq0,a,A -> q0,AA\n"
            "q0,b,A -> q1,ε\nq1,b,A -> q1,ε\nq1,ε,⊥ -> qf,⊥")
        for cadena in cadenas("ab", 6):
            esperado = any(cadena == "a" * n + "b" * n for n in range(1, 4))
            resultado = formales.simular_ap(cadena, maquina)
            self.assertEqual(resultado["aceptada"], esperado, cadena)
            self.assertTrue(all(paso["pila"][0] == "⊥" for paso in resultado["pasos"]))
        self.assertFalse(formales.simular_ap("x", maquina)["aceptada"])

    def test_lba_definida_por_transiciones(self):
        maquina = formales.crear_cinta(
            "lba", "q0,q1,q2,qf", "a,b", "a,b,⊢,⊣", "q0", "qf",
            "q0,a -> q1,a,R\nq1,b -> q2,b,R\nq2,⊣ -> qf,⊣,S")
        for cadena in cadenas("ab", 4):
            resultado = formales.simular_cinta(cadena, maquina)
            self.assertEqual(resultado["aceptada"], cadena == "ab", cadena)
            for paso in resultado["pasos"]:
                self.assertEqual(paso["cinta"][0], "⊢")
                self.assertEqual(paso["cinta"][-1], "⊣")
                self.assertTrue(0 <= paso["cabeza"] < len(paso["cinta"]))
        self.assertFalse(formales.simular_cinta("x", maquina)["aceptada"])

    def test_mt_definida_por_transiciones_y_ciclo(self):
        maquina = formales.crear_cinta("mt", "q0,qf", "1", "1,□", "q0", "qf",
                                       "q0,1 -> qf,1,S")
        self.assertTrue(formales.simular_cinta("1", maquina)["aceptada"])
        self.assertFalse(formales.simular_cinta("", maquina)["aceptada"])
        bucle = formales.crear_cinta("mt", "q0,qf", "1", "1,□", "q0", "qf",
                                     "q0,□ -> q0,□,S")
        resultado = formales.simular_cinta("", bucle)
        self.assertIsNone(resultado["aceptada"])
        self.assertTrue(resultado["limite"])
        convergente = formales.crear_cinta(
            "mt", "q0,q1,q2,q3,qf", "1", "1,□", "q0", "qf",
            "q0,□ -> q1,□,S\nq0,□ -> q2,□,S\n"
            "q1,□ -> q3,□,S\nq2,□ -> q3,□,S")
        resultado = formales.simular_cinta("", convergente)
        self.assertFalse(resultado["aceptada"])
        oversized_ap = formales.crear_ap("q0", "a", "⊥", "q0", "", "⊥", "")
        oversized_lba = formales.crear_cinta(
            "lba", "q0", "a", "a,⊢,⊣", "q0", "", "")
        oversized_tm = formales.crear_cinta(
            "mt", "q0", "a", "a,□", "q0", "", "")
        for resultado in (formales.simular_ap("a" * 501, oversized_ap),
                          formales.simular_cinta("a" * 501, oversized_lba),
                          formales.simular_cinta("a" * 501, oversized_tm)):
            self.assertIsNone(resultado["aceptada"])
            self.assertTrue(resultado["limite"])


if __name__ == "__main__":
    unittest.main()
