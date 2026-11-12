# Implementación y conceptos aplicados

## Propósito

La aplicación ilustra cómo aumenta la capacidad de cómputo al pasar por los cuatro niveles de la jerarquía de Chomsky. En todos los módulos se recibe una cadena y se produce una traza ordenada de configuraciones que la interfaz muestra y permite recorrer.

## Organización del código

- `main.py` inicia la aplicación.
- `interfaz/menu.py` expone el punto de entrada del menú.
- `interfaz/pantalla_inicio.py` construye la portada, la navegación, la teoría, los ejercicios y las miniaturas de los cuatro modelos.
- `interfaz/simulador.py` contiene la interfaz común: entrada, ejemplos, controles de reproducción, tabla de pasos y dibujo de la máquina. Los cuatro niveles incluyen barra lateral, disposición adaptable y una guía de tres pasos; los niveles 3 y 0 incluyen editores propios para AFN y MT.
- `interfaz/parametrizacion_colores.py` concentra la paleta y asigna nombres claros a los colores de fondo, panel, campos, texto, bordes, selección y resultados.
- `modelos/formales.py` interpreta las reglas editables de AP, LBA y MT sin depender de Tkinter.
- `modelos/nivel3.py` simula AFN con transiciones ε y construye el AFD equivalente por subconjuntos.
- `modelos/nivel2.py` implementa el autómata de pila para dos símbolos configurables.
- `modelos/nivel1.py` implementa la LBA para tres símbolos configurables.
- `modelos/nivel0.py` implementa una máquina de Turing para palíndromos configurables o suma unaria.

Los modelos no dependen de Tkinter: cada función `simular` devuelve un diccionario con el resultado, un mensaje y una lista de pasos. La interfaz interpreta esa lista para mostrar la tabla y la configuración activa. Esta separación permite cambiar la presentación sin reescribir las transiciones de los modelos.

## Tema visual parametrizado

Los seis tonos de referencia se declaran una sola vez en `PALETA_BASE`, dentro de `interfaz/parametrizacion_colores.py`. Debajo de esa lista, cada constante documenta el uso visual del tono (por ejemplo, `FONDO_APP`, `CAMPO`, `TEXTO` y `ACENTO`). Para adaptar el tema basta con cambiar los valores de `PALETA_BASE`; el menú y los cuatro módulos consumen los nombres de rol, por lo que no hace falta buscar códigos hexadecimales por la interfaz.

La portada organiza el contenido en una barra lateral fija y un área principal desplazable. Un gráfico de AFN presenta una transición real; cada tarjeta incluye una miniatura diferente para el estado, la pila, la cinta acotada o la cinta extensible. Los paneles de teoría y ejercicios permiten abrir el módulo correspondiente; los ejercicios cargan la cadena de prueba para que se pueda seguir su recorrido.

## Modelos computacionales

### Nivel 3: AFN y construcción de subconjuntos

El alfabeto se configura con símbolos de un carácter separados por comas. La primera plantilla elige un símbolo final `f` y reconoce:

`L = Σ* f`

El AFN tiene dos estados: `q0` inicial y `q1` final. `q0` tiene un bucle sobre todo el alfabeto `Σ` y, al leer `f`, también puede avanzar a `q1`. Como `q1` no tiene transiciones de salida, solo acepta cuando esa rama se toma en el último símbolo de la entrada.

La segunda plantilla reproduce la bifurcación de la referencia: `q0` llega por ε a `r1` y `t1`. La rama `r` detecta dos apariciones consecutivas del segundo símbolo (`11` con `0,1`); la rama `t`, dos del primero (`00`). `r3` y `t3` son finales y conservan la aceptación mientras leen más símbolos. Por tanto, con `0,1` reconoce las cadenas que contienen `00` o `11`.

