from fractions import Fraction

from modules.utils import formatear_a_fraccion


def mostrar_matriz(matriz: list = [], titulo: str = "Matriz"):
    if not matriz:
        print("  (Matriz vacía)")
        return
    filas = [[formatear_a_fraccion(valor) for valor in fila] for fila in matriz]
    columnas = len(filas[0])
    anchos = [
        max(len(filas[i][j]) for i in range(len(filas))) for j in range(columnas)
    ]
    print(f"--- {titulo} ---")
    for fila in filas:
        print("  " + "  ".join(cell.rjust(anchos[j]) for j, cell in enumerate(fila)))


def _copiar(matriz):
    return [fila[:] for fila in matriz]


def _hallar_pivote(matriz, k: int) -> bool:
    """Busca un pivote válido empezando en fila y columna k.

    Cambia filas si es necesario.

    Retorna False si toda la columna es 0 (matriz singular).
    """
    if matriz[k][k] != 0:
        return True
    for fila in range(k + 1, len(matriz)):
        if matriz[fila][k] != 0:
            matriz[k], matriz[fila] = matriz[fila], matriz[k]
            return True
    return False


def eliminacion_montante(aumentada):
    """Aplica el método de eliminación de Montante a la matriz aumentada.

    ValueError si algún pivote es 0 (sistema singular).
    """
    matriz = _copiar(aumentada)
    n = len(matriz)
    columnas = len(matriz[0]) if n else 0
    pivote_anterior = Fraction(1)
    for k in range(n):
        if not _hallar_pivote(matriz, k):
            raise ValueError(
                "El sistema es singular: pivote igual a cero en la etapa " f"{k + 1}"
            )
        pivote = matriz[k][k]
        for i in range(n):
            if i == k:
                continue
            for j in range(columnas):
                if j == k:
                    continue
                matriz[i][j] = (
                    pivote * matriz[i][j] - matriz[i][k] * matriz[k][j]
                ) / pivote_anterior
        pivote_anterior = pivote
    return matriz


def determinante(matriz):
    """Calcula el determinante usando el método de Montante."""
    n = len(matriz)
    if n == 0:
        return Fraction(0)
    matriz_temp = _copiar(matriz)
    signo = 1
    pivote_anterior = Fraction(1)
    for k in range(n - 1):
        if matriz_temp[k][k] == 0:
            matriz_temp_cambiada = _hallar_pivote(matriz_temp, k)
            if not matriz_temp_cambiada:
                return Fraction(0)
            signo = -signo
        pivote = matriz_temp[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                matriz_temp[i][j] = (
                    pivote * matriz_temp[i][j]
                    - matriz_temp[i][k] * matriz_temp[k][j]
                ) / pivote_anterior
        pivote_anterior = pivote
    return signo * matriz_temp[n - 1][n - 1]


def resolver_sistema(coeficientes, constantes):
    """Resuelve el sistema de ecuaciones con Montante.

    Retorna una lista de valores para cada incógnita.
    ValueError si no tiene solución única.
    """
    n = len(coeficientes)
    aumentada = [fila + [b] for fila, b in zip(coeficientes, constantes)]
    reducida = eliminacion_montante(aumentada)
    ultimo_pivote = reducida[n - 1][n - 1]
    if ultimo_pivote == 0:
        raise ValueError(
            "El sistema no tiene solución única (determinante igual a cero)"
        )
    return [reducida[i][n] / ultimo_pivote for i in range(n)]


def rango(matriz):
    """Auxiliar para saber qué tipo es una matriz con determinante 0."""
    matriz_temp = _copiar(matriz)
    n = len(matriz_temp)
    columnas = len(matriz_temp[0]) if n else 0
    fila_actual = 0
    for col in range(columnas):
        pivote_fila = None
        for i in range(fila_actual, n):
            if matriz_temp[i][col] != 0:
                pivote_fila = i
                break
        if pivote_fila is None:
            continue
        matriz_temp[fila_actual], matriz_temp[pivote_fila] = (
            matriz_temp[pivote_fila],
            matriz_temp[fila_actual],
        )
        pivote = matriz_temp[fila_actual][col]
        for j in range(col, columnas):
            matriz_temp[fila_actual][j] /= pivote
        for i in range(n):
            if i != fila_actual and matriz_temp[i][col] != 0:
                factor = matriz_temp[i][col]
                for j in range(col, columnas):
                    matriz_temp[i][j] -= factor * matriz_temp[fila_actual][j]
        fila_actual += 1
        if fila_actual == n:
            break
    return fila_actual


def resoluble(coeficientes, constantes):
    """Verifica si el sistema es resoluble.

    Retorna una tupla (es_resoluble, descripción).
    """
    aumentada = [fila + [b] for fila, b in zip(coeficientes, constantes)]
    if determinante(coeficientes) != 0:
        return True, (
            "Sistema compatible determinado: solución única "
            "(determinante distinto de cero)."
        )
    rango_a = rango(coeficientes)
    rango_ab = rango(aumentada)
    if rango_a == rango_ab:
        return True, (
            "Sistema compatible indeterminado: tiene infinitas soluciones "
            "(determinante cero, rangos iguales)."
        )
    return False, (
        "Sistema incompatible: no tiene solución "
        "(determinante cero y rangos distintos)."
    )
