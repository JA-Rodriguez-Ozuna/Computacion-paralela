/* ============================================================
   checkpoint_mpi.c
   Tolerancia a Fallos: Checkpoint y Rollback Recovery con MPI

   Compilar:
     gcc -O2 checkpoint_mpi.c -o checkpoint.exe ^
       -I"C:\Program Files (x86)\Microsoft SDKs\MPI\Include" ^
       -L"C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64" ^
       -lmsmpi

   Ejecucion 1 (primera vez, simula fallo):
     mpiexec -n 4 .\checkpoint.exe

   Ejecucion 2 (recuperacion desde checkpoint):
     mpiexec -n 4 .\checkpoint.exe
   ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

/* ── Configuracion ──────────────────────────────────────────── */
#define N_ITERACIONES  20      /* iteraciones totales del bucle */
#define FALLO_EN       10      /* simular fallo en iteracion 10 */
#define CKPT_INTERVALO  5      /* guardar checkpoint cada 5 iter */
#define TAM_VECTOR     100     /* tamano del vector de trabajo   */

/* ── Estructura del estado a guardar en checkpoint ─────────── */
typedef struct {
    int    iteracion;              /* progreso actual            */
    double suma_parcial;           /* acumulado hasta ahora      */
    double vector[TAM_VECTOR];     /* estado del vector de datos */
} Estado;

/* ── Nombre del archivo de checkpoint por proceso ──────────── */
void nombre_ckpt(int rank, char* buf, int sz) {
    snprintf(buf, sz, "checkpoint_proc%d.bin", rank);
}

/* ── Guardar checkpoint en disco ────────────────────────────── */
void guardar_checkpoint(int rank, const Estado* e) {
    char nombre[64];
    nombre_ckpt(rank, nombre, sizeof(nombre));
    FILE* f = fopen(nombre, "wb");
    if (!f) { fprintf(stderr, "[P%d] ERROR: no pudo crear checkpoint\n", rank); return; }
    fwrite(e, sizeof(Estado), 1, f);
    fclose(f);
    printf("[P%d] Checkpoint guardado — iteracion %d, suma=%.2f\n",
           rank, e->iteracion, e->suma_parcial);
    fflush(stdout);
}

/* ── Cargar checkpoint desde disco ─────────────────────────── */
int cargar_checkpoint(int rank, Estado* e) {
    char nombre[64];
    nombre_ckpt(rank, nombre, sizeof(nombre));
    FILE* f = fopen(nombre, "rb");
    if (!f) return 0;   /* no existe checkpoint */
    fread(e, sizeof(Estado), 1, f);
    fclose(f);
    printf("[P%d] Checkpoint encontrado — reanudando desde iteracion %d\n",
           rank, e->iteracion);
    fflush(stdout);
    return 1;
}

/* ── Inicializar vector con valores basados en rank ─────────── */
void inicializar_vector(double* v, int rank) {
    for (int i = 0; i < TAM_VECTOR; i++)
        v[i] = (double)(rank + 1) * (i + 1) * 0.1;
}

/* ════════════════════════════════════════════════════════════
   MAIN
   ════════════════════════════════════════════════════════════ */
int main(int argc, char* argv[]) {
    int rank, nprocs;
    Estado estado;
    int recuperado = 0;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    /* ── FASE 1: Detectar si existe checkpoint (Rollback) ──── */
    recuperado = cargar_checkpoint(rank, &estado);

    if (!recuperado) {
        /* Primera ejecucion: inicializar estado desde cero */
        estado.iteracion   = 0;
        estado.suma_parcial = 0.0;
        inicializar_vector(estado.vector, rank);

        if (rank == 0) {
            printf("\n===========================================\n");
            printf(" EJECUCION INICIAL (sin checkpoint previo)\n");
            printf(" Procesos: %d | Iteraciones: %d\n", nprocs, N_ITERACIONES);
            printf(" Fallo simulado en iteracion: %d\n", FALLO_EN);
            printf("===========================================\n\n");
            fflush(stdout);
        }
    } else {
        if (rank == 0) {
            printf("\n===========================================\n");
            printf(" RECUPERACION DESDE CHECKPOINT\n");
            printf(" Reanudando desde iteracion: %d\n", estado.iteracion);
            printf("===========================================\n\n");
            fflush(stdout);
        }
    }

    /* Sincronizar todos los procesos antes de empezar */
    MPI_Barrier(MPI_COMM_WORLD);

    /* ── FASE 2: Bucle computacional ────────────────────────── */
    int iter_inicio = estado.iteracion;

    for (int iter = iter_inicio; iter < N_ITERACIONES; iter++) {

        /* Computo: sumar elementos del vector */
        double suma_local = 0.0;
        for (int i = 0; i < TAM_VECTOR; i++) {
            estado.vector[i] += (double)(rank + 1) * 0.01;
            suma_local += estado.vector[i];
        }
        estado.suma_parcial += suma_local;
        estado.iteracion = iter + 1;

        printf("[P%d] Iteracion %2d completada — suma_parcial=%.2f\n",
               rank, iter + 1, estado.suma_parcial);
        fflush(stdout);

        /* ── CHECKPOINT COORDINADO cada CKPT_INTERVALO iter ── */
        if ((iter + 1) % CKPT_INTERVALO == 0) {

            /* Todos los procesos sincronizan antes del checkpoint */
            MPI_Barrier(MPI_COMM_WORLD);

            if (rank == 0) {
                printf("\n--- Checkpoint coordinado en iteracion %d ---\n\n",
                       iter + 1);
                fflush(stdout);
            }

            guardar_checkpoint(rank, &estado);

            /* Barrera post-checkpoint: todos confirmaron guardar */
            MPI_Barrier(MPI_COMM_WORLD);
        }

        /* ── SIMULAR FALLO en iteracion FALLO_EN ────────────── */
        if (!recuperado && (iter + 1) == FALLO_EN) {
            if (rank == 0) {
                printf("\n!!! FALLO SIMULADO en iteracion %d !!!\n", iter + 1);
                printf("    Reinicia con: mpiexec -n %d .\\checkpoint.exe\n\n",
                       nprocs);
                fflush(stdout);
            }
            MPI_Barrier(MPI_COMM_WORLD);
            MPI_Finalize();
            exit(1);   /* simular fallo abrupto */
        }
    }

    /* ── FASE 3: Reduccion final ────────────────────────────── */
    MPI_Barrier(MPI_COMM_WORLD);

    double suma_global = 0.0;
    MPI_Reduce(&estado.suma_parcial, &suma_global, 1,
               MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("\n===========================================\n");
        printf(" EJECUCION COMPLETADA\n");
        printf(" Suma global de todos los procesos: %.2f\n", suma_global);
        printf(" Iteraciones completadas: %d\n", N_ITERACIONES);
        printf("===========================================\n");
        fflush(stdout);
    }

    MPI_Finalize();
    return 0;
}