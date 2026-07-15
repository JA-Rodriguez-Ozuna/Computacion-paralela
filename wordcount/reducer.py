#!/usr/bin/env python3
# Reducer: agrupa por palabra y suma los conteos
import sys

palabra_actual = None
suma = 0

for linea in sys.stdin:
    linea = linea.strip()
    partes = linea.split('\t')
    if len(partes) != 2:
        continue
    palabra, conteo = partes[0], int(partes[1])

    if palabra == palabra_actual:
        suma += conteo
    else:
        if palabra_actual is not None:
            print(f"{palabra_actual}\t{suma}")
        palabra_actual = palabra
        suma = conteo

if palabra_actual is not None:
    print(f"{palabra_actual}\t{suma}")