El tercer modo permite definir un AFN o AFN-ε propio mediante `Q`, `Σ`, `q₀`, `F` y reglas `origen,símbolo -> destinos`. El ejemplo inicial reconoce las cadenas que contienen `01`. `crear_desde_reglas` valida unicidad, pertenencia de estados y símbolos, y formato de cada transición. La ausencia de una regla significa que la función de transición devuelve `∅`; `ε` solo aparece como etiqueta de transición, no como símbolo de entrada. El diagrama completo se genera con todos los estados y reglas introducidos, incluyendo flecha inicial, bucles y estados finales; se distribuye en una elipse para facilitar la lectura. La misma definición alimenta la tabla AFD y la búsqueda de ejemplos de aceptación/rechazo más cortos. El límite de 8 estados, 6 símbolos y 256 subconjuntos protege la interfaz de un crecimiento exponencial de la construcción de subconjuntos.

En la pantalla, el estudiante sigue tres etapas: seleccionar una plantilla o el modo propio; ajustar el alfabeto y el símbolo final, o declarar `Q`, `q₀`, `F` y `δ`; escribir o cargar una cadena y leer la animación. Los números de las filas de traza empiezan en 1 para coincidir con el indicador `Paso n de m`. La barra lateral permite volver a **Simuladores** o abrir otro nivel. El sistema no deduce una máquina única de un enunciado informal: el usuario expresa la definición formal y la interfaz construye sus visualizaciones a partir de ella.

El motor realiza la conversión completa: parte de `clausuraε({q0})`; para cada subconjunto `S` y símbolo `a`, calcula `mover(S,a)` como la unión de los destinos y luego `clausuraε(mover(S,a))`. Explora los subconjuntos nuevos con una cola hasta que no queden pendientes. `∅` aparece si ninguna rama continúa. Un subconjunto del AFD es final si contiene al menos un estado final del AFN. La animación muestra cada lectura y el gráfico resalta los estados activos; la tabla presenta todas las transiciones alcanzables. La traza admite hasta 500 símbolos.

### Nivel 2: PDA para un lenguaje libre de contexto

El lenguaje es `L = {xⁿyⁿ | n ≥ 1}`, donde `x` y `y` son dos símbolos distintos configurables (pueden ser letras o dígitos). El marcador `⊥` representa la base de la pila. En el estado que procesa `x`, cada símbolo `x` agrega una `A`. Al leer la primera `y`, la máquina cambia al estado de consumo y retira una `A` por cada `y`. Rechaza si se agota la pila antes de tiempo, si queda alguna `A` al terminar, si la entrada está vacía o si aparece una `x` después de una `y`.

La pila usa disciplina LIFO (último en entrar, primero en salir); en este lenguaje las marcas son iguales, por lo que la información útil es su cantidad.

La interfaz admite hasta 12 símbolos y seis marcas apiladas para conservar la pila dentro del área visible.
El control `n` genera `xⁿyⁿ` con `1 ≤ n ≤ 6`; los campos de símbolos siguen recibiendo un solo carácter.

La pantalla presenta el uso como una secuencia: elegir el AP guiado o el editable; configurar los dos símbolos y `n`; introducir la palabra y seguir la pila en la traza. `n` es un contador para generar la palabra, no un símbolo de entrada. Por ejemplo, con `x=a`, `y=b`, `n=2`, la palabra es `aabb` y la pila evoluciona `⊥ → ⊥A → ⊥AA → ⊥A → ⊥`. El sidebar permite abrir otros niveles y, en una ventana estrecha, el diagrama y la tabla se apilan verticalmente.

El modo **Definir mi AP** ejecuta un autómata de pila no determinista especificado por el usuario. Cada regla tiene la forma `estado,entrada,tope -> siguiente,reemplazo`; `ε` en entrada no consume símbolo y `ε` en reemplazo retira el tope. La cadena de reemplazo se escribe desde la base hacia el nuevo tope. El marcador de fondo se conserva. La búsqueda por anchura encuentra una ruta aceptante si existe; sin ruta aceptante, un espacio de configuraciones finito permite rechazar exhaustivamente. El tope de búsqueda (5.000 configuraciones, 64 símbolos de pila por configuración y 1.000 transiciones por ruta) produce un resultado inconcluso, nunca rechazo.

