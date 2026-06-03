/*
 * mpi_punto_a_punto.c
 * Actividad de Programacion: Comunicacion Punto a Punto con MPI
 * Semana 4 - Programacion Paralela
 *
 * Compilar: mpicc -o mpi_punto_a_punto mpi_punto_a_punto.c
 * Ejecutar:  mpirun -np 2 ./mpi_punto_a_punto
 */

#include <stdio.h>
#include <mpi.h>

int main(int argc, char *argv[]) {

    int rank;       /* Identificador del proceso actual */
    int size;       /* Numero total de procesos         */
    int valor = 0;  /* Variable a enviar/recibir        */
    MPI_Status status; /* Estado de la operacion MPI_Recv */

    /* -------------------------------------------------------
     * 1. INICIALIZACION DEL ENTORNO MPI
     * ------------------------------------------------------- */
    MPI_Init(&argc, &argv);

    /* Obtener el identificador (rango) del proceso actual */
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    /* Obtener el numero total de procesos en el comunicador */
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    /* Verificar que se ejecutan exactamente 2 procesos */
    if (size != 2) {
        if (rank == 0) {
            fprintf(stderr,
                "Error: Este programa requiere exactamente 2 procesos.\n"
                "Ejecutar con: mpirun -np 2 ./mpi_punto_a_punto\n");
        }
        MPI_Finalize();
        return 1;
    }

    /* -------------------------------------------------------
     * 2. COMUNICACION PUNTO A PUNTO
     * ------------------------------------------------------- */
    if (rank == 0) {
        /* --- PROCESO EMISOR (rank 0) --- */
        valor = 100;   /* Definir el valor a enviar */

        printf("[Proceso %d] Enviando valor %d al proceso 1...\n",
               rank, valor);

        /*
         * MPI_Send(buffer, count, datatype, dest, tag, comm)
         *   buffer   -> direccion de la variable a enviar
         *   count    -> numero de elementos (1 entero)
         *   datatype -> tipo MPI (MPI_INT)
         *   dest     -> proceso destino (1)
         *   tag      -> etiqueta del mensaje (0)
         *   comm     -> comunicador (MPI_COMM_WORLD)
         */
        MPI_Send(&valor, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);

        printf("[Proceso %d] Valor enviado correctamente.\n", rank);

    } else if (rank == 1) {
        /* --- PROCESO RECEPTOR (rank 1) --- */

        /*
         * MPI_Recv(buffer, count, datatype, source, tag, comm, status)
         *   buffer   -> direccion donde almacenar el mensaje recibido
         *   count    -> numero maximo de elementos esperados
         *   datatype -> tipo MPI (MPI_INT)
         *   source   -> proceso origen (0); MPI_ANY_SOURCE para cualquiera
         *   tag      -> etiqueta del mensaje esperado (0)
         *   comm     -> comunicador (MPI_COMM_WORLD)
         *   status   -> informacion sobre el mensaje recibido
         */
        MPI_Recv(&valor, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, &status);

        printf("[Proceso %d] Valor recibido: %d  (enviado por el proceso %d)\n",
               rank, valor, status.MPI_SOURCE);
    }

    /* -------------------------------------------------------
     * 3. FINALIZACION DEL ENTORNO MPI
     * ------------------------------------------------------- */
    MPI_Finalize();

    return 0;
}