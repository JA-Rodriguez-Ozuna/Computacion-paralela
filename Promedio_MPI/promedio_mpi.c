/* ============================================================
   promedio_mpi.c
   Calculo de promedio distribuido con comunicaciones colectivas MPI
   Usa: MPI_Bcast, MPI_Reduce

   Compilar:  mpicc -O2 promedio_mpi.c -o promedio_mpi.exe
   Ejecutar:  mpiexec -n 4 .\promedio_mpi.exe
   ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>

int main(int argc, char* argv[]) {
    int    rank, nprocs, N;
    double suma_local = 0.0;
    double suma_total = 0.0;
    double promedio   = 0.0;

    /* 1. Inicializar entorno MPI */
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    /* 2. Solo el proceso 0 solicita N al usuario */
    if (rank == 0) {
        printf("===========================================\n");
        printf(" MPI AVANZADO - Comunicaciones Colectivas\n");
        printf(" Procesos activos: %d\n", nprocs);
        printf("===========================================\n");
        printf("Ingrese N (cantidad de valores por proceso): ");
        fflush(stdout);
        scanf("%d", &N);
    }

    /* 3. Broadcast: proceso 0 distribuye N a todos */
    MPI_Bcast(&N, 1, MPI_INT, 0, MPI_COMM_WORLD);
    printf("[Proceso %d] N recibido = %d\n", rank, N);
    fflush(stdout);

    /* 4. Cada proceso genera N valores aleatorios y suma localmente */
    srand((unsigned int)(time(NULL) + rank * 1000));  /* semilla unica por proceso */

    for (int i = 0; i < N; i++) {
        double valor = (double)(rand() % 1000) / 10.0;  /* valores entre 0.0 y 99.9 */
        suma_local += valor;
    }

    printf("[Proceso %d] Suma local = %.2f  (promedio local = %.2f)\n",
           rank, suma_local, suma_local / N);
    fflush(stdout);

    /* Pequeña espera para que los prints no se mezclen */
    MPI_Barrier(MPI_COMM_WORLD);

    /* 5. Reduccion: sumar todas las sumas locales en el proceso 0 */
    MPI_Reduce(&suma_local,   /* dato de entrada (cada proceso) */
               &suma_total,   /* dato de salida (solo proceso 0) */
               1,             /* cantidad de elementos */
               MPI_DOUBLE,    /* tipo de dato */
               MPI_SUM,       /* operacion: sumar */
               0,             /* proceso raiz que recibe el resultado */
               MPI_COMM_WORLD);

    /* 6. Proceso 0 calcula el promedio total */
    if (rank == 0) {
        promedio = suma_total / ((double)N * nprocs);

        printf("\n-------------------------------------------\n");
        printf("[Proceso 0] Suma total   = %.2f\n", suma_total);
        printf("[Proceso 0] Total valores= %d  (%d procs x %d valores)\n",
               N * nprocs, nprocs, N);
        printf("[Proceso 0] Promedio     = %.4f\n", promedio);
        printf("-------------------------------------------\n\n");
        fflush(stdout);
    }

    /* 7. Broadcast: proceso 0 distribuye el promedio a todos */
    MPI_Bcast(&promedio, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    /* 8. Cada proceso imprime el promedio recibido */
    printf("[Proceso %d] Promedio recibido = %.4f\n", rank, promedio);
    fflush(stdout);

    /* 9. Finalizar MPI */
    MPI_Finalize();
    return 0;
}