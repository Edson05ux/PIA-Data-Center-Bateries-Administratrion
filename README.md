# PIA: Administración de baterías de un centro de datos

Aplicación de consola desarrollada en Python para estimar el balance neto de
energía de las baterías de respaldo de un centro de datos. A partir de
mediciones de potencia en kW, el programa ajusta una función polinomial que pasa
por todos los datos y calcula su integral a lo largo del día mediante la regla
compuesta del trapecio.

## Descripción

El programa solicita al usuario al menos dos mediciones de potencia. Cada
medición se compone de una hora del día (entero entre 0 y 23) y una potencia en
kW:

- **Potencia positiva:** entrada de energía; la red carga las baterías.
- **Potencia negativa:** salida de energía; las baterías se descargan.

Con las mediciones se construye un polinomio que pasa exactamente por todos los
puntos. La cantidad de mediciones determina el grado de la función:

| Mediciones | Función resultante |
| ---------- | ------------------ |
| 2          | lineal             |
| 3          | cuadrática         |
| 4          | cúbica             |
| n          | grado n - 1        |

Los coeficientes se obtienen resolviendo el sistema de Vandermonde con el
**método de Montante**, implementado en el Proyecto 1. El cálculo se realiza con
aritmética exacta mediante `Fraction`, por lo que no se acumulan errores de
redondeo en los coeficientes.

Finalmente, la función de potencia `f(t)` se integra de 0 a 24 horas con la
**regla compuesta del trapecio**. El usuario indica cuántos trapecios desea
utilizar; una mayor cantidad reduce el ancho de cada subintervalo y, en general,
mejora la estimación.

El resultado es el cambio neto de energía respecto a la carga inicial de la
batería, que se desconoce:

- **Balance positivo:** la batería terminó con más carga que al inicio.
- **Balance negativo:** la batería terminó con menos carga que al inicio.
- **Balance cero:** la carga final es igual a la inicial.

## Características

- Menú interactivo completamente en español.
- Validación de todos los datos ingresados por el usuario.
- Mínimo de dos mediciones y horas distintas para poder ajustar la función.
- Acepta potencias enteras o decimales, positivas o negativas.
- Cálculo exacto de coeficientes e integral con `fractions.Fraction`.
- Presentación de la matriz aumentada, los coeficientes y la función ajustada.
- Interpretación automática del balance de energía.
- Solo utiliza la biblioteca estándar de Python.

## Requisitos

- Python 3.8 o superior (desarrollado con Python 3.14).
- No requiere dependencias externas.

## Ejecución

Desde la raíz del proyecto:

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
        ├── __init__.py             # Paquete de módulos
        ├── ajuste.py               # Sistema de Vandermonde y polinomio
        ├── integracion.py          # Regla compuesta del trapecio
        ├── menu.py                 # Menú interactivo
        ├── montante.py             # Método de Montante (reutilizado)
        └── utils.py                # Entrada, formato y consola (reutilizado)
```

| Archivo | Responsabilidad |
| ------- | --------------- |
| `src/main.py` | Punto de entrada; inicia el menú con `modules.menu.run`. |
| `src/modules/menu.py` | Captura de mediciones, solicitud de trapecios y presentación de resultados. |
| `src/modules/ajuste.py` | Construcción del sistema de Vandermonde, resolución de coeficientes y evaluación del polinomio. |
| `src/modules/integracion.py` | Implementación de la regla compuesta del trapecio. |
| `src/modules/montante.py` | Método de Montante para resolver sistemas de ecuaciones (reutilizado del Proyecto 1). |
| `src/modules/utils.py` | Lectura y validación de datos, formato numérico y control de consola (reutilizado del Proyecto 1). |

## Uso

Al iniciar el programa se muestra el menú principal:

```
=== Balance de energía en baterías de un centro de datos ===

Menú:
  1) Calcular balance de energía del día
  2) Salir
```

La opción 1 solicita:

1. La cantidad de mediciones que se van a ingresar (mínimo 2).
2. Para cada medición:
   - La hora del día, como entero entre 0 y 23.
   - La potencia en kW. Los valores positivos representan carga y los
     negativos, descarga.
3. La cantidad de trapecios que se usarán en la integración.

No se permiten dos mediciones en la misma hora, ya que una función no puede
tomar dos valores distintos en el mismo instante.

Después de leer los datos, el programa muestra:

- La matriz aumentada del sistema de Vandermonde.
- Los coeficientes del polinomio, tanto en fracción exacta como en decimal
  aproximado.
- La función de potencia ajustada en términos de `t` (hora).
- El ancho de cada trapecio (`Δt`).
- La energía neta del día en kWh.
- La interpretación del balance respecto a la carga inicial.

## Ejemplo de ejecución

Supóngase que se registran 10 kW a las 0 h y -5 kW a las 12 h, y que se eligen
6 trapecios.

Entrada:

```
¿Cuántas mediciones deseas ingresar? (mínimo 2): 2

Medición 1:
  Hora (0-23): 0
  Potencia en kW (+ carga / - descarga): 10

Medición 2:
  Hora (0-23): 12
  Potencia en kW (+ carga / - descarga): -5

¿Cuántos trapecios deseas usar? (más trapecios = mejor estimación): 6
```

Salida (fragmento):

```
=== Ajuste polinomial con el método de Montante ===
--- Sistema de ecuaciones (matriz aumentada) ---
  1   0  10
  1  12  -5

=== Resultados ===

Puntos registrados:
  Hora 0: 10 kW
  Hora 12: -5 kW

Coeficientes del polinomio (de menor a mayor grado):
  a0 = 10 ≈ 10
  a1 = -5/4 ≈ -1.25

Función de potencia ajustada:
  f(t) = -(5/4)t + 10

Integración con la regla del trapecio:
  Intervalo: 0 a 24 h
  Trapecios: 6
  Δt = 4 h
  Energía neta = -120 kWh ≈ -120 kWh

Interpretación del balance:
  La batería terminó con 120 kWh menos que su carga inicial (predominó la descarga).
  El balance es el cambio neto respecto a la carga inicial (desconocida).
```

Como la función ajustada es lineal, la regla del trapecio obtiene el valor
exacto de la integral:

```
∫₀²⁴ (10 - 5t/4) dt = -120 kWh
```

## Métodos numéricos

### Ajuste polinomial

Para `n` mediciones `(t_i, p_i)` se plantea un polinomio de grado `n - 1`:

```
f(t) = a0 + a1·t + a2·t² + ... + a(n-1)·t^(n-1)
```

La condición de que la función pase por cada medición genera el sistema de
Vandermonde:

```
a0 + a1·t_i + a2·t_i² + ... + a(n-1)·t_i^(n-1) = p_i
```

para `i = 1, 2, ..., n`. En forma matricial, cada fila corresponde a una
medición y tiene la forma `[1, t_i, t_i², ..., t_i^(n-1) | p_i]`.

El sistema se resuelve con `resolver_sistema` del módulo `montante.py`, que
aplica eliminación de Montante con aritmética exacta. Como todas las horas son
distintas, la matriz de Vandermonde es no singular y el polinomio obtenido
interpola exactamente todos los puntos.

Este programa realiza una **interpolación**, no un ajuste por mínimos cuadrados:
con `n` datos se calculan `n` coeficientes y la curva pasa por todas las
mediciones.

### Regla compuesta del trapecio

Para aproximar la integral de `f(t)` en el intervalo `[a, b]` con `n`
subintervalos:

```
h = (b - a) / n

∫ₐᵇ f(t) dt ≈ (h / 2) · [f(t0) + 2·f(t1) + 2·f(t2) + ... + 2·f(t(n-1)) + f(tn)]
```

donde `t0 = a`, `tn = b` y `t(k) = a + k·h`.

En este proyecto `a = 0` y `b = 24`, por lo que la integral representa la
energía neta intercambiada durante el día:

```
Energía neta ≈ ∫₀²⁴ f(t) dt
```

La unidad del resultado es kWh, ya que la potencia está en kW y el tiempo en
horas. Si `f(t)` es lineal, la regla del trapecio es exacta para cualquier
cantidad de trapecios; para funciones de grado mayor es una aproximación que
mejora al aumentar `n`.

La integral se evalúa en el día completo `[0, 24]`. Si las mediciones no cubren
todo ese intervalo, el polinomio se extrapola para las horas sin medición, por
lo que el resultado debe interpretarse como una estimación basada en el modelo
ajustado.

## Validaciones y manejo de errores

- La cantidad de mediciones debe ser un entero positivo y al menos 2.
- La hora debe ser un entero entre 0 y 23 y no puede repetirse.
- La potencia debe ser un número entero o decimal finito; se aceptan valores
  positivos y negativos.
- La cantidad de trapecios debe ser un entero positivo.
- Ante una entrada inválida, el programa muestra el error y vuelve a solicitar
  el dato.
- `Ctrl+C` o el fin de la entrada terminan el programa de forma ordenada.

## Reutilización de proyectos anteriores

- `modules/montante.py` conserva la implementación del método de Montante del
  Proyecto 1, incluyendo `resolver_sistema` y `mostrar_matriz`.
- `modules/utils.py` reutiliza del Proyecto 1 las funciones de lectura,
  formateo y control de consola: `leer_int`, `leer_fraccion`, `leer_opcion`,
  `formatear_a_fraccion`, `formatear_a_decimal`, `borrar_consola` y `pausar`.
- La organización `src/main.py` + `src/modules` sigue la misma estructura de
  entrada utilizada en los proyectos anteriores; `modules/__init__.py` define
  el paquete de módulos.

## Limitaciones

- La carga inicial de la batería es desconocida; el programa calcula únicamente
  el cambio neto, no el estado absoluto de carga.
- La calidad del resultado depende de la cantidad y representatividad de las
  mediciones.
- Un número muy grande de mediciones eleva el grado del polinomio y puede
  producir oscilaciones entre los puntos (fenómeno de Runge).
- El programa no guarda los datos entre ejecuciones; cada cálculo comienza
  desde cero.
