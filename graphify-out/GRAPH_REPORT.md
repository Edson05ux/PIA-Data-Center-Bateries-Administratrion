# Graph Report - PIA-Data-Center-Bateries-Administratrion  (2026-11-01)

## Corpus Check
- Corpus is ~3,386 words - fits in a single context window. You may not need a graph.

## Summary
- 77 nodes · 146 edges · 8 communities (6 shown, 2 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.86)
- Token cost: 9,000 input · 2,500 output

## Community Hubs (Navigation)
- Consola y utilidades de E/S
- Interpolación polinomial (Vandermonde)
- Método de Montante
- Integración por trapecios
- Presentación de resultados
- Entrada de mediciones
- Entrada y ejecución

## God Nodes (most connected - your core abstractions)
1. `ejecutar_calculo()` - 11 edges
2. `formatear_a_fraccion()` - 9 edges
3. `Reutilización de código del Proyecto 1` - 8 edges
4. `resolver_coeficientes()` - 7 edges
5. `_ingresar_mediciones()` - 7 edges
6. `_mostrar_resultados()` - 7 edges
7. `run()` - 7 edges
8. `resolver_sistema()` - 7 edges
9. `leer_int()` - 6 edges
10. `leer_fraccion()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Balance neto de energía del día` --implements--> `_mostrar_resultados()`  [INFERRED]
  README.md → src/modules/menu.py
- `Aritmética exacta con Fraction` --rationale_for--> `resolver_coeficientes()`  [INFERRED]
  README.md → src/modules/ajuste.py
- `Convención de signo de potencia (+ carga / − descarga)` --shares_data_with--> `_ingresar_mediciones()`  [INFERRED]
  README.md → src/modules/menu.py
- `Sistema de Vandermonde` --implements--> `construir_sistema()`  [INFERRED]
  README.md → src/modules/ajuste.py
- `Interpolación polinomial de mediciones` --implements--> `resolver_coeficientes()`  [INFERRED]
  README.md → src/modules/ajuste.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Flujo de cálculo del balance de energía diario** — src_modules_menu_ingresar_mediciones, src_modules_ajuste_construir_sistema, src_modules_ajuste_resolver_coeficientes, src_modules_integracion_regla_del_trapecio, src_modules_menu_mostrar_resultados [INFERRED 0.85]
- **Funciones reutilizadas del Proyecto 1 en utils.py** — src_modules_utils_leer_int, src_modules_utils_leer_fraccion, src_modules_utils_leer_opcion, src_modules_utils_formatear_a_fraccion, src_modules_utils_formatear_a_decimal, src_modules_utils_borrar_consola, src_modules_utils_pausar [EXTRACTED 1.00]
- **Núcleo del método de Montante** — src_modules_montante_hallar_pivote, src_modules_montante_eliminacion_montante, src_modules_montante_resolver_sistema, src_modules_montante_mostrar_matriz [INFERRED 0.85]

## Communities (8 total, 2 thin omitted)

### Community 0 - "Consola y utilidades de E/S"
Cohesion: 0.20
Nodes (5): run(), borrar_consola(), formatear_a_decimal(), leer_opcion(), pausar()

### Community 1 - "Interpolación polinomial (Vandermonde)"
Cohesion: 0.17
Nodes (10): Extrapolación a horas sin medición, Fenómeno de Runge, Interpolación polinomial de mediciones, Método de Montante, Sistema de Vandermonde, construir_sistema(), evaluar_polinomio(), resolver_coeficientes() (+2 more)

### Community 2 - "Método de Montante"
Cohesion: 0.23
Nodes (7): _copiar(), determinante(), eliminacion_montante(), _hallar_pivote(), rango(), resoluble(), resolver_sistema()

### Community 3 - "Integración por trapecios"
Cohesion: 0.21
Nodes (5): Balance neto de energía del día, Regla compuesta del trapecio, regla_del_trapecio(), _leer_numero_trapecios(), leer_int()

### Community 4 - "Presentación de resultados"
Cohesion: 0.32
Nodes (3): formatear_polinomio(), _mostrar_resultados(), formatear_a_fraccion()

### Community 5 - "Entrada de mediciones"
Cohesion: 0.29
Nodes (4): Convención de signo de potencia (+ carga / − descarga), _ingresar_mediciones(), leer_fraccion(), _obtener_numero()

## Knowledge Gaps
- **3 isolated node(s):** `Fenómeno de Runge`, `Convención de signo de potencia (+ carga / − descarga)`, `Extrapolación a horas sin medición`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 35 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `resolver_coeficientes()` connect `Interpolación polinomial (Vandermonde)` to `Método de Montante`, `Integración por trapecios`, `Presentación de resultados`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `resolver_coeficientes()` (e.g. with `Aritmética exacta con Fraction` and `Interpolación polinomial de mediciones`) actually correct?**
  _`resolver_coeficientes()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Fenómeno de Runge`, `Convención de signo de potencia (+ carga / − descarga)`, `Extrapolación a horas sin medición` to the rest of the system?**
  _3 weakly-connected nodes found - possible missing edges._
- **Why does `ejecutar_calculo()` connect `Interpolación polinomial (Vandermonde)` to `Consola y utilidades de E/S`, `Integración por trapecios`, `Presentación de resultados`, `Entrada de mediciones`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `resolver_sistema()` connect `Método de Montante` to `Consola y utilidades de E/S`, `Interpolación polinomial (Vandermonde)`, `Presentación de resultados`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._