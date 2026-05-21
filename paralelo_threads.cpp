// ============================================================
//  paralelo_threads.cpp
//  Demostración de paralelismo con std::thread (C++17)
//  No requiere librerías externas.
//
//  Compilar:
//    g++ -O2 -std=c++17 paralelo_threads.cpp -o paralelo_threads.exe
//  Ejecutar:
//    .\paralelo_threads.exe
// ============================================================
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <numeric>
 
// Función que cada hilo ejecuta sobre su rango
void sumar_rango(const std::vector<double>& A,
                 const std::vector<double>& B,
                 std::vector<double>& C,
                 int inicio, int fin) {
    for (int i = inicio; i < fin; i++) {
        C[i] = A[i] + B[i];
    }
}
 
int main() {
    const int N          = 100000000; // 100 millones de elementos
    const int NUM_HILOS  = std::thread::hardware_concurrency(); // núcleos disponibles
 
    std::vector<double> A(N, 1.5);
    std::vector<double> B(N, 2.5);
    std::vector<double> C(N, 0.0);
 
    std::cout << "=== Paralelismo con std::thread ===" << std::endl;
    std::cout << "Nucleos disponibles: " << NUM_HILOS << std::endl;
    std::cout << "Elementos          : " << N << std::endl;
 
    // ── Versión SECUENCIAL ────────────────────────────────────
    auto t1 = std::chrono::high_resolution_clock::now();
 
    for (int i = 0; i < N; i++) {
        C[i] = A[i] + B[i];
    }
 
    auto t2   = std::chrono::high_resolution_clock::now();
    double ts = std::chrono::duration<double>(t2 - t1).count();
    std::cout << "\nTiempo secuencial  : " << ts << "s" << std::endl;
 
    // Resetear C
    std::fill(C.begin(), C.end(), 0.0);
 
    // ── Versión PARALELA con std::thread ─────────────────────
    auto t3 = std::chrono::high_resolution_clock::now();
 
    std::vector<std::thread> hilos;
    int tamano = N / NUM_HILOS;
 
    for (int t = 0; t < NUM_HILOS; t++) {
        int inicio = t * tamano;
        int fin    = (t == NUM_HILOS - 1) ? N : inicio + tamano;
        hilos.emplace_back(sumar_rango,
                           std::cref(A), std::cref(B), std::ref(C),
                           inicio, fin);
    }
 
    // Esperar a que todos los hilos terminen
    for (auto& h : hilos) {
        h.join();
    }
 
    auto t4   = std::chrono::high_resolution_clock::now();
    double tp = std::chrono::duration<double>(t4 - t3).count();
 
    std::cout << "Tiempo paralelo    : " << tp << "s" << std::endl;
    std::cout << "Speedup            : " << ts / tp << "x" << std::endl;
    std::cout << "Verificacion       : C[0]=" << C[0]
              << "  C[N-1]=" << C[N-1] << std::endl;
 
    return 0;
}