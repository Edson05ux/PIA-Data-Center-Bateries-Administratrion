"""Menú interactivo para la administración de baterías de un centro de datos."""

from fractions import Fraction

from modules.ajuste import (
    construir_sistema,
    evaluar_polinomio,
    formatear_polinomio,
    resolver_coeficientes,
)
from modules.integracion import regla_del_trapecio
from modules.montante import mostrar_matriz
from modules.utils import (
    borrar_consola,
    formatear_a_decimal,
    formatear_a_fraccion,
    leer_fraccion,
    leer_int,
    leer_opcion,
    pausar,
)

HORA_INICIO = Fraction(0)
HORA_FIN = Fraction(24)


def _ingresar_mediciones():
    """Lee las mediciones de potencia y las ordena por hora."""
    print("\n--- Mediciones de potencia ---")
    print("Cada medición tiene una hora (0-23) y una potencia en kW.")
    print("Potencia positiva = carga (entrada); negativa = descarga (salida).\n")

    cantidad = leer_int("¿Cuántas mediciones deseas ingresar? (mínimo 3): ")
    while cantidad < 3:
        print("Debes ingresar al menos 3 mediciones para calcular el balance.")
        cantidad = leer_int("¿Cuántas mediciones deseas ingresar? (mínimo 3): ")

    puntos = []
    horas_usadas = set()
    for i in range(1, cantidad + 1):
        print(f"\nMedición {i}:")
        while True:
            hora = leer_opcion("  Hora (0-23): ", 0, 23)
            if hora not in horas_usadas:
                break
            print("  Ya existe una medición para esa hora. Ingresa otra hora.")
        horas_usadas.add(hora)
        potencia = leer_fraccion("  Potencia en kW (+ carga / - descarga): ")
        puntos.append((Fraction(hora), potencia))

    puntos.sort(key=lambda punto: punto[0])
    return puntos


def _leer_numero_trapecios():
    """Lee la cantidad de trapecios para la integración."""
    print("\n--- Integración numérica ---")
    print(
        f"Se integrará la potencia de {int(HORA_INICIO)} a {int(HORA_FIN)} h "
        "para obtener la energía neta del día.\n"
    )
    return leer_int(
        "¿Cuántos trapecios deseas usar? (más trapecios = mejor estimación): "
    )


def _mostrar_resultados(puntos, coeficientes, numero_trapecios, energia):
    """Muestra el ajuste polinomial y el balance neto de energía."""
    print("\n=== Resultados ===")

    print("\nPuntos registrados:")
    for hora, potencia in puntos:
        print(f"  Hora {int(hora)}: {formatear_a_decimal(potencia)} kW")

    print("\nCoeficientes del polinomio (de menor a mayor grado):")
    for i, coeficiente in enumerate(coeficientes):
        print(
            f"  a{i} = {formatear_a_fraccion(coeficiente)}"
            f" ≈ {formatear_a_decimal(coeficiente)}"
        )

    print("\nFunción de potencia ajustada:")
    print(f"  f(t) = {formatear_polinomio(coeficientes)}")

    ancho = (HORA_FIN - HORA_INICIO) / numero_trapecios
    print("\nIntegración con la regla del trapecio:")
    print(f"  Intervalo: {int(HORA_INICIO)} a {int(HORA_FIN)} h")
    print(f"  Trapecios: {numero_trapecios}")
    print(f"  Δt = {formatear_a_decimal(ancho)} h")
    print(
        f"  Energía neta = {formatear_a_fraccion(energia)} kWh"
        f" ≈ {formatear_a_decimal(energia)} kWh"
    )

    print("\nInterpretación del balance:")
    if energia > 0:
        print(
            f"  La batería terminó con {formatear_a_decimal(energia)} kWh más "
            "que su carga inicial (predominó la carga)."
        )
    elif energia < 0:
        print(
            f"  La batería terminó con {formatear_a_decimal(abs(energia))} kWh menos "
            "que su carga inicial (predominó la descarga)."
        )
    else:
        print("  La batería terminó con la misma carga que al inicio del día.")
    print("  El balance es el cambio neto respecto a la carga inicial (desconocida).")


def ejecutar_calculo():
    """Ejecuta el ajuste polinomial y la integración con datos del usuario."""
    puntos = _ingresar_mediciones()
    numero_trapecios = _leer_numero_trapecios()

    aumentada = construir_sistema(puntos)
    print("\n=== Ajuste polinomial con el método de Montante ===")
    mostrar_matriz(aumentada, "Sistema de ecuaciones (matriz aumentada)")

    coeficientes = resolver_coeficientes(aumentada)
    energia = regla_del_trapecio(
        lambda t: evaluar_polinomio(coeficientes, t),
        HORA_INICIO,
        HORA_FIN,
        numero_trapecios,
    )

    _mostrar_resultados(puntos, coeficientes, numero_trapecios, energia)


def run():
    """Método principal para ejecutar el menú."""
    while True:
        borrar_consola()
        print("=== Balance de energía en baterías de un centro de datos ===\n")
        print("Menú:")
        print("  1) Calcular balance de energía del día")
        print("  2) Salir")

        opcion = leer_opcion("Selecciona una opción (1-2): ", 1, 2)

        try:
            if opcion == 1:
                ejecutar_calculo()
            elif opcion == 2:
                print("¡Hasta luego!")
                break
        except ValueError as error:
            print(f"Error: {error}\n")
        except (KeyboardInterrupt, EOFError):
            print("\n¡Hasta luego!")
            break

        pausar()
