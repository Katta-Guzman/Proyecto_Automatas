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

Desde la pantalla inicial, selecciona uno de los cuatro niveles. En cada simulador puedes elegir un ejemplo, editar la entrada y pulsar **Simular**. Usa **Anterior**, **Siguiente** o **Reproducir** para recorrer la ejecución. La tabla de la derecha también permite saltar a un paso al seleccionar su fila. **Limpiar** restablece la vista.

## Módulos y ejemplos

### Nivel 3 — Autómata finito determinista

Reconoce cadenas no vacías que terminan en un símbolo configurado. Puedes cambiar el alfabeto (símbolos de un carácter separados por comas) y el símbolo final. El ejemplo inicial usa alfabeto `{a,b}` y símbolo final `a`.

La traza se limita a entradas de 500 símbolos.

| Entrada | Resultado esperado |
| --- | --- |
| `a` | Aceptada |
| `ba` | Aceptada |
| `baba` | Aceptada |
| `b` | Rechazada |
| `abb` | Rechazada |
| `ε` (entrada vacía) | Rechazada |

### Nivel 2 — Autómata de pila

Reconoce `L = {aⁿbⁿ | n ≥ 1}`. Por cada `a` apila `A`; por cada `b` desapila una `A`. La pila empieza con el marcador `⊥`.

Para mantener visible la pila, la interfaz limita la entrada a 12 símbolos y seis `a`.

| Entrada | Resultado esperado |
| --- | --- |
| `ab` | Aceptada |
| `aabb` | Aceptada |
| `aaabbb` | Aceptada |
| `aab` | Rechazada: quedan marcas en la pila |
| `abba` | Rechazada: una `a` aparece después de una `b` |
| `bba` | Rechazada |

### Nivel 1 — Autómata linealmente acotado

Reconoce `L = {aⁿbⁿcⁿ | n ≥ 1}`. La cinta de entrada queda encerrada por `⊢` y `⊣`. En cada ronda marca una `a`, una `b` y una `c` como `X`, `Y` y `Z`, y mueve el cabezal en ambos sentidos. Se limita la entrada a 16 símbolos para que la traza pueda recorrerse con fluidez.

| Entrada | Resultado esperado |
| --- | --- |
| `abc` | Aceptada |
| `aabbcc` | Aceptada |
| `aaabbbccc` | Aceptada |
| `aabcc` | Rechazada: cantidades distintas |
| `aabbc` | Rechazada: cantidades distintas |
| `abac` | Rechazada: orden inválido |

### Nivel 0 — Máquina de Turing

El selector ofrece dos ejemplos computables:

1. **Palíndromo binario**: marca símbolos de los extremos y compara cada pareja. Acepta `0110`, `010` y la cadena vacía `ε`; rechaza `0101`.
2. **Suma unaria**: interpreta cada `1` como una unidad y transforma `1ⁿ+1ᵐ`, con `n,m ≥ 1`, en el bloque resultado. `111+11` produce `11111` (3 + 2 = 5); `1+1` produce `11`.

La ventana de cinta muestra celdas blancas `□` y se desplaza alrededor del cabezal para representar la cinta extendible.

## Estructura del proyecto

```text
Proyecto_Automatas/
├── main.py
├── interfaz/
│   ├── menu.py
│   └── simulador.py
├── modelos/
│   ├── nivel3.py
│   ├── nivel2.py
│   ├── nivel1.py
│   └── nivel0.py
├── documentacion/
│   └── implementacion.md
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
