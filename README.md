# Jerarquía de Chomsky

Proyecto para implementar y simular los modelos computacionales asociados a los
niveles de la jerarquía de Chomsky.

## Estructura

```text
jerarquia_chomsky/
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

En este repositorio, la carpeta raíz del proyecto es el propio directorio
`Proyecto_Automatas`.

## Instalación y ejecución

Se requiere Python 3. Desde la carpeta raíz, inicia el punto de entrada con:

```bash
python main.py
```

Los módulos están preparados como estructura inicial; la interfaz y los
simuladores se implementarán en las siguientes etapas.

## Modelos previstos

- Nivel 3: autómata finito.
- Nivel 2: autómata de pila.
- Nivel 1: autómata acotado.
- Nivel 0: máquina de Turing.

Consulta [documentacion/implementacion.md](documentacion/implementacion.md)
para el alcance técnico previsto.

