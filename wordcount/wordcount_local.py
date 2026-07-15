#!/usr/bin/env python3
"""
wordcount_local.py
Simulacion completa del flujo MapReduce: Map -> Shuffle -> Reduce
Con medicion de tiempos y variacion de reducers
"""
import re
import time
from collections import defaultdict

def mapper(lineas):
    """FASE MAP: tokeniza cada linea y emite (palabra, 1)"""
    pares = []
    for linea in lineas:
        linea = linea.strip().lower()
        palabras = re.findall(r'[a-zA-Z]+', linea)
        for palabra in palabras:
            pares.append((palabra, 1))
    return pares

def shuffle_sort(pares):
    """FASE SHUFFLE: agrupa pares por clave (palabra)"""
    grupos = defaultdict(list)
    for palabra, valor in pares:
        grupos[palabra].append(valor)
    return dict(sorted(grupos.items()))

def reducer(grupos, num_reducers=1):
    """FASE REDUCE: suma valores por palabra"""
    resultado = {}
    claves = list(grupos.keys())
    # Distribuir claves entre reducers
    particiones = [[] for _ in range(num_reducers)]
    for i, clave in enumerate(claves):
        particion = hash(clave) % num_reducers
        particiones[particion].append(clave)

    for particion in particiones:
        for clave in particion:
            resultado[clave] = sum(grupos[clave])
    return dict(sorted(resultado.items()))

def ejecutar_wordcount(archivo, num_reducers=1):
    print(f"\n{'='*50}")
    print(f" WordCount con {num_reducers} reducer(s)")
    print(f"{'='*50}")

    with open(archivo, 'r') as f:
        lineas = f.readlines()

    print(f" Lineas de entrada: {len(lineas)}")

    # MAP
    t1 = time.time()
    pares = mapper(lineas)
    t_map = time.time() - t1
    print(f" Pares emitidos   : {len(pares)}")
    print(f" Tiempo MAP       : {t_map:.6f} s")

    # SHUFFLE
    t2 = time.time()
    grupos = shuffle_sort(pares)
    t_shuffle = time.time() - t2
    print(f" Palabras unicas  : {len(grupos)}")
    print(f" Tiempo SHUFFLE   : {t_shuffle:.6f} s")

    # REDUCE
    t3 = time.time()
    resultado = reducer(grupos, num_reducers)
    t_reduce = time.time() - t3
    print(f" Tiempo REDUCE    : {t_reduce:.6f} s")

    t_total = t_map + t_shuffle + t_reduce
    print(f" Tiempo TOTAL     : {t_total:.6f} s")

    print(f"\n Resultado:")
    for palabra, conteo in resultado.items():
        print(f"   {palabra:<20} {conteo}")

    return t_total

# Ejecutar con 1, 2 y 4 reducers
t1 = ejecutar_wordcount("texto_entrada.txt", num_reducers=1)
t2 = ejecutar_wordcount("texto_entrada.txt", num_reducers=2)
t4 = ejecutar_wordcount("texto_entrada.txt", num_reducers=4)

print(f"\n{'='*50}")
print(f" COMPARACION DE RENDIMIENTO")
print(f"{'='*50}")
print(f" 1 reducer : {t1:.6f} s  (base)")
print(f" 2 reducers: {t2:.6f} s  (speedup: {t1/t2:.2f}x)")
print(f" 4 reducers: {t4:.6f} s  (speedup: {t1/t4:.2f}x)")