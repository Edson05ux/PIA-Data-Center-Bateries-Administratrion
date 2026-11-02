import subprocess

todo = {"ajuste":["construir_sistema","resolver_coeficientes","evaluar_polinomio","formatear_polinomio"],"integracion":["regla_del_trapecio"],"menu":["_ingresar_mediciones","_leer_numero_trapecios","_mostrar_resultados","ejecutar_calculo","run"],"montante":["mostrar_matriz","_copiar","_hallar_pivote","eliminacion_montante","determinante","resolver_sistema","rango","resoluble"],"utils":["formatear_a_fraccion","_obtener_numero","leer_int","leer_fraccion","leer_opcion","formatear_a_decimal","borrar_consola","pausar"]}

for file in todo:
    for func in todo[file]:
        subprocess.run(["pyflowchart", f"../src/modules/{file}.py", "-o", f"{file}_{func}.html", "-f", func])