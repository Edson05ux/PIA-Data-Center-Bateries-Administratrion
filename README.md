# PIA: Administración de baterías de un centro de datos

Programa de línea de comandos en Python que estima el cambio neto de energía de
las baterías de respaldo (UPS) de un centro de datos a partir de mediciones de
potencia.

## Descripción

El programa solicita al usuario al menos dos mediciones de potencia, cada una
asociada a una hora del día (0-23):

- **Potencia positiva:** la red carga las baterías (entrada).
- **Potencia negativa:** las baterías se descargan (salida).

Con los puntos `(hora, potencia)` se ajusta un polinomio que pasa exactamente
por todas las mediciones:

| Mediciones | Función ajustada |
| ---------- | ---------------- |
| 2          | lineal           |
| 3          | cuadrática       |
| n          | grado n - 1      |

Los coeficientes se calculan resolviendo el sistema de Vandermonde con el
**método de Montante** del Proyecto 1, usando aritmética exacta con
`Fraction`.

Después se integra la función de potencia `f(t)` de 0 a 24 horas con la
**regla compuesta del trapecio**. El usuario elige el número de trapecios: a
mayor cantidad, mejor es la estimación. La energía neta obtenida es el cambio
respecto a la carga inicial de la batería (desconocida):

- **Resultado positivo:** la batería terminó con más carga.
- **Resultado negativo:** la batería terminó con menos carga.
- **Resultado cero:** la carga final es igual a la inicial.

## Requisitos

- Python 3.8 o superior (desarrollado en Python 3.14).
- No requiere dependencias externas.

## Ejecución

```bash
# Opción 1: usar el script de ejecución
bash exec.sh

# Opción 2: ejecutar directamente
python3 src/main.py
```

## Estructura del proyecto

```
.
├── exec.sh                         # Script de ejecución
├── README.md
├── .gitignore
└── src/
    ├── main.py                     # Punto de entrada
    └── modules/
        ├── __init__.py             # Paquete
        ├── ajuste.py               # Sistema de Vandermonde y polinomio
        ├── integracion.py          # Regla compuesta del trapecio
        ├── menu.py                 # Menú interactivo
        ├── montante.py             # Método de Montante (reutilizado)
        └── utils.py                # Entrada, formato y consola (reutilizado)
```

## Uso

Al ejecutar el programa se muestra el menú:

```
1) Calcular balance de energía del día
2) Salir
```

La opción 1 solicita:

1. La cantidad de mediciones (mínimo 2).
2. Para cada medición, la hora (entero entre 0 y 23) y la potencia en kW.
   No se permiten dos mediciones en la misma hora.
3. La cantidad de trapecios para la integración.

El programa muestra:

- La matriz aumentada del sistema de Vandermonde.
- Los coeficientes exactos y aproximados del polinomio.
- La función ajustada en términos de `t` (hora).
- La energía neta del día en kWh y la interpretación del balance.

## Ejemplo

Mediciones: 10 kW a las 0 h y -5 kW a las 12 h. Trapecios: 6.

```
Función de potencia ajustada:
  f(t) = -(5/4)t + 10

Integración con la regla del trapecio:
  Intervalo: 0 a 24 h
  Trapecios: 6
  Δt = 4 h
  Energía neta = -120 kWh ≈ -120 kWh

Interpretación del balance:
  La batería terminó con 120 kWh menos que su carga inicial (predominó la descarga).
```

En este caso la función es lineal, por lo que la regla del trapecio obtiene el
valor exacto de la integral:

```
∫₀²⁴ (10 - 5t/4) dt = -120 kWh
```

## Métodos

### Ajuste polinomial

Para `n` mediciones `(t_i, p_i)` se plantea el sistema de Vandermonde:

```
a0 + a1·t_i + a2·t_i² + ... + a(n-1)·t_i^(n-1) = p_i    para i = 1..n
```

La matriz de coeficientes y el vector de términos independientes se resuelven
con `resolver_sistema` del módulo `montante.py`. Al tener todas las horas
distintas, el sistema tiene solución única y el polinomio pasa por todos los
puntos.

### Regla del trapecio

Para `n` trapecios en el intervalo `[a, b]`:

```
h = (b - a) / n

∫ₐᵇ f(t) dt ≈ (h / 2) · [f(a) + 2·f(a + h) + ... + 2·f(b - h) + f(b)]
```

La integral se evalúa en el día completo `[0, 24]`; si las mediciones no cubren
todo ese intervalo, el polinomio se extrapola para las horas sin medición.

## Reutilización de proyectos anteriores

- `modules/montante.py` conserva la implementación del método de Montante del
  Proyecto 1 (`resolver_sistema`, `mostrar_matriz`, etc.).
- `modules/utils.py` reutiliza las funciones de entrada, formato y control de
  consola del Proyecto 1 (`leer_int`, `leer_fraccion`, `leer_opcion`,
  `formatear_a_decimal`, `borrar_consola`, `pausar`).
- `src/main.py` y `modules/__init__.py` siguen la misma estructura de entrada
  usada en los proyectos anteriores.
