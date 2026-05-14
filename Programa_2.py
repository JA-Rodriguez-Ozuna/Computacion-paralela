# Programa 2: Paralelismo real con multiprocessing
# Calcula números primos en rangos usando múltiples procesos
 
import multiprocessing
import time
import math
 
def es_primo(n):
    """Verifica si n es primo."""
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True
 
def contar_primos_en_rango(rango):
    inicio, fin = rango
    cantidad = sum(1 for n in range(inicio, fin) if es_primo(n))
    pid = multiprocessing.current_process().pid
    print(f'  [PID {pid}] Rango {inicio}-{fin}: {cantidad} primos')
    return cantidad
 
if __name__ == '__main__':
    LIMITE = 1_000_000
    NUM_PROCESOS = multiprocessing.cpu_count()
    tamano = LIMITE // NUM_PROCESOS
    rangos = [(i*tamano, (i+1)*tamano) for i in range(NUM_PROCESOS)]
 
    print(f'Contando primos hasta {LIMITE:,} con {NUM_PROCESOS} procesos...')
 
    inicio = time.time()
    total_seq = sum(contar_primos_en_rango(r) for r in rangos)
    t_seq = time.time() - inicio
 
    inicio = time.time()
    with multiprocessing.Pool(processes=NUM_PROCESOS) as pool:
        resultados = pool.map(contar_primos_en_rango, rangos)
    total_par = sum(resultados)
    t_par = time.time() - inicio
 
    print(f'Total primos: {total_seq:,}')
    print(f'Tiempo secuencial: {t_seq:.2f}s')
    print(f'Tiempo paralelo:   {t_par:.2f}s')
    print(f'Speedup real:      {t_seq/t_par:.2f}x')