### Nivel 1: LBA para un lenguaje sensible al contexto

El lenguaje es `L = {xⁿyⁿzⁿ | n ≥ 1}`, donde `x`, `y` y `z` son tres símbolos distintos configurables. La máquina crea una cinta con un delimitador fijo a cada lado: `⊢ entrada ⊣`. Primero verifica el orden de los bloques `x+ y+ z+`. Después, en cada ronda:

1. Busca una `x` sin marcar y la reemplaza por `X`.
2. Avanza para buscar una `y` sin marcar y la reemplaza por `Y`.
3. Avanza para buscar una `z` sin marcar y la reemplaza por `Z`.
4. Regresa hacia el comienzo y repite.

Si no hay `x` sin marcar, comprueba que tampoco queden `y` o `z` sin marcar. Acepta solo si las cantidades coinciden. Si falta una marca requerida, rechaza. El cabezal no cruza los delimitadores ni se agregan celdas, por lo que el espacio utilizado está acotado linealmente por la entrada. La interfaz limita la longitud a 16 símbolos para que la traza detallada sea manejable.
El control `n` genera `xⁿyⁿzⁿ` con `1 ≤ n ≤ 5` y respeta el límite de cinta.

La opción adicional reconoce `{x yⁿ z²ⁿ | n ≥ 1}`. Solo aparece una `x`; por cada `y` la máquina marca **dos** `z`. Rechaza si falta una de las dos `z` o si quedan `z` al agotar las `y`. Con `x=a`, `y=b`, `z=c`, `n=2` genera `abbcccc`. Esta opción también es libre de contexto, pero el módulo mantiene como ejemplo principal `xⁿyⁿzⁿ`, que requiere capacidad sensible al contexto.

El modo **Definir mi LBA** usa reglas `estado,lee -> siguiente,escribe,mueve` y una cinta con extremos fijos `⊢` y `⊣`. `L` mueve a la izquierda, `R` a la derecha y `S` mantiene la cabeza en la celda actual. El editor impide borrar o cruzar delimitadores y crear fronteras nuevas. La máquina puede ser no determinista (varias reglas para una misma combinación). La búsqueda por anchura acepta si alguna ruta alcanza un estado final. Como hay un número finito de configuraciones para cada entrada, la exploración exhaustiva terminaría en principio; el límite de 5.000 configuraciones o 1.000 transiciones por ruta devuelve **no evaluada** en lugar de simular un rechazo.

La pantalla de este nivel mantiene el sidebar de **Simuladores** y presenta tres pasos. En los patrones guiados, `n` genera la entrada y no es un símbolo adicional. El modo `xⁿyⁿzⁿ` acepta `aabbcc` para `n=2`; en cada ronda marca una letra de cada bloque como `X`, `Y` y `Z`. El modo `x·yⁿ·z²ⁿ` acepta `abbcccc`, con una `a`, dos `b` y cuatro `c`; esta segunda práctica también es libre de contexto. Las sugerencias de aceptación y rechazo dependen del patrón y de los símbolos configurados. El modo formal de muestra acepta `ab`; al editar sus reglas se ocultan las sugerencias fijas.

### Nivel 0: Máquina de Turing

La cinta es un diccionario de posiciones enteras. Una posición sin valor almacena el blanco `□`; el cabezal puede moverse a posiciones negativas o más allá del extremo derecho de la entrada. Cada paso guarda una copia de la cinta, el estado, el símbolo leído y la acción para que el usuario pueda inspeccionar la lectura, escritura y movimiento.

La pantalla del Nivel 0 contiene una guía de tres pasos que cambia según la opción seleccionada. El selector ofrece **Palíndromo**, **Suma unaria** y **Definir mi MT**; la cadena se puede escribir directamente o cargar desde los ejemplos opcionales. Tras simular, la reproducción permite avanzar y retroceder por la traza completa. La cinta dibujada centra la ventana en el cabezal, resalta la celda activa y las marcas `X`/`Y`, y muestra el estado y el alfabeto de cinta.

