# PIA-Data-Center-Bateries-Administratrion
# SmartGrid UPS Flow: Control de Flujo de Potencia y Balance de Baterías

Sistema para calcular el consumo y almacenamiento neto de energía en las baterías de respaldo (UPS) de un centro de datos. Analiza cómo cambia la potencia a lo largo del tiempo, manejando tanto el consumo eléctrico como la recarga de las baterías (valores positivos y negativos).

---

## 🏗️ Estructura del Proceso

El programa realiza el cálculo en dos pasos consecutivos mediante métodos numéricos:

1. **Obtención de la Función de Potencia ($f(t)$):**
   * Se recopilan 3 mediciones reales de los sensores de potencia en kilovatios ($\text{kW}$):
     * **Valores positivos ($+$):** La red eléctrica alimenta el centro de datos o carga las baterías.
     * **Valores negativos ($-$):** Las baterías se están descargando para mantener el servidor activo.
   * Con estos puntos se arma un sistema de ecuaciones $3 \times 3$ de la forma $f(t) = at^2 + bt + c$.
   * Se resuelve el sistema usando el **Método de Montante**, obteniendo los coeficientes exactos de la función sin arrastrar errores de punto flotante ni fracciones complejas.

2. **Cálculo del Balance Neto de Energía (Integración Numérica):**
   * Con la función $f(t)$ definida, se calcula la energía total acumulada en un intervalo de tiempo $[t_1, t_2]$:
     $$\text{Energía Neta} = \int_{t_1}^{t_2} f(t) \, dt$$
   * Se aplica la **Regla de Simpson 1/3** (o Trapecio) para calcular el área bajo la curva. Los periodos de carga (área positiva) suman energía y los de descarga (área negativa) la restan de forma automática, entregando el balance final en $\text{kWh}$.

---

## 🛠️ Métodos Utilizados
* **Lenguaje:** Python 3.x
* **Álgebra Lineal:** Método de Montante (resolución exacta de matrices $3 \times 3$).
* **Cálculo Numérico:** Regla de Simpson 1/3 (integración definida con signos mixtos).

---

## 🚀 Ejemplo de Uso

```python
from smartgrid_ups import UPSFlowModel

# 1. Datos de los sensores: (tiempo en horas, potencia en kW)
# 40 kW cargando a las 2h, -25 kW descargando a las 6h, 10 kW cargando a las 10h
puntos = [(2, 40.0), (6, -25.0), (10, 10.0)]

# 2. Obtener la ecuación cuadrática con Montante
modelo = UPSFlowModel(puntos)
funcion_potencia = modelo.resolver_montante()

# 3. Calcular la energía neta entre t = 0 y t = 12 horas con Simpson 1/3
energia_neta = modelo.calcular_integral(t_inicio=0, t_fin=12, metodo="simpson_13")
print(f"Balance neto de energía: {energia_neta} kWh")
