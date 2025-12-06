import subprocess
import os
import glob
import time
import sys

# Definicion de la carpeta donde he guardado los scripts individuales
CARPETA_SCRIPTS = "transformaciones"

print("--- INICIO DE LA EJECUCION GENERAL ---")
print(f"Escaneando carpeta: {CARPETA_SCRIPTS}...\n")

# 1. Busqueda automatica de scripts
# Utilizo glob para encontrar cualquier archivo .py dentro de la carpeta
ruta_busqueda = os.path.join(CARPETA_SCRIPTS, "*.py")
lista_scripts = glob.glob(ruta_busqueda)

# 2. Ordenacion alfabetica
# Esto es importante para mantener el orden logico:
# - generar_enlaces.py (va primero)
# - transformar_... (van despues)
# - validacion... (va al final)
lista_scripts.sort()

if not lista_scripts:
    print(f"[ERROR] No se han encontrado archivos .py en {CARPETA_SCRIPTS}")
    sys.exit()

print(f"Se han encontrado {len(lista_scripts)} scripts. Procedo a ejecutarlos en orden.\n")

inicio_tiempo = time.time()
errores = []

# 3. Bucle de ejecucion
for ruta_script in lista_scripts:
    nombre_archivo = os.path.basename(ruta_script)
    
    # Me salto archivos de sistema o init si los hubiera
    if nombre_archivo.startswith("__"):
        continue

    print(f"> Ejecutando: {nombre_archivo}...")

    try:
        # Lanzo el script usando el mismo interprete de Python actual
        resultado = subprocess.run(
            [sys.executable, ruta_script], 
            capture_output=True, 
            text=True
        )
        
        if resultado.returncode == 0:
            # Si el script termina bien, muestro la ultima linea de su salida
            lineas_salida = resultado.stdout.strip().splitlines()
            mensaje = lineas_salida[-1] if lineas_salida else "Finalizado correctamente."
            print(f"  [OK] {mensaje}")
        else:
            # Si el script falla, capturo el error y lo muestro
            print(f"  [FALLO] Error en {nombre_archivo}")
            print(f"  Detalle: {resultado.stderr.strip().splitlines()[-1]}")
            errores.append(nombre_archivo)
            
    except Exception as e:
        print(f"  [ERROR CRITICO] No se pudo lanzar {nombre_archivo}: {e}")
        errores.append(nombre_archivo)

# 4. Resumen final
print("\n" + "-"*40)
if not errores:
    print(f"EJECUCION COMPLETADA CON EXITO. Se han procesado {len(lista_scripts)} scripts.")
    print("Los resultados se han guardado en la carpeta 'archivos_ttl'.")
else:
    print(f"PROCESO FINALIZADO CON ERRORES ({len(errores)} fallos).")
    print(f"Revisar los scripts: {errores}")

tiempo_total = round(time.time() - inicio_tiempo, 2)
print(f"Tiempo total de ejecucion: {tiempo_total} segundos.")
print("-"*40)