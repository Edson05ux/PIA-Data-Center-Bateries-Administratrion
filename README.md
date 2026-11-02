# PIA-Data-Center-Bateries-Administratrion
SmartGrid UPS Analytics: Control de Flujo de Potencia y Balance Energético en Data CenterSoftware de análisis e infraestructura diseñado para calcular la ecuación del flujo de potencia continua y evaluar el balance energético neto en el sistema de almacenamiento de energía (UPS / Banco de Baterías) de un centro de datos.🏗️ Arquitectura del Pipeline NuméricoEl sistema procesa los registros de flujo eléctrico en dos etapas secuenciales basadas en métodos numéricos exactos:Obtención de la Función de Flujo de Potencia ($f(t)$):A partir de mediciones tomadas por sensores en instantes clave del día (potencia en $\text{kW}$ vs. tiempo en horas), se plantea un sistema de ecuaciones polinómicas mediante una matriz de Vandermonde.Se aplica el Método de Montante para resolver el sistema de ecuaciones de manera exacta con aritmética entera. Esto evita el arrastre de errores por punto flotante y procesa sin problemas valores mixtos:$f(t) > 0$ (Positivo): Red alimentando/cargando el sistema de baterías (Superávit).$f(t) < 0$ (Negativo): Baterías suministrando energía por picos de demanda o caída de red (Déficit/Descarga).Cálculo del Balance Neto de Energía ($\text{kWh}$):Utilizando la función polinómica $f(t)$ resultante, se determina el consumo o ganancia neta acumulada en un intervalo $[t_1, t_2]$ mediante integración definida:
$$\text{Balance de Energía} = \int_{t_1}^{t_2} f(t) \, dt$$Se aplica Integración Numérica (Regla de Simpson 1/3 / Trapecio) para evaluar el área neta con signo, donde las zonas de descarga restan y las de carga suman automáticamente al balance total.🛠️ Tecnologías y MétodosLenguaje: Python 3.xÁlgebra Lineal: Algoritmo de Montante (Determinantes para matriz de Vandermonde).Cálculo Numérico: Regla de Simpson 1/3 Compuesta y Método del Trapecio.Dominio: Gestión de energía en TI y sistemas críticos.🚀 Uso Rápidofrom ups_analytics import UPSPowerModel

# 1. Cargar mediciones de los sensores: (tiempo en horas, potencia neta en kW)
# Valores positivos = Carga, Valores negativos = Descarga
mediciones = [(2, 40.0), (6, -25.0), (10, 10.0)]

# 2. Obtener la ecuación continua f(t) mediante el Método de Montante
modelo = UPSPowerModel(mediciones)
coeficientes = modelo.resolver_montante()  # Devuelve a, b, c para f(t) = at² + bt + c

# 3. Calcular el balance neto de energía (kWh) en un rango mediante Integración Numérica
energia_neta = modelo.calcular_integral(t_inicio=0, t_fin=12, metodo="simpson_13")
print(f"Balance energético neto del periodo: {energia_neta:.2f} kWh")

