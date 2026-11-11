# Implementación y conceptos aplicados

## Propósito

La aplicación ilustra cómo aumenta la capacidad de cómputo al pasar por los cuatro niveles de la jerarquía de Chomsky. En todos los módulos se recibe una cadena y se produce una traza ordenada de configuraciones que la interfaz muestra y permite recorrer.

## Organización del código

- `main.py` inicia la aplicación.
- `interfaz/menu.py` construye la pantalla inicial y abre el módulo seleccionado.
- `interfaz/simulador.py` contiene la interfaz común: entrada, ejemplos, controles de reproducción, tabla de pasos y dibujo de la máquina.
- `modelos/nivel3.py` implementa el DFA configurable.
- `modelos/nivel2.py` implementa el autómata de pila para `aⁿbⁿ`.
- `modelos/nivel1.py` implementa la LBA para `aⁿbⁿcⁿ`.
- `modelos/nivel0.py` implementa dos máquinas de Turing pequeñas.

Los modelos no dependen de Tkinter: cada función `simular` devuelve un diccionario con el resultado, un mensaje y una lista de pasos. La interfaz interpreta esa lista para mostrar la tabla y la configuración activa. Esta separación permite cambiar la presentación sin reescribir las transiciones de los modelos.

## Modelos computacionales

### Nivel 3: DFA para un lenguaje regular

El alfabeto es configurable mediante símbolos de un carácter separados por comas. También se elige un símbolo final `f`. El lenguaje reconocido es:

`L = (Σ − {f})* f`

La traza admite hasta 500 símbolos por entrada para mantener manejable la tabla de pasos.

El autómata tiene dos estados: `q0` (inicial, no aceptación) y `q1` (aceptación). Al leer `f` pasa a `q1`; al leer cualquier otro símbolo del alfabeto pasa a `q0`. Así, el estado final depende únicamente del último símbolo. Una entrada vacía termina en `q0` y se rechaza.

### Nivel 2: PDA para un lenguaje libre de contexto

El lenguaje es `L = {aⁿbⁿ | n ≥ 1}`. El marcador `⊥` representa la base de la pila. En el estado que procesa `a`, cada letra `a` agrega una `A`. Al leer la primera `b`, la máquina cambia al estado de consumo y retira una `A` por cada `b`. Rechaza si se agota la pila antes de tiempo, si queda alguna `A` al terminar, si la entrada está vacía o si aparece una `a` después de una `b`.

La pila usa disciplina LIFO (último en entrar, primero en salir); en este lenguaje las marcas son iguales, por lo que la información útil es su cantidad.

La interfaz admite hasta 12 símbolos y seis `a` para conservar todas las marcas de pila dentro del área visible.

### Nivel 1: LBA para un lenguaje sensible al contexto

El lenguaje es `L = {aⁿbⁿcⁿ | n ≥ 1}`. La máquina crea una cinta con un delimitador fijo a cada lado: `⊢ entrada ⊣`. Primero verifica el orden de los bloques `a+ b+ c+`. Después, en cada ronda:

1. Busca una `a` sin marcar y la reemplaza por `X`.
2. Avanza para buscar una `b` sin marcar y la reemplaza por `Y`.
3. Avanza para buscar una `c` sin marcar y la reemplaza por `Z`.
4. Regresa hacia el comienzo y repite.

Si no hay `a` sin marcar, comprueba que tampoco queden `b` o `c` sin marcar. Acepta solo si las cantidades coinciden. Si falta una marca requerida, rechaza. El cabezal no cruza los delimitadores ni se agregan celdas, por lo que el espacio utilizado está acotado linealmente por la entrada. La interfaz limita la longitud a 16 símbolos para que la traza detallada sea manejable.

### Nivel 0: Máquina de Turing

La cinta es un diccionario de posiciones enteras. Una posición sin valor almacena el blanco `□`; el cabezal puede moverse a posiciones negativas o más allá del extremo derecho de la entrada. Cada paso guarda una copia de la cinta, el estado, el símbolo leído y la acción para que el usuario pueda inspeccionar la lectura, escritura y movimiento.

