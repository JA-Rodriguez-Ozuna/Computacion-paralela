/* ============================================================
   metricas_rendimiento.c
   Analisis de Metricas de Rendimiento con OpenMP
   Speedup, Eficiencia y Ley de Amdahl

   Compilar:  gcc -O2 -fopenmp metricas_rendimiento.c -o metricas.exe
   Ejecutar:  .\metricas.exe
   ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define TAM_ARREGLO  100000000   /* 100 millones de elementos */
#define REPETICIONES 5           /* promedio de 5 ejecuciones */

/* ── Suma secuencial (baseline T1) ─────────────────────────── */
long long suma_secuencial(int* arr, int n) {
    long long suma = 0;
    for (int i = 0; i < n; i++)
        suma += arr[i];
    return suma;
}

/* ── Suma paralela con OpenMP ──────────────────────────────── */
long long suma_paralela(int* arr, int n, int num_hilos) {
    long long suma = 0;
    omp_set_num_threads(num_hilos);

    #pragma omp parallel for reduction(+:suma)
    for (int i = 0; i < n; i++)
        suma += arr[i];

    return suma;
}

/* ── Main ──────────────────────────────────────────────────── */
int main() {
    int hilos[] = {1, 2, 4, 8, 16};
    int num_configs = 5;

    /* Reservar e inicializar arreglo */
    int* arr = (int*)malloc(TAM_ARREGLO * sizeof(int));
    if (!arr) {
        printf("Error: no se pudo reservar memoria\n");
        return 1;
    }

    srand(42);
    for (int i = 0; i < TAM_ARREGLO; i++)
        arr[i] = rand() % 100 + 1;

    printf("========================================\n");
    printf(" METRICAS DE RENDIMIENTO - OpenMP\n");
    printf(" Arreglo: %d elementos\n", TAM_ARREGLO);
    printf(" Nucleos: %d\n", omp_get_max_threads());
    printf(" Repeticiones: %d (promedio)\n", REPETICIONES);
    printf("========================================\n\n");

    /* --- Medicion secuencial (T1) --- */
    double t_seq = 0.0;
    long long resultado_seq = 0;

    for (int r = 0; r < REPETICIONES; r++) {
        double t1 = omp_get_wtime();
        resultado_seq = suma_secuencial(arr, TAM_ARREGLO);
        double t2 = omp_get_wtime();
        t_seq += (t2 - t1);
    }
    t_seq /= REPETICIONES;

    printf("Tiempo secuencial (T1): %.6f s\n", t_seq);
    printf("Suma verificacion:      %lld\n\n", resultado_seq);

    /* --- Encabezado de tabla --- */
    printf("%-8s %-14s %-10s %-12s\n",
           "Hilos", "Tiempo (s)", "Speedup", "Eficiencia");
    printf("----------------------------------------------\n");

    /* --- Medicion paralela para cada configuracion --- */
    for (int c = 0; c < num_configs; c++) {
        int p = hilos[c];
        double t_par = 0.0;
        long long resultado_par = 0;

        for (int r = 0; r < REPETICIONES; r++) {
            double t1 = omp_get_wtime();
            resultado_par = suma_paralela(arr, TAM_ARREGLO, p);
            double t2 = omp_get_wtime();
            t_par += (t2 - t1);
        }
        t_par /= REPETICIONES;

        double speedup    = t_seq / t_par;
        double eficiencia = speedup / p;

        printf("%-8d %-14.6f %-10.2f %-12.2f%%\n",
               p, t_par, speedup, eficiencia * 100);

        /* Verificar resultado correcto */
        if (resultado_par != resultado_seq)
            printf("  ADVERTENCIA: resultado incorrecto!\n");
    }

    /* --- Ley de Amdahl --- */
    double f = 0.95;  /* fraccion paralelizable estimada (95%) */

    printf("\n========================================\n");
    printf(" LEY DE AMDAHL (f = %.0f%% paralelizable)\n", f * 100);
    printf("========================================\n");
    printf("%-8s %-16s\n", "Hilos", "Speedup teorico");
    printf("---------------------------\n");

    for (int c = 0; c < num_configs; c++) {
        int p = hilos[c];
        double sp_teorico = 1.0 / ((1.0 - f) + f / p);
        printf("%-8d %-16.2f\n", p, sp_teorico);
    }
    printf("Limite (p->inf): %.2f\n", 1.0 / (1.0 - f));

    free(arr);
    printf("\nPrograma finalizado.\n");
    return 0;
}