El modo **palíndromo** permite configurar dos símbolos distintos de un carácter. Marca con `X` y `Y` los dos símbolos ya comparados. En cada ciclo marca el símbolo sin procesar más a la izquierda, busca el extremo derecho y compara el último símbolo sin marcar. Rechaza ante una diferencia y acepta cuando no quedan parejas. La entrada vacía se acepta como palíndromo. `X`, `Y` y `□` están reservados para las marcas y el blanco. La guía explica la comparación y actualiza ejemplos como `010`/`01` o `aba`/`ab` según el alfabeto configurado.

El modo **suma unaria** recibe dos bloques positivos con formato `1ⁿ+1ᵐ`, con `n,m ≥ 1` (sin espacios; por ejemplo, `111+11`). Aquí `n` es una cantidad de repeticiones: `111` representa tres, no el número decimal 111. La interfaz ofrece controles `n` y `m` para generar la entrada, que sigue editable, o permite escribirla directamente. La máquina recorre hasta el blanco final, borra el último `1` del segundo sumando y reemplaza `+` por `1`. El resultado es un solo bloque de unos cuya longitud es la suma. La traza muestra la operación; la entrada se limita a 28 caracteres.

El modo **Definir mi MT** permite editar estados, alfabetos, estado inicial, estados finales y reglas. Cada transición usa el formato `estado,lee -> siguiente,escribe,mueve`; `L`, `R` y `S` indican izquierda, derecha y quieto. `□` representa una celda vacía del alfabeto de cinta y no puede ser un símbolo de entrada. La interfaz explica los campos antes de abrir el editor.

La MT ejecuta transiciones de forma no determinista. Se exploran las configuraciones por anchura; una ruta que llega a un estado final acepta. Si las rutas se agotan sin aceptación y sin ciclos, se rechaza; si se repite una configuración o se alcanza el presupuesto (5.000 configuraciones o 1.000 transiciones por ruta), el resultado es inconcluso. Un límite de simulación no demuestra que la máquina real rechace ni que vaya a terminar. Las sugerencias con aceptación/rechazo fijo se ocultan al modificar las reglas, para no presentar como válidos resultados de una máquina distinta.

## Interfaz y flujo de uso

1. `main.py` abre la pantalla principal.
2. La persona selecciona uno de los cuatro niveles.
3. El módulo explica qué significa una cadena y deja escribir una sin elegir un ejemplo.
4. Una franja superior muestra un ejemplo rápido adaptado a los símbolos configurados; el Nivel 0 además explica la tarea en una guía de tres pasos.
5. Elegir un ejemplo solo lo carga en la entrada al pulsar **Cargar ejemplo**.
6. Al pulsar **Simular cadena**, el modelo produce la traza completa.
7. La reproducción comienza automáticamente. **Detener**, la velocidad, **Anterior**, **Siguiente**, **Reproducir** o una fila actualizan la configuración visible.
8. El dibujo resalta los estados del AFN/AFD, el tope de la pila o la posición del cabezal y permite ver las marcas. En los niveles de pila y cinta, una ruta de control resume la fase activa; la traza contiene los estados y movimientos concretos. **Ampliar diagrama** abre una vista grande sincronizada con la traza.

Se usa Tkinter, incluido normalmente con Python, para mantener la instalación sencilla y multiplataforma. No hay llamadas de red ni dependencias de terceros.

## Alcance y simplificaciones

