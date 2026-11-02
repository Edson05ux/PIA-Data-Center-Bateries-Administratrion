# PIA-Data-Center-Bateries-Administratrion
# CloudTraffic Analytics: Cálculo de Ancho de Banda y Transferencia de Datos

Software de análisis e infraestructura diseñado para automatizar el cálculo del volumen de datos transferidos en servidores en la nube a partir de registros dispersos de velocidad[cite: 2].

---

## 🏗️ Arquitectura del Pipeline Numérico

El sistema procesa la información en dos etapas secuenciales basadas en métodos numéricos exactos y eficientes:

1. **Obtención de la Función de Tráfico ($f(t)$)[cite: 2]:**
   * A partir de $n$ puntos de datos obtenidos por sensores de monitoreo de velocidad (Mbps) a lo largo del tiempo, se plantea un sistema de ecuaciones polinómicas (ajustado mediante una matriz de Vandermonde)[cite: 2].
   * Se aplica el **Método de Montante** para resolver el sistema lineal de manera exacta, evitando errores de redondeo por punto flotante y manejando coeficientes con valores mixtos (positivos y negativos)[cite: 2].

2. **Cálculo Integral del Volumen Total de Datos[cite: 2]:**
   * Utilizando la función continua $f(t)$ obtenida en la fase anterior, se calcula el acumulado de transferencia de datos en un intervalo de tiempo $[t_1, t_2]$[cite: 2]:
     $$\text{Total de Datos} = \int_{t_1}^{t_2} f(t) \, dt$$
   * Se implementan algoritmos de **Integración Numérica** (Regla del Trapecio, Simpson 1/3 o Romberg) para aproximar el área bajo la curva de forma eficiente, integrando de manera nativa los cambios de signo en flujos netos positivos y negativos[cite: 2].

---

## 🛠️ Tecnologías y Métodos
* **Lenguaje:** Python 3.x
* **Matemática Aplicada:** Álgebra lineal exacta (Algoritmo de Montante) y cálculo numérico (Integración definida).
* **Paradigmas:** Programación modular orientada al procesamiento analítico de infraestructura.

---

## 🚀 Uso Rápido

```python
# Ejemplo de inicialización del pipeline analítico
from cloud_traffic import CloudTrafficModel

# 1. Cargar mediciones de sensores (tiempo, velocidad en Mbps)
puntos = [(0, 15.5), (4, -8.2), (8, 22.1)]

# 2. Resolver coeficientes mediante el Método de Montante
modelo = CloudTrafficModel(puntos)
funcion_trafico = modelo.resolver_montante()

# 3. Calcular la transferencia total en un intervalo de tiempo mediante integración numérica
volumen_total = modelo.calcular_integral(t_inicio=0, t_end=12, metodo="simpson_13")
print(f"Volumen total transferido: {volumen_total} GB")
