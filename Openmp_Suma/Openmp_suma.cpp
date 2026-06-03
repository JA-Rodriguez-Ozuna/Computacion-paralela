// ============================================================
//  openmp_suma.cpp
//  Demostración de paralelismo con OpenMP
//  Compilar: g++ -O2 -fopenmp openmp_suma.cpp -o openmp_suma
//  Ejecutar: ./openmp_suma
// ============================================================
#include <iostream>
#include <vector>
#include <omp.h>
 
int main() {
    const int N = 100000000; // 100 millones de elementos
    std::vector<double> A(N, 1.5);
    std::vector<double> B(N, 2.5);
    std::vector<double> C(N, 0.0);
 
    // ── Versión SECUENCIAL ────────────────────────────────────
    double t1 = omp_get_wtime();
    for (int i = 0; i < N; i++) {
        C[i] = A[i] + B[i];
    }
    double t2 = omp_get_wtime();
    std::cout << "=== OpenMP Demo ===" << std::endl;
    std::cout << "Hilos disponibles : " << omp_get_max_threads() << std::endl;
    std::cout << "Tiempo secuencial : " << (t2 - t1) << "s" << std::endl;
 
    // Resetear C
    std::fill(C.begin(), C.end(), 0.0);
 
    // ── Versión PARALELA ──────────────────────────────────────
    double t3 = omp_get_wtime();
 
    #pragma omp parallel for
    for (int i = 0; i < N; i++) {
        C[i] = A[i] + B[i];
    }
 
    double t4 = omp_get_wtime();
    std::cout << "Tiempo paralelo   : " << (t4 - t3) << "s" << std::endl;
    std::cout << "Speedup           : " << (t2-t1)/(t4-t3) << "x" << std::endl;
    std::cout << "Verificacion      : C[0]=" << C[0] << " C[N-1]=" << C[N-1] << std::endl;
 
    return 0;
}