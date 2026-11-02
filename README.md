# PIA-Data-Center-Bateries-Administratrion
# SmartGrid UPS Flow: Control de Flujo de Potencia y Balance de Baterías

Software de análisis de infraestructura diseñado para automatizar el cálculo del balance neto de energía en sistemas de respaldo (UPS) de centros de datos, procesando registros de potencia variable (positivos y negativos) a lo largo del tiempo.

---

## 🏗️ Arquitectura del Pipeline Numérico

El sistema procesa la información en dos etapas secuenciales basadas en métodos numéricos exactos y eficientes:

1. **Obtención de la Función de Potencia ($f(t)$):**
   * A partir de $n$ puntos de datos obtenidos por sensores de monitoreo de potencia neta en kilovatios ($\text{kW}$) —donde los valores positivos indican carga o consumo de red y los negativos indican descarga del banco de baterías—, se plantea un sistema de ecuaciones polinómicas.
   * Se aplica el **Método de Montante** para resolver el sistema lineal de manera exacta, evitando errores de punto flotante y manejando con precisión coeficientes con valores mixtos.

2. **Cálculo Integral del Balance Neto de Energía:**
   * Utilizando la función continua $f(t)$ obtenida en la fase anterior, se calcula el acumulado neto de energía en un intervalo de tiempo $[t_1, t_2]$:
     $$\text{Energía Neta} = \int_{t_1}^{t_2} f(t) \, dt$$
   * Se implementan algoritmos de **Integración Numérica** (Regla del Trapecio o Simpson 1/3) para aproximar el área neta bajo la curva, integrando de forma natural los cambios de signo (las áreas superiores suman energía al sistema y las inferiores restan reservas).

---

## 🛠️ Tecnologías y Métodos
* **Lenguaje:** Python 3.x
* **Matemática Aplicada:** Álgebra lineal exacta (Algoritmo de Montante) y cálculo numérico (Integración definida con signo).
* **Paradigmas:** Programación modular orientada al análisis de infraestructura crítica.

---

## 🚀 Uso Rápido

```python
# Ejemplo de inicialización del pipeline analítico
from smartgrid_ups import UPSFlowModel

# 1. Cargar mediciones de sensores (tiempo en horas, potencia en kW - positivo/negativo)
puntos = [(2, 40.0), (6, -25.0), (10, 10.0)]

# 2. Resolver coeficientes mediante el Método de Montante
modelo = UPSFlowModel(puntos)
funcion_potencia = modelo.resolver_montante()

# 3. Calcular el balance neto de energía mediante integración numérica
energia_neta = modelo.calcular_integral(t_inicio=0, t_end=12, metodo="simpson_13")
print(f"Balance neto de energía: {energia_neta} kWh")
