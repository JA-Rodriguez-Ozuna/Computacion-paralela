/* ============================================================
   vector_suma_hibrido.cu
   Suma de vectores: OpenMP (CPU) vs CUDA (GPU)

   Compilar:
     nvcc -Xcompiler -fopenmp vector_suma_hibrido.cu -o vector_suma.exe

   Ejecutar:
     .\vector_suma.exe

   Requisitos:
     - NVIDIA GPU con soporte CUDA
     - CUDA Toolkit instalado (nvcc en PATH)
     - MinGW con soporte OpenMP (-fopenmp)
   ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include <cuda_runtime.h>

#define N     1048576   /* 1M elementos (2^20) */
#define BLOCK 256       /* hilos por bloque CUDA */

/* ── KERNEL CUDA ─────────────────────────────────────────────
   Cada hilo calcula exactamente un elemento: C[tid] = A[tid] + B[tid]
   tid = indice global unico calculado a partir de bloque e hilo  */
__global__ void add_vectors(float* a, float* b, float* c, int n) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < n)                /* guardia de limite */
        c[tid] = a[tid] + b[tid];
}

int main() {
    int   n     = N;
    size_t bytes = n * sizeof(float);

    /* ── Reservar memoria en el host (CPU RAM) ────────────── */
    float *h_a     = (float*)malloc(bytes);
    float *h_b     = (float*)malloc(bytes);
    float *h_c_cpu = (float*)malloc(bytes);   /* resultado CPU */
    float *h_c_gpu = (float*)malloc(bytes);   /* resultado GPU */

    if (!h_a || !h_b || !h_c_cpu || !h_c_gpu) {
        printf("Error: sin memoria en host\n");
        return 1;
    }

    /* Inicializar vectores A y B */
    for (int i = 0; i < n; i++) {
        h_a[i] = (float)(i % 100) + 1.0f;
        h_b[i] = (float)(i % 50)  + 0.5f;
    }

    printf("============================================\n");
    printf(" SUMA DE VECTORES: OpenMP vs CUDA\n");
    printf(" N = %d elementos\n", n);
    printf("============================================\n\n");

    /* ════════════════════════════════════════════════════════
       FASE 1: VERSION CPU CON OpenMP
       ════════════════════════════════════════════════════════ */
    double t_cpu_ini = omp_get_wtime();

    #pragma omp parallel for
    for (int i = 0; i < n; i++)
        h_c_cpu[i] = h_a[i] + h_b[i];

    double t_cpu_fin = omp_get_wtime();
    double t_cpu = t_cpu_fin - t_cpu_ini;

    printf("[CPU - OpenMP]\n");
    printf("  Hilos usados : %d\n", omp_get_max_threads());
    printf("  Tiempo       : %.6f s\n\n", t_cpu);

    /* ════════════════════════════════════════════════════════
       FASE 2: VERSION GPU CON CUDA
       ════════════════════════════════════════════════════════ */
    float *d_a, *d_b, *d_c;

    /* Eventos CUDA para medir tiempo incluyendo transferencias */
    cudaEvent_t ev_start, ev_stop;
    cudaEventCreate(&ev_start);
    cudaEventCreate(&ev_stop);

    cudaEventRecord(ev_start);   /* iniciar reloj GPU */

    /* Paso 1: Reservar memoria en la GPU (VRAM) */
    cudaMalloc((void**)&d_a, bytes);
    cudaMalloc((void**)&d_b, bytes);
    cudaMalloc((void**)&d_c, bytes);

    /* Paso 2: Transferir datos Host -> Device (a traves de PCIe) */
    cudaMemcpy(d_a, h_a, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, bytes, cudaMemcpyHostToDevice);

    /* Paso 3: Ejecutar kernel
       num_bloques bloques de BLOCK hilos cada uno
       Total hilos = num_bloques * BLOCK >= N                   */
    int num_bloques = (n + BLOCK - 1) / BLOCK;
    add_vectors<<<num_bloques, BLOCK>>>(d_a, d_b, d_c, n);

    /* Paso 4: Transferir resultado Device -> Host */
    cudaMemcpy(h_c_gpu, d_c, bytes, cudaMemcpyDeviceToHost);

    cudaEventRecord(ev_stop);          /* parar reloj GPU */
    cudaEventSynchronize(ev_stop);     /* esperar a que termine */

    float t_gpu_ms = 0.0f;
    cudaEventElapsedTime(&t_gpu_ms, ev_start, ev_stop);
    double t_gpu = (double)t_gpu_ms / 1000.0;

    printf("[GPU - CUDA]\n");
    printf("  Bloques      : %d\n", num_bloques);
    printf("  Hilos/bloque : %d\n", BLOCK);
    printf("  Hilos totales: %d\n", num_bloques * BLOCK);
    printf("  Tiempo       : %.6f s  (incl. transferencias)\n\n", t_gpu);

    /* ── Verificacion de resultados ──────────────────────── */
    int errores = 0;
    for (int i = 0; i < n; i++)
        if (fabsf(h_c_gpu[i] - h_c_cpu[i]) > 1e-5f)
            errores++;

    printf("Verificacion  : %s (%d errores de %d elementos)\n\n",
           errores == 0 ? "CORRECTA" : "INCORRECTA", errores, n);

    /* ── Comparacion de rendimiento ──────────────────────── */
    double speedup = t_cpu / t_gpu;
    printf("============================================\n");
    printf(" COMPARACION DE RENDIMIENTO\n");
    printf("============================================\n");
    printf("  T_CPU (OpenMP) : %.6f s\n", t_cpu);
    printf("  T_GPU (CUDA)   : %.6f s\n", t_gpu);
    printf("  Speedup GPU/CPU: %.2fx  (%s)\n", speedup,
           speedup > 1.0 ? "GPU mas rapida" : "CPU mas rapida");

    /* ── Liberar recursos ────────────────────────────────── */
    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
    cudaEventDestroy(ev_start);
    cudaEventDestroy(ev_stop);
    free(h_a); free(h_b); free(h_c_cpu); free(h_c_gpu);

    return 0;
}
