# Programa 1: Concurrencia con threading
# Simula descarga paralela de múltiples archivos
 
import threading
import time
import random
 
def descargar_archivo(nombre, tamano_mb):
    """Simula la descarga de un archivo (tarea I/O-bound)."""
    tiempo_descarga = tamano_mb * 0.1 + random.uniform(0.1, 0.5)
    print(f'  [{threading.current_thread().name}] Iniciando: {nombre} ({tamano_mb} MB)')
    time.sleep(tiempo_descarga)
    print(f'  [{threading.current_thread().name}] Completado: {nombre} en {tiempo_descarga:.2f}s')
 
archivos = [
    ("dataset_grande.csv",  50),
    ("modelo_ia.pkl",       30),
    ("imagenes.zip",        80),
    ("reporte_anual.pdf",   10),
]
 
print('=== Descarga SECUENCIAL ===')
inicio = time.time()
for nombre, tam in archivos:
    descargar_archivo(nombre, tam)
print(f'Tiempo secuencial: {time.time()-inicio:.2f}s')
 
print('=== Descarga PARALELA con threading ===')
inicio = time.time()
hilos = []
for nombre, tam in archivos:
    hilo = threading.Thread(target=descargar_archivo, args=(nombre, tam),
                             name=f"Hilo-{nombre[:8]}")
    hilos.append(hilo)
    hilo.start()
 
for hilo in hilos:
    hilo.join()
 
print(f'Tiempo paralelo: {time.time()-inicio:.2f}s')
print("Speedup aproximado: ~4x menos tiempo")
