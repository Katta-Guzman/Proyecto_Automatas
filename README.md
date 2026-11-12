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

El selector **Tipo de AFN** ofrece dos máquinas:

1. **Termina en símbolo**: reconoce `Σ* f`, donde `f` es el símbolo final. Puedes cambiar el alfabeto (símbolos de un carácter separados por comas) y `f`. La pantalla dibuja el AFN y su AFD. Por defecto usa `a,b` y `f=a`; puedes probar `a,b,1`.
2. **Contiene dos iguales seguidos**: usa dos ramas con transiciones `ε`, como el diagrama de referencia. Con `0,1` acepta cualquier cadena que contenga `00` o `11` en alguna posición. Los dos símbolos también se pueden cambiar.
3. **Definir mi AFN-ε**: pulsa **Editar reglas del AFN-ε** y declara estados, alfabeto, inicial, finales y una transición por línea con el formato `origen,símbolo -> destino1,destino2`. Por ejemplo, `q0,ε -> q1` o `q1,1 -> q1,q2`. Las transiciones ausentes llevan al conjunto vacío. Al aplicar, se validan las referencias y se genera el grafo y el AFD por subconjuntos alcanzables. El editor admite hasta 8 estados, 6 símbolos y 256 subconjuntos del AFD para que la vista siga siendo manejable.

El AFN, sus estados activos y la tabla de subconjuntos alcanzables del AFD se calculan desde las reglas, no desde una lista fija de respuestas. Desplaza el gráfico para recorrerlo.

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

Reconoce cadenas con la forma `XⁿYⁿ`, para `n ≥ 1`. Puedes cambiar los dos símbolos por letras o números. Por cada símbolo del primer bloque apila `A`; por cada símbolo del segundo bloque desapila una `A`. La pila empieza con `⊥`.

Los campos **Apila una marca por** y **Retira una marca por** reciben un solo carácter cada uno. Si quieres `aaabbb`, conserva `a` y `b`, elige **n = 3** y pulsa **Generar cadena**. También puedes escribir la cadena a mano.

Para mantener visible la pila, la interfaz limita la entrada a 12 símbolos y seis símbolos del primer bloque.

El selector **Definir mi AP** abre un editor de transiciones. La regla `q0,a,⊥ -> q0,⊥A` significa: en `q0`, al leer `a` con `⊥` arriba, deja el fondo y apila `A`. `ε` no consume entrada; en la sustitución representa quitar el símbolo del tope. La máquina acepta por estado final después de consumir toda la cadena. En una máquina no determinista, la app busca una ruta de aceptación; si agota el presupuesto de configuraciones muestra **no evaluada**.

El editor carga de inicio un AP para `aⁿbⁿ`; con `aabb` apila dos marcas, las retira con las dos `b` y llega al final:

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

El selector **Patrón del lenguaje** ofrece dos opciones. La principal reconoce `aⁿbⁿcⁿ` para `n ≥ 1`, con la misma cantidad de los tres símbolos. La otra reconoce `abⁿc²ⁿ`: **una sola `a`**, `n` letras `b` y `2n` letras `c`. Por ejemplo, con `n=2` genera `abbcccc`. Puedes configurar tres letras o números distintos. La cinta queda encerrada por `⊢` y `⊣`; en cada ronda marca los símbolos necesarios como `X`, `Y` y `Z`. Se limita la entrada a 16 símbolos para mantener visible la traza.

**Símbolo a**, **Símbolo b** y **Símbolo c** reciben un carácter distinto cada uno. Para crear `aabbcc` en el primer patrón o `abbcccc` en el segundo, escribe `a`, `b` y `c`, elige **n = 2** y pulsa **Generar cadena**. `n` va de 1 a 5; la cadena generada se puede editar antes de simular. Escribir `bb` o `cccc` en un campo de símbolo produce un error porque esos campos no representan bloques completos.

| Entrada | Resultado esperado |
| --- | --- |
| `abc` | Aceptada |
| `aabbcc` | Aceptada |
| `aaabbbccc` | Aceptada |
| `aabcc` | Rechazada: cantidades distintas |
| `aabbc` | Rechazada: cantidades distintas |
| `abac` | Rechazada: orden inválido |

Con el segundo patrón, `abcc`, `abbcccc` y `abbbcccccc` se aceptan; `abbccc` y `aabcc` se rechazan.

**Definir mi LBA** permite especificar estados, alfabetos, finales y reglas como `q0,a -> q1,a,R`. `L`, `R` y `S` mueven el cabezal a la izquierda, derecha o lo dejan quieto. Declara `⊢` y `⊣` en el alfabeto de cinta; el validador impide borrarlos o cruzarlos. La aceptación ocurre al alcanzar un estado final. La búsqueda de rutas usa un presupuesto de configuraciones; agotarlo significa **no evaluada**.

La definición inicial de muestra acepta `ab`: avanza por `a`, luego por `b`, y acepta al leer el delimitador derecho. El patrón `aⁿbⁿcⁿ` del modo guiado muestra un lenguaje sensible al contexto.

### Nivel 0 — Máquina de Turing

El selector ofrece dos ejemplos computables:

1. **Palíndromo**: elige dos símbolos (por ejemplo `0,1` o `a,b`); la máquina marca los extremos y compara cada pareja. Con `0,1`, acepta `0110`, `010` y la cadena vacía `ε`; rechaza `0101`.
2. **Suma unaria**: interpreta cada `1` como una unidad y transforma `1ⁿ+1ᵐ`, con `n,m ≥ 1`, en el bloque resultado. `111+11` produce `11111` (3 + 2 = 5); `1+1` produce `11`.

La ventana de cinta representa las celdas vacías con `□` y se desplaza alrededor del cabezal para mostrar la cinta extendible.

**Definir mi MT** deja editar las transiciones `estado,lee -> siguiente,escribe,mueve`, con `L`, `R` o `S`. Añade `□` al alfabeto de cinta para leer y escribir blancos. Un estado final acepta y una regla ausente detiene esa ruta sin aceptación. Una MT que repite una configuración o agota el presupuesto queda **no evaluada**: una simulación finita no puede decidir si toda MT arbitraria terminará.

La máquina inicial recorre los unos y escribe uno adicional en el primer blanco; así `111` queda como `1111`.

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
