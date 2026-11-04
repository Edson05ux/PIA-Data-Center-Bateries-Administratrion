# PIA: Administración de baterías de un centro de datos

Aplicación de escritorio y de consola desarrollada en Python para estimar el
balance neto de energía de las baterías de respaldo de un centro de datos. A
partir de mediciones de potencia en kW, el programa ajusta una función
polinomial que pasa por todos los datos y calcula su integral a lo largo del día
mediante la regla compuesta del trapecio.

El proyecto incluye dos interfaces que comparten el mismo motor de cálculo:

- **Interfaz gráfica (GUI):** aplicación de escritorio con `customtkinter`.
- **Interfaz de consola (CLI):** menú interactivo en la terminal.

También incluye ejecutables autocontenidos para Linux y Windows en
`attachables/`, por lo que no es necesario tener Python instalado para usarlos.

## Descripción

El programa solicita al usuario al menos tres mediciones de potencia. Cada
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

La aplicación exige un mínimo de tres mediciones para calcular el balance, por
lo que el caso más simple que se puede resolver desde la GUI o la CLI es una
función cuadrática.

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

- Dos interfaces: GUI de escritorio y menú interactivo de consola.
- Interfaz completamente en español.
- Validación de todos los datos ingresados por el usuario.
- Mínimo de tres mediciones y horas distintas para poder calcular.
- Acepta potencias enteras o decimales, positivas o negativas.
- Cálculo exacto de coeficientes e integral con `fractions.Fraction`.
- Presentación de la matriz aumentada, los coeficientes y la función ajustada.
- Interpretación automática del balance de energía.
- La GUI permite agregar, eliminar y limpiar mediciones antes de calcular.
- Ejecutables autocontenidos para Linux y Windows.

## Requisitos

### Ejecutar desde el código fuente

- Python 3.8 o superior (desarrollado y probado con Python 3.14).
- Para la CLI: solo la biblioteca estándar de Python.
- Para la GUI: `customtkinter` y `tkinter`.

En Arch Linux / CachyOS, `customtkinter` está disponible en los repositorios:

```bash
sudo pacman -S python-customtkinter
```

También se puede instalar con `pip` dentro de un entorno virtual:

```bash
python3 -m venv .venv
.venv/bin/pip install customtkinter
```

En Windows:

```powershell
pip install customtkinter
```

### Usar los ejecutables

Los archivos de `attachables/` son autocontenidos y no requieren Python ni
dependencias adicionales:

- `PIA_GUI` y `PIA_CLI` para Linux.
- `PIA_GUI.exe` y `PIA_CLI.exe` para Windows.

## Ejecución

Desde la raíz del proyecto:

### Interfaz gráfica

```bash
# Linux
bash exec_gui.sh
# o directamente
python3 src/gui_app.py
```

```bat
:: Windows
run_gui.bat
:: o directamente
python src\gui_app.py
```

### Interfaz de consola

```bash
# Linux
bash exec.sh
# o directamente
python3 src/main.py
```

```bat
:: Windows
python src\main.py
```

### Ejecutables

```bash
# Linux
./attachables/PIA_GUI
./attachables/PIA_CLI
```

```bat
:: Windows
attachables\PIA_GUI.exe
attachables\PIA_CLI.exe
```

Los ejecutables de Linux fueron compilados en CachyOS; si se ejecutan en una
distribución con una versión de `glibc` incompatible, puede ser necesario
recompilarlos o usar la versión de consola desde el código fuente.

## Estructura del proyecto

```
.
├── attachables/                    # Ejecutables autocontenidos
│   ├── PIA_CLI                     # CLI para Linux
│   ├── PIA_CLI.exe                 # CLI para Windows
│   ├── PIA_GUI                     # GUI para Linux
│   └── PIA_GUI.exe                 # GUI para Windows
├── diagrams/                       # Diagramas de flujo de los módulos
├── docs/                           # Documento del proyecto (DOCX y PDF)
├── exec.sh                         # Ejecuta la CLI en Linux
├── exec_gui.sh                     # Ejecuta la GUI en Linux
├── run_gui.bat                     # Ejecuta la GUI en Windows
├── README.md
└── src/
    ├── gui_app.py                  # Punto de entrada de la GUI
    ├── main.py                     # Punto de entrada de la CLI
    └── modules/
        ├── __init__.py             # Paquete de módulos
        ├── ajuste.py               # Sistema de Vandermonde y polinomio
        ├── integracion.py          # Regla compuesta del trapecio
        ├── menu.py                 # Menú interactivo de la CLI
        ├── montante.py             # Método de Montante (reutilizado)
        └── utils.py                # Entrada, formato y consola (reutilizado)
```

| Archivo | Responsabilidad |
| ------- | --------------- |
| `src/gui_app.py` | Interfaz gráfica con `customtkinter`: captura de mediciones, validación, cálculo y presentación de resultados. |
| `src/main.py` | Punto de entrada de la CLI; inicia el menú con `modules.menu.run`. |
| `src/modules/menu.py` | Captura de mediciones, solicitud de trapecios y presentación de resultados en consola. |
| `src/modules/ajuste.py` | Construcción del sistema de Vandermonde, resolución de coeficientes y evaluación del polinomio. |
| `src/modules/integracion.py` | Implementación de la regla compuesta del trapecio. |
| `src/modules/montante.py` | Método de Montante para resolver sistemas de ecuaciones (reutilizado del Proyecto 1). |
| `src/modules/utils.py` | Lectura y validación de datos, formato numérico y control de consola (reutilizado del Proyecto 1). |

## Uso

### Interfaz gráfica

La GUI muestra un panel para capturar mediciones y otro para los resultados.