- Cada nivel permite definir una máquina finita por sus transiciones; las plantillas guiadas siguen siendo ejemplos listos para ejecutar. La app no recibe gramáticas arbitrarias ni traduce automáticamente cualquier descripción de lenguaje a una máquina.
- Las dos plantillas regulares reconocen, respectivamente, cadenas que terminan en un símbolo y cadenas que contienen un par igual consecutivo; el editor de AFN-ε permite otros lenguajes regulares.
- La construcción de subconjuntos funciona para cualquier AFN finito expresado mediante la estructura de transiciones de `nivel3.py`; la interfaz ofrece dos plantillas pedagógicas.
- El PDA y la LBA permiten cambiar los símbolos de entrada; la suma de Turing continúa usando números unarios.
- Los simuladores limitan entradas, reglas y configuraciones para que la memoria y las trazas se puedan explorar en la interfaz. Si una búsqueda se corta, devuelve **no evaluada**, sin afirmar aceptación ni rechazo.
- La LBA valida un lenguaje sensible al contexto concreto y limita entradas a 16 símbolos por legibilidad de la traza.
- El modo de suma opera con números positivos escritos en unario.
- Los límites de entrada evitan trazas excesivamente grandes y mantienen la interfaz interactiva.

## Verificación y criterio académico en Colombia

Las reglas matemáticas de los autómatas no cambian según el país. Para la sustentación conviene declarar el alfabeto, los estados, la transición, el estado inicial, los finales y el criterio de aceptación; después mostrar una traza que corresponda a esas reglas. El material de [Lenguajes y Máquinas de la Universidad de los Andes](https://cursos.virtual.uniandes.edu.co/isis1106/wp-content/uploads/sites/81/2019/08/capitulo1.pdf) relaciona lenguajes regulares con autómatas finitos, libres de contexto con autómatas de pila, sensibles al contexto con máquinas linealmente restringidas e irrestrictos con máquinas de Turing. El [programa de Lenguajes Formales de la UPTC](https://www.uptc.edu.co/sitio/export/sites/default/portal/sitios/universidad/vic_aca/facultades/fac_sog/preg/ing_54673_s/.content/docs/plan_estud/Sem7-lengform.pdf) incluye precisamente alfabetos, cadenas, AFN/AFD, conversión, autómatas de pila y máquinas de Turing. Un [trabajo de la Universidad Tecnológica de Pereira](https://ojs2.utp.edu.co/index.php/revistaciencia/article/view/2573) describe un simulador como herramienta para visualizar el reconocimiento de palabras de un lenguaje.

La aplicación distingue tres resultados: **aceptada** (alguna ejecución alcanza el criterio final), **rechazada** (la cadena no pertenece al alfabeto o se agotaron todas las rutas sin aceptación) y **no evaluada** (un presupuesto se agotó o una MT entró en ciclo). Las pruebas en `tests/test_modelos.py` comparan los resultados con definiciones independientes de los lenguajes sobre conjuntos exhaustivos de cadenas cortas; además inspeccionan invariantes de pila, cinta y configuración. Se ejecutan con `py -m unittest discover -s tests -v`, también en GitHub Actions con Python 3.9 y 3.12.

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

## Fuentes para las reglas

- [Cornell: implementación de analizadores léxicos](https://courses.cs.cornell.edu/cs4120/2023sp/notes/leximpl/index.html): clausura ε y construcción de subconjuntos.
- [MIT OpenCourseWare: autómatas de pila](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/a22fce6f6824c53dbb79a0da786966a6_MIT18_404f20_lec4.pdf): apilar al leer el primer bloque y desapilar al leer el segundo.
- [MIT OpenCourseWare: autómatas linealmente acotados](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/a48f01c5374e72ee4f68a70bc0e38583_MIT18_404f20_lec10.pdf): el cabezal se mantiene en la porción de entrada.
- [MIT OpenCourseWare: máquinas de Turing](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/12409362e93748137502be876e72f9b3_IycOPFmEQk8.pdf): lectura, escritura, movimiento bidireccional y detención.
- [Cornell: indecidibilidad del problema de parada](https://www.cs.cornell.edu/courses/cs212/2000sp/notes/lectures/l28-computability.htm): no hay un algoritmo general que determine siempre si cualquier programa termina.