El modo **palíndromo binario** marca con `X` los ceros ya comparados y con `Y` los unos. En cada ciclo marca el símbolo sin procesar más a la izquierda, busca el extremo derecho y compara el último símbolo sin marcar. Rechaza ante una diferencia y acepta cuando no quedan parejas. La entrada vacía se acepta como palíndromo.

El modo **suma unaria** recibe dos bloques positivos con formato `1ⁿ+1ᵐ`, con `n,m ≥ 1` (sin espacios; por ejemplo, `111+11`). La máquina recorre hasta el blanco final, borra el último `1` del segundo sumando y reemplaza `+` por `1`. El resultado es un solo bloque de unos cuya longitud es la suma. La entrada de este modo se limita a 28 caracteres.

## Interfaz y flujo de uso

1. `main.py` abre la pantalla principal.
2. La persona selecciona uno de los cuatro niveles.
3. El módulo muestra su lenguaje, controles y ejemplos incluidos.
4. Al pulsar **Simular**, el modelo produce la traza completa.
5. **Anterior**, **Siguiente**, **Reproducir** o la selección de una fila actualizan el estado visible de la máquina.
6. El dibujo resalta el estado activo, el tope de la pila o la posición del cabezal y permite ver las marcas escritas.

Se usa Tkinter, incluido normalmente con Python, para mantener la instalación sencilla y multiplataforma. No hay llamadas de red ni dependencias de terceros.

## Alcance y simplificaciones

- Los lenguajes implementados son ejemplos didácticos de cada familia; no son intérpretes de gramáticas arbitrarias.
- El DFA deja configurar alfabeto y símbolo final, pero su regla sigue siendo “termina en ese símbolo”.
- Los simuladores limitan las entradas para que la cinta, la pila y las trazas se puedan explorar en la interfaz.
- La LBA valida un lenguaje sensible al contexto concreto y limita entradas a 16 símbolos por legibilidad de la traza.
- El modo de suma opera con números positivos escritos en unario.
- Los límites de entrada evitan trazas excesivamente grandes y mantienen la interfaz interactiva.

## Guion breve para la sustentación

**Presentación (30–45 segundos):**

> Chomsky Lab es una aplicación de escritorio en Python que muestra la jerarquía de Chomsky mediante cuatro simuladores. En cada módulo se introduce una cadena y se puede avanzar paso a paso para observar el estado y la memoria disponible para la máquina. Se eligieron lenguajes concretos para que la diferencia entre memoria finita, pila, cinta acotada y cinta extendible sea visible.

**Demostración recomendada:**

1. Nivel 3: comparar `ba` (acepta) con `b` (rechaza) y cambiar el símbolo final a `b`.
2. Nivel 2: simular `aabb` y observar cómo la pila vuelve a `⊥`; luego probar `aab`.
3. Nivel 1: simular `aabbcc` y observar marcas `X`, `Y`, `Z` y movimientos de ida y regreso; luego probar `aabcc`.
4. Nivel 0: mostrar `010` frente a `0101`, o ejecutar `111+11` y leer el resultado `11111`.

**Preguntas que puede explicar el equipo:**

- ¿Por qué el nivel 2 necesita pila? Porque debe recordar cuántas `a` aparecieron antes de consumir las `b`; una cantidad fija de estados no basta para cualquier `n`.
- ¿Qué significa linealmente acotado? Que la máquina solo utiliza una cantidad de cinta proporcional a la longitud de la entrada; aquí los delimitadores fijan esa región.
- ¿Qué representa una configuración? El estado de control, el contenido de la memoria (pila o cinta) y la posición del cabezal cuando aplica.
- ¿Cómo se separan interfaz y lógica? Los módulos `modelos` devuelven pasos y resultado; `interfaz` los representa sin calcular las reglas del lenguaje.
