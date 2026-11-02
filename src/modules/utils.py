import os
import sys
from decimal import Decimal, InvalidOperation
from fractions import Fraction


def formatear_a_fraccion(valor) -> str:
    """Convierte un número a su representación como fracción a/b."""
    valor = Fraction(valor)
    return str(valor)


def _obtener_numero(texto):
    """Retorna una fracción exacta a partir del número ingresado.

    ValueError si el valor no es válido.
    """
    texto = str(texto).strip()
    if not texto:
        raise ValueError("Entrada vacía: se esperaba un número")
    try:
        return Fraction(int(texto))
    except ValueError:
        pass
    try:
        decimal = Decimal(texto)
        if not decimal.is_finite():
            raise ValueError(f'"{texto}" no es un número finito válido')
        return Fraction(decimal)
    except InvalidOperation:
        raise ValueError(f'"{texto}" no es un número entero ni flotante válido')


def leer_int(prompt: str):
    """Lee un entero positivo."""
    while True:
        entrada = input(prompt).strip()
        try:
            value = int(entrada)
            if value <= 0:
                print("Debe ser un número entero positivo. Intenta de nuevo.")
                continue
            return value
        except ValueError:
            print(f'"{entrada}" no es un número entero válido. Intenta de nuevo.')


def leer_fraccion(prompt: str):
    """Lee un entero o decimal y lo regresa como Fraction."""
    while True:
        entrada = input(prompt).strip()
        try:
            return _obtener_numero(entrada)
        except ValueError as error:
            print(f"Entrada inválida: {error}. Intenta de nuevo.")


def leer_opcion(prompt: str, lower: int, upper: int) -> int:
    """Lee un entero dentro del rango cerrado [lower, upper]."""
    while True:
        entrada = input(prompt).strip()
        try:
            valor = int(entrada)
            if lower <= valor <= upper:
                return valor
            print(f"Opción fuera de rango (se esperaba entre {lower} y {upper}).")
        except ValueError:
            print(f'"{entrada}" no es un número entero válido.')


def formatear_a_decimal(valor) -> str:
    """Fracción, cadena u objeto Decimal a representación decimal."""
    texto = f"{float(valor):.6f}".rstrip("0").rstrip(".")
    return texto if texto not in ("", "-") else "0"


def borrar_consola():
    """Borra la consola si la entrada es una terminal interactiva."""
    if not sys.stdin.isatty():
        return
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """Simula el comportamiento de pause en cmd."""
    if not sys.stdin.isatty():
        return
    if os.name == "nt":
        os.system("pause")
    else:
        input("Presiona Enter para continuar...")
