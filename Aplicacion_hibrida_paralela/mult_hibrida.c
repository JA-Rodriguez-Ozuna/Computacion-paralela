/* ============================================================
   mult_hibrida.c
   Multiplicacion de matrices hibrida MPI + OpenMP

   Compilar:  mpicc -O2 -fopenmp mult_hibrida.c -o mult_hibrida
   Ejecutar:  mpirun -np 4 ./mult_hibrida.exe

   Requisitos:
     - Compilador MPI (mpicc): instalar MS-MPI o OpenMPI
     - Soporte OpenMP: flag -fopenmp (GCC) o /openmp (MSVC)

   Nota: N debe ser divisible entre el numero de procesos MPI.
   ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>
#include <omp.h>

#define N 1024  /* dimension de las matrices NxN */

/* ── Reservar matriz contigua en memoria ───────────────────── */
double* crear_matriz(int filas, int cols) {
    double* M = (double*)calloc(filas * cols, sizeof(double));
    if (!M) {
        fprintf(stderr, "Error: no se pudo reservar memoria\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }
    return M;
}

/* ── Inicializar con valores aleatorios ────────────────────── */
void llenar_matriz(double* M, int filas, int cols) {
    for (int i = 0; i < filas * cols; i++)
        M[i] = (double)(rand() % 10 + 1);
}

/* ── Verificar resultado comparando una celda ──────────────── */
double verificar_celda(double* A, double* B, int fila, int col, int n) {
    double suma = 0.0;
    for (int k = 0; k < n; k++)
        suma += A[fila * n + k] * B[k * n + col];
    return suma;
}

/* ── Main ──────────────────────────────────────────────────── */
int main(int argc, char* argv[]) {
    int rank, nprocs;
    double t_inicio, t_fin;

    /* 1. Inicializar MPI */
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    /* Verificar que N sea divisible entre los procesos */
    if (N % nprocs != 0) {
        if (rank == 0)
            printf("Error: N (%d) debe ser divisible entre nprocs (%d)\n",
                   N, nprocs);
        MPI_Finalize();
        return 1;
    }

    int filas_local = N / nprocs;

    /* Matrices completas (solo proceso 0 las necesita) */
    double* A = NULL;
    double* C = NULL;

    /* B la necesitan todos los procesos */
    double* B = crear_matriz(N, N);

    /* Submatrices locales para cada proceso */
    double* A_local = crear_matriz(filas_local, N);
    double* C_local = crear_matriz(filas_local, N);

    /* Proceso 0: inicializar matrices A y B */
    if (rank == 0) {
        A = crear_matriz(N, N);
        C = crear_matriz(N, N);

        srand(42);
        llenar_matriz(A, N, N);
        llenar_matriz(B, N, N);

        printf("================================================\n");
        printf(" MULTIPLICACION DE MATRICES HIBRIDA MPI+OpenMP\n");
        printf("================================================\n");
        printf(" Dimension      : %d x %d\n", N, N);
        printf(" Procesos MPI   : %d\n", nprocs);
        printf(" Hilos OpenMP   : %d (por proceso)\n", omp_get_max_threads());
        printf(" Filas/proceso  : %d\n", filas_local);
        printf("================================================\n\n");
    }

    /* Sincronizar antes de medir tiempo */
    MPI_Barrier(MPI_COMM_WORLD);
    t_inicio = MPI_Wtime();

    /* 2. Distribuir filas de A entre procesos */
    MPI_Scatter(A,                       /* buffer de envio (solo proceso 0) */
                filas_local * N,         /* elementos por proceso */
                MPI_DOUBLE,              /* tipo de dato */
                A_local,                 /* buffer de recepcion (cada proceso) */
                filas_local * N,         /* elementos a recibir */
                MPI_DOUBLE,
                0,                       /* proceso root */
                MPI_COMM_WORLD);

    /* Enviar B completa a todos los procesos */
    MPI_Bcast(B,                         /* buffer */
              N * N,                     /* cantidad de elementos */
              MPI_DOUBLE,
              0,                         /* proceso root */
              MPI_COMM_WORLD);

    /* 3. Multiplicacion local con OpenMP */
    #pragma omp parallel for collapse(2) schedule(static)
    for (int i = 0; i < filas_local; i++) {
        for (int j = 0; j < N; j++) {
            double suma = 0.0;
            for (int k = 0; k < N; k++) {
                suma += A_local[i * N + k] * B[k * N + j];
            }
            C_local[i * N + j] = suma;
        }
    }

    /* 4. Recopilar resultados parciales en proceso 0 */
    MPI_Gather(C_local,                  /* buffer de envio (cada proceso) */
               filas_local * N,          /* elementos por proceso */
               MPI_DOUBLE,
               C,                        /* buffer de recepcion (solo proceso 0) */
               filas_local * N,
               MPI_DOUBLE,
               0,                        /* proceso root */
               MPI_COMM_WORLD);

    /* Sincronizar antes de parar el reloj */
    MPI_Barrier(MPI_COMM_WORLD);
    t_fin = MPI_Wtime();

    /* 5. Mostrar resultados (solo proceso 0) */
    if (rank == 0) {
        double tiempo = t_fin - t_inicio;
        double gflops = (2.0 * N * N * N) / (tiempo * 1e9);

        printf("Tiempo total    : %.4f s\n", tiempo);
        printf("Rendimiento     : %.2f GFLOPS\n", gflops);

        /* Verificacion de resultado */
        double esperado_00   = verificar_celda(A, B, 0, 0, N);
        double esperado_NN   = verificar_celda(A, B, N-1, N-1, N);
        double obtenido_00   = C[0];
        double obtenido_NN   = C[(N-1)*N + (N-1)];

        printf("\nVerificacion:\n");
        printf("  C[0][0]     = %.1f (esperado: %.1f) %s\n",
               obtenido_00, esperado_00,
               (obtenido_00 == esperado_00) ? "OK" : "ERROR");
        printf("  C[%d][%d] = %.1f (esperado: %.1f) %s\n",
               N-1, N-1, obtenido_NN, esperado_NN,
               (obtenido_NN == esperado_NN) ? "OK" : "ERROR");

        free(A);
        free(C);
    }

    /* Liberar memoria */
    free(A_local);
    free(B);
    free(C_local);

    MPI_Finalize();
    return 0;
}