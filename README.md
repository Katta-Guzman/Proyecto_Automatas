# Chomsky Lab — Simulador de la jerarquía de Chomsky

Aplicación educativa de escritorio para explorar los modelos computacionales de los cuatro niveles de la jerarquía de Chomsky. La interfaz permite ejecutar una entrada, recorrer cada paso y observar el estado, la pila o la cinta de la máquina.

## Requisitos

- Python 3.9 o posterior.
- Tkinter, que viene incluido en la mayoría de las instalaciones de Python.
- No se requieren paquetes de terceros.

En algunas distribuciones Linux Tkinter se instala por separado (por ejemplo, el paquete `python3-tk`).

## Instalación y ejecución

Clona o descarga el repositorio. Abre una terminal en la carpeta `Proyecto_Automatas` y ejecuta:

```powershell
py main.py
```

En macOS o Linux también puedes usar:

```bash
python3 main.py
```

Desde la pantalla inicial, selecciona uno de los cuatro niveles. Arriba aparece un ejemplo rápido. El campo **Cadena de entrada** permite escribir la tuya; no es obligatorio elegir un ejemplo. La lista de ejemplos solo cambia la entrada cuando pulsas **Cargar ejemplo**. Pulsa **Simular cadena**: la vista baja al gráfico y la animación recorre toda la traza. Puedes detenerla, elegir velocidad **Lenta**, **Normal** o **Rápida**, usar **Anterior** y **Siguiente**, volver a **Reproducir** o seleccionar una fila. Pulsa **Ampliar diagrama** para ver la máquina grande en una ventana que sigue el paso actual. La barra derecha desplaza toda la pantalla del módulo. **Vaciar** deja la entrada en blanco para probar la cadena vacía.

Una cadena puede usar letras, números u otros caracteres si pertenecen al alfabeto elegido en ese módulo. Por ejemplo, el nivel 3 admite el alfabeto `a,b,1`; los niveles 2 y 1 permiten cambiar sus símbolos; el modo de palíndromo del nivel 0 permite elegir dos símbolos.

## Personalizar los colores

La paleta completa está centralizada en [`interfaz/parametrizacion_colores.py`](interfaz/parametrizacion_colores.py). Allí puedes cambiar los seis valores de `PALETA_BASE`; los nombres de rol (`FONDO_APP`, `PANEL`, `CAMPO`, `TEXTO`, `BORDE`, `ACENTO` y `ESTADO_OK`) explican dónde se usa cada tono. El menú, los campos, los diagramas y las animaciones usan esos roles para mantener el mismo tema.

## Módulos y ejemplos

### Nivel 3 — AFN y conversión a AFD

La pantalla mantiene la navegación lateral visible y organiza el trabajo en tres pasos: escoger una plantilla o el modo propio, revisar la definición y probar la cadena. El texto de ayuda explica el objetivo y propone ejemplos de aceptación y rechazo. Escribe una cadena directamente o elige una sugerencia; la lista no modifica la entrada hasta pulsar **Cargar ejemplo**. Después de simular, la tabla y el diagrama recorren los mismos pasos; **Anterior**, **Siguiente** y **Reproducir** permiten estudiar la ejecución.

El selector **Tipo de AFN** ofrece tres opciones:

1. **Termina en símbolo**: reconoce `Σ* f`, donde `f` es el símbolo final. Puedes cambiar el alfabeto (símbolos de un carácter separados por comas) y `f`. La pantalla dibuja el AFN y su AFD. Por defecto usa `a,b` y `f=a`; puedes probar `a,b,1`.
2. **Contiene dos iguales seguidos**: usa dos ramas con transiciones `ε`, como el diagrama de referencia. Con `0,1` acepta cualquier cadena que contenga `00` o `11` en alguna posición. Los dos símbolos también se pueden cambiar.
3. **Definir mi AFN-ε**: pulsa **Abrir editor de estados y transiciones** y declara `Q`, `Σ`, estado inicial `q₀`, finales `F` y `δ`. Escribe una transición por línea con el formato `origen,símbolo -> destino1,destino2`. Un ejemplo inicial reconoce cadenas que contienen `01`: `q0,0 -> q0,q1`, `q0,1 -> q0`, `q1,1 -> q2`, `q2,0 -> q2`, `q2,1 -> q2`. En `q0,0 -> q0,q1`, la máquina puede seguir en `q0` o abrir otra ruta hacia `q1`. `q0,ε -> q1` cambia de estado sin consumir símbolo. Las transiciones ausentes llevan al conjunto vacío. Al aplicar, se validan las referencias y se genera el grafo completo —estados, flechas, bucles, estado inicial y finales— desde tus reglas, además del AFD por subconjuntos alcanzables. El editor admite hasta 8 estados, 6 símbolos y 256 subconjuntos del AFD para que la vista siga siendo manejable.

El AFN, sus estados activos, ejemplos de aceptación/rechazo y la tabla de subconjuntos alcanzables del AFD se calculan desde las reglas actuales, no desde una lista fija de respuestas. El editor trabaja con una definición formal: el sistema no deduce una máquina única de un enunciado escrito en lenguaje natural. Desplaza el gráfico para recorrerlo o pulsa **Ampliar diagrama** para abrirlo en una ventana grande.

La traza se limita a entradas de 500 símbolos. Si se supera un límite de visualización, la aplicación indica **no evaluada**, que es distinto de una cadena rechazada por el autómata.

| Entrada | Resultado esperado |
| --- | --- |
| `a` | Aceptada |
| `ba` | Aceptada |
| `baba` | Aceptada |
| `b` | Rechazada |
| `abb` | Rechazada |
| `ε` (entrada vacía) | Rechazada |

En la segunda plantilla, `0110` y `1001` se aceptan; `0101`, `0` y la cadena vacía se rechazan.

### Nivel 2 — Autómata de pila

La pantalla conserva el sidebar y explica el módulo en tres pasos: elegir el modo, configurar símbolos y `n`, y seguir la pila durante la simulación. En el modo guiado reconoce cadenas con la forma `XⁿYⁿ`, para `n ≥ 1`. Puedes cambiar `X` y `Y` por letras o números distintos. Por cada símbolo del primer bloque apila `A`; por cada símbolo del segundo bloque desapila una `A`. La pila empieza con `⊥`.

Los campos **Símbolo x · apila una A** y **Símbolo y · retira una A** reciben un carácter cada uno. `n` cuenta las repeticiones y no se escribe dentro de la cadena: con `a`, `b` y `n = 3`, pulsa **Generar cadena** para obtener `aaabbb`. También puedes escribir la cadena a mano o cargar un ejemplo opcional. `aabb` se acepta; `aab` se rechaza porque queda una marca; `abba` se rechaza porque una `a` aparece después de empezar el bloque de `b`.

Para mantener visible la pila, la interfaz limita la entrada a 12 símbolos y seis símbolos del primer bloque.

El selector **Definir mi AP** abre un editor de transiciones. La regla `q0,a,⊥ -> q0,⊥A` significa: en `q0`, al leer `a` con `⊥` arriba, deja el fondo y apila `A`. `ε` no consume entrada; en la sustitución representa quitar el símbolo del tope. La máquina acepta por estado final después de consumir toda la cadena. En una máquina no determinista, la app busca una ruta de aceptación; si agota el presupuesto de configuraciones muestra **no evaluada**.

El editor carga de inicio un AP para `aⁿbⁿ`; con `aabb` apila dos marcas, las retira con las dos `b` y llega al final. La guía muestra paso a paso la función de las reglas y el cambio de la pila:

```text
q0,a,⊥ -> q0,⊥A
q0,a,A -> q0,AA
q0,b,A -> q1,ε
q1,b,A -> q1,ε
q1,ε,⊥ -> qf,⊥
```

| Entrada | Resultado esperado |
| --- | --- |
| `ab` | Aceptada |
| `aabb` | Aceptada |
| `aaabbb` | Aceptada |
| `aab` | Rechazada: quedan marcas en la pila |
| `abba` | Rechazada: una `a` aparece después de una `b` |
| `bba` | Rechazada |

### Nivel 1 — Autómata linealmente acotado

El módulo tiene sidebar y guía en tres pasos: elegir el patrón, configurar símbolos o transiciones, y seguir la cinta. El selector **Patrón del ejercicio** ofrece tres modos. El principal reconoce `xⁿyⁿzⁿ` para `n ≥ 1`, con la misma cantidad de los tres símbolos. El segundo reconoce `x·yⁿ·z²ⁿ`: **una sola `x`**, `n` símbolos `y` y `2n` símbolos `z`. Esta segunda forma también es libre de contexto; se conserva como práctica de la máquina, mientras `xⁿyⁿzⁿ` es el ejemplo característico del Nivel 1. **Definir mi LBA** permite ejecutar reglas propias.

En los dos patrones guiados, los campos reciben un carácter distinto cada uno. Para crear `aabbcc` con `xⁿyⁿzⁿ` o `abbcccc` con `x·yⁿ·z²ⁿ`, escribe `a`, `b`, `c`, elige **n = 2** y pulsa **Generar cadena**. `n` va de 1 a 5 y controla repeticiones; no forma parte de la cadena. Puedes editar el resultado antes de simular. `X`, `Y`, `Z`, `⊢` y `⊣` están reservados para las marcas y límites de cinta.

La cinta muestra `⊢` y `⊣` como fronteras fijas y señala la posición actual del cabezal. En `xⁿyⁿzⁿ`, cada ronda marca una `x`, una `y` y una `z` como `X`, `Y` y `Z`. En `x·yⁿ·z²ⁿ`, marca la única `x` y, por cada `y`, marca dos `z`. La entrada guiada se limita a 16 símbolos para mantener visible la traza.

| Entrada | Resultado esperado |
| --- | --- |
| `abc` | Aceptada |
| `aabbcc` | Aceptada |
| `aaabbbccc` | Aceptada |
| `aabcc` | Rechazada: cantidades distintas |
| `aabbc` | Rechazada: cantidades distintas |
| `abac` | Rechazada: orden inválido |

Con el segundo patrón, `abcc`, `abbcccc` y `abbbcccccc` se aceptan; `abbccc` y `aabcc` se rechazan.

**Definir mi LBA** permite especificar estados, alfabetos, finales y reglas como `q0,a -> q1,a,R`. `L`, `R` y `S` mueven el cabezal a la izquierda, derecha o lo dejan quieto. Declara `⊢` y `⊣` en el alfabeto de cinta; el validador impide borrarlos o cruzarlos. La máquina inicial de muestra acepta `ab`; `a` y `ba` se rechazan con esas reglas. Al editar el LBA, se ocultan esos ejemplos para evitar mostrar resultados que ya no correspondan a la máquina. La aceptación ocurre al alcanzar un estado final. La búsqueda de rutas usa un presupuesto de configuraciones; agotarlo significa **no evaluada**.

La definición inicial de muestra acepta `ab`: avanza por `a`, luego por `b`, y acepta al leer el delimitador derecho. El patrón `aⁿbⁿcⁿ` del modo guiado muestra un lenguaje sensible al contexto.

### Nivel 0 — Máquina de Turing

La pantalla guía el ejercicio en tres pasos: elegir una tarea, entender su formato o editar las reglas, y ejecutar la cadena siguiendo la cinta. El cabezal se mueve por posiciones de la cinta; la ventana se centra en él, `□` identifica una celda vacía y las marcas del palíndromo aparecen resaltadas.

1. **Palíndromo**: configura dos símbolos distintos de un carácter (por ejemplo `0,1` o `a,b`). La máquina compara los extremos, marca las parejas ya revisadas con `X` e `Y` y vuelve hacia el centro. Con `0,1`, acepta `0110`, `010` y la cadena vacía `ε`; rechaza `0101`. `X`, `Y` y `□` se reservan para marcas y blancos. La entrada admite hasta 24 caracteres.
2. **Suma unaria**: cada `1` representa una unidad y `+` separa los sumandos; no se escriben espacios. Elige `n` y `m` y pulsa **Generar entrada**, o escribe la cadena directamente. `n=3`, `m=2` genera `111+11`: representa 3 + 2 y produce `11111`; `1+1` produce `11`. El formato es `1ⁿ+1ᵐ`, con ambos sumandos positivos; la entrada admite hasta 28 caracteres.
3. **Definir mi MT**: edita estados, alfabeto de entrada y cinta, estado inicial, finales y transiciones `estado,lee -> siguiente,escribe,mueve`. `L`, `R` y `S` significan izquierda, derecha y quieto. El blanco `□` pertenece al alfabeto de cinta, pero no al de entrada. La máquina de muestra usa `q0,1 -> q0,1,R` y `q0,□ -> qf,1,S`: `111` se transforma en `1111`; `0` se rechaza porque no pertenece a Σ.

Al pulsar **Simular cadena**, la traza permite avanzar o reproducir cada regla. Una máquina personalizada acepta cuando alguna ruta llega a un estado final; si todas se detienen sin llegar a uno, rechaza. Una ruta cíclica o el límite de búsqueda produce **no evaluada**, porque una simulación finita no puede decidir si toda máquina arbitraria terminará. Después de editar reglas, la interfaz oculta las sugerencias con resultado fijo para no atribuirles una respuesta incorrecta.

## Comprobación de los modelos

Ejecuta las pruebas automáticas con:

```powershell
py -m unittest discover -s tests -v
```

Se comparan los cuatro reconocedores con definiciones independientes de sus lenguajes en conjuntos exhaustivos de cadenas cortas. También se comprueban la equivalencia AFN/AFD, la base de la pila, los límites de la cinta acotada, la suma unaria y la distinción entre rechazo y límite de visualización. GitHub Actions ejecuta estas pruebas en Python 3.9 y 3.12 tras cada envío o solicitud de integración.

## Alcance

Los cuatro niveles admiten ahora máquinas definidas por transiciones, además de los recorridos guiados. Los intérpretes aceptan notación de un carácter para símbolos y hasta 8 estados; cada modo limita además el número de reglas. El AP busca rutas no deterministas con tope de 5.000 configuraciones y pila de 64 marcas; LBA y MT usan hasta 5.000 configuraciones y 1.000 pasos por ruta. Si el presupuesto no alcanza, el resultado es **no evaluada**. La MT reporta también inconcluso si detecta una configuración repetida. Una MT arbitraria puede no terminar y el problema de parada es indecidible, así que la app no promete decidir todos los programas o lenguajes.

## Estructura del proyecto

```text
Proyecto_Automatas/
├── .github/workflows/tests.yml
├── main.py
├── interfaz/
│   ├── menu.py
│   ├── pantalla_inicio.py
│   ├── simulador.py
│   └── parametrizacion_colores.py
├── modelos/
│   ├── formales.py
│   ├── nivel0.py
│   ├── nivel1.py
│   ├── nivel2.py
│   └── nivel3.py
├── tests/test_modelos.py
├── documentacion/implementacion.md
└── README.md
```

La explicación de los conceptos, algoritmos, estructura y guía para la sustentación está en [`documentacion/implementacion.md`](documentacion/implementacion.md).

## Repositorio público

El checkout debe apuntar a un repositorio público de GitHub o GitLab. Crea el repositorio vacío (sin archivos iniciales), configura su URL y publica la rama `main`:

```bash
git remote set-url origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main
```

Después comparte el enlace del repositorio en la entrega académica. La aplicación funciona localmente sin configurar servicios externos.
