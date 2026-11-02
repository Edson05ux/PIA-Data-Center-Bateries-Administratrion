"""Ajuste del polinomio que pasa por las mediciones de potencia."""

from fractions import Fraction

from modules.montante import resolver_sistema
from modules.utils import formatear_a_fraccion


def construir_sistema(puntos):
    """Construye la matriz aumentada del sistema de Vandermonde.

    Cada punto (hora, potencia) aporta la ecuación
    a0 + a1*hora + a2*hora^2 + ... = potencia.
    """
    if len(puntos) < 2:
        raise ValueError("Se requieren al menos 2 mediciones para ajustar la función.")
    horas = [hora for hora, _ in puntos]
    if len(set(horas)) != len(horas):
        raise ValueError("Cada medición debe tener una hora distinta.")

    cantidad = len(puntos)
    aumentada = []
    for hora, potencia in puntos:
        fila = [Fraction(1)]
        for _ in range(1, cantidad):
            fila.append(fila[-1] * hora)
        aumentada.append(fila + [potencia])
    return aumentada


def resolver_coeficientes(aumentada):
    """Resuelve el sistema de Vandermonde con el método de Montante.

    Retorna los coeficientes de menor a mayor grado.
    """
    cantidad = len(aumentada)
    coeficientes = [fila[:cantidad] for fila in aumentada]
    constantes = [fila[cantidad] for fila in aumentada]
    return resolver_sistema(coeficientes, constantes)


def evaluar_polinomio(coeficientes, x):
    """Evalúa el polinomio con coeficientes de menor a mayor grado (Horner)."""
    resultado = Fraction(0)
    for coeficiente in reversed(coeficientes):
        resultado = resultado * x + coeficiente
    return resultado


def formatear_polinomio(coeficientes) -> str:
    """Devuelve el polinomio en texto, de mayor a menor grado."""
    terminos = []
    for grado in range(len(coeficientes) - 1, -1, -1):
        coeficiente = coeficientes[grado]
        if coeficiente == 0:
            continue

        signo = "-" if coeficiente < 0 else "+"
        magnitud = abs(coeficiente)

        if grado == 0:
            cuerpo = formatear_a_fraccion(magnitud)
        else:
            if magnitud == 1:
                factor = ""
            elif magnitud.denominator == 1:
                factor = str(magnitud.numerator)
            else:
                factor = f"({formatear_a_fraccion(magnitud)})"
            variable = "t" if grado == 1 else f"t^{grado}"
            cuerpo = f"{factor}{variable}"

        terminos.append((signo, cuerpo))

    if not terminos:
        return "0"

    primer_signo, primer_cuerpo = terminos[0]
    texto = ("-" if primer_signo == "-" else "") + primer_cuerpo
    for signo, cuerpo in terminos[1:]:
        texto += f" {signo} {cuerpo}"
    return texto
