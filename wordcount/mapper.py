#!/usr/bin/env python3
# Mapper: lee líneas, tokeniza palabras y emite (palabra, 1)
import sys
import re

for linea in sys.stdin:
    linea = linea.strip().lower()
    palabras = re.findall(r'[a-zA-Z]+', linea)
    for palabra in palabras:
        print(f"{palabra}\t1")