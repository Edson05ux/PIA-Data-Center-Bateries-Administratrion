"""Integración numérica mediante la regla compuesta del trapecio."""

from fractions import Fraction


def regla_del_trapecio(funcion, limite_inferior, limite_superior, numero_trapecios):
    """Aproxima la integral definida con la regla compuesta del trapecio."""
    if numero_trapecios <= 0:
        raise ValueError("El número de trapecios debe ser mayor que cero.")

    inferior = Fraction(limite_inferior)
    superior = Fraction(limite_superior)
    ancho = (superior - inferior) / numero_trapecios

    suma = funcion(inferior) + funcion(superior)
    for i in range(1, numero_trapecios):
        suma += 2 * funcion(inferior + i * ancho)
    return suma * ancho / 2