1. Escribe la **hora** (0-23) y la **potencia** en kW.
2. Presiona **Agregar medición** (o `Enter`).
3. Repite el proceso hasta tener al menos tres mediciones.
4. Indica la cantidad de **trapecios**.
5. Presiona **Calcular balance** (o `Enter` desde el campo de trapecios).

La lista de mediciones permite eliminar puntos individuales o limpiar todo con
**Limpiar**. Las tarjetas superiores muestran la cantidad de puntos, el rango de
horas y el estado del cálculo. El panel de resultados presenta la matriz
aumentada, los coeficientes, la función ajustada, el ancho de cada trapecio, la
energía neta y la interpretación del balance.

La GUI aplica las mismas validaciones que la CLI: mínimo tres mediciones, horas
entre 0 y 23 sin duplicados, potencias numéricas y un número entero positivo de
trapecios.

### Interfaz de consola

Al iniciar la CLI se muestra el menú principal:

```
=== Balance de energía en baterías de un centro de datos ===

Menú:
  1) Calcular balance de energía del día
  2) Salir
```

La opción 1 solicita:

1. La cantidad de mediciones que se van a ingresar (mínimo 3).
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

Supóngase que se registran 10 kW a las 0 h, 4 kW a las 6 h y -5 kW a las 12 h, y
que se eligen 6 trapecios.

Entrada:

```
¿Cuántas mediciones deseas ingresar? (mínimo 3): 3

Medición 1:
  Hora (0-23): 0
  Potencia en kW (+ carga / - descarga): 10

Medición 2:
  Hora (0-23): 6
  Potencia en kW (+ carga / - descarga): 4

Medición 3:
  Hora (0-23): 12
  Potencia en kW (+ carga / - descarga): -5

¿Cuántos trapecios deseas usar? (más trapecios = mejor estimación): 6
```

Salida (fragmento):

```
=== Ajuste polinomial con el método de Montante ===
--- Sistema de ecuaciones (matriz aumentada) ---
  1   0    0  10
  1   6   36   4
  1  12  144  -5

=== Resultados ===

Puntos registrados:
  Hora 0: 10 kW
  Hora 6: 4 kW
  Hora 12: -5 kW

Coeficientes del polinomio (de menor a mayor grado):
  a0 = 10 ≈ 10
  a1 = -3/4 ≈ -0.75
  a2 = -1/24 ≈ -0.041667

Función de potencia ajustada:
  f(t) = -(1/24)t^2 - (3/4)t + 10

Integración con la regla del trapecio:
  Intervalo: 0 a 24 h
  Trapecios: 6
  Δt = 4 h
  Energía neta = -512/3 kWh ≈ -170.666667 kWh

Interpretación del balance:
  La batería terminó con 170.666667 kWh menos que su carga inicial (predominó la descarga).
  El balance es el cambio neto respecto a la carga inicial (desconocida).
```

La energía neta también se puede calcular analíticamente:

```
∫₀²⁴ (-(1/24)t² - (3/4)t + 10) dt = -512/3 kWh ≈ -170.666667 kWh
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

- La cantidad de mediciones debe ser al menos 3.
- La hora debe ser un entero entre 0 y 23 y no puede repetirse.
- La potencia debe ser un número entero o decimal finito; se aceptan valores
  positivos y negativos.
- La cantidad de trapecios debe ser un entero positivo.
- En la CLI, ante una entrada inválida se muestra el error y se vuelve a
  solicitar el dato.
- En la GUI, los errores se muestran en la etiqueta de estado y en el panel de
  resultados.
- `Ctrl+C` o el fin de la entrada terminan la CLI de forma ordenada.

## Compilación de ejecutables

Los ejecutables se generaron con **PyInstaller** en modo `--onefile`. Para
reconstruirlos:

```bash
python3 -m venv .venv-build
.venv-build/bin/pip install pyinstaller customtkinter

# GUI
.venv-build/bin/pyinstaller --noconfirm --clean --onefile --windowed \
  --name PIA_GUI --collect-all customtkinter src/gui_app.py

# CLI
.venv-build/bin/pyinstaller --noconfirm --clean --onefile \
  --name PIA_CLI src/main.py
```

Los resultados se generan en `dist/PIA_GUI` y `dist/PIA_CLI` (Linux), o con
extensión `.exe` en Windows. Después se copian a `attachables/`. Para compilar
la versión de Windows se debe ejecutar el mismo comando con un Python de
Windows o dentro de Wine, usando `python -m PyInstaller`.

## Reutilización de proyectos anteriores

- `modules/montante.py` conserva la implementación del método de Montante del
  Proyecto 1, incluyendo `resolver_sistema` y `mostrar_matriz`.
- `modules/utils.py` reutiliza del Proyecto 1 las funciones de lectura,
  formateo y control de consola: `leer_int`, `leer_fraccion`, `leer_opcion`,
  `formatear_a_fraccion`, `formatear_a_decimal`, `borrar_consola` y `pausar`.
- La organización `src/main.py` + `src/modules` sigue la misma estructura de
  entrada utilizada en los proyectos anteriores; `modules/__init__.py` define
  el paquete de módulos. La GUI reutiliza los mismos módulos de cálculo.

## Limitaciones

- La carga inicial de la batería es desconocida; el programa calcula únicamente
  el cambio neto, no el estado absoluto de carga.
- La calidad del resultado depende de la cantidad y representatividad de las
  mediciones.
- Un número muy grande de mediciones eleva el grado del polinomio y puede
  producir oscilaciones entre los puntos (fenómeno de Runge).
- El programa no guarda los datos entre ejecuciones; cada cálculo comienza
  desde cero.
