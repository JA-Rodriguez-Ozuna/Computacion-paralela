// ============================================================
//  sincronizacion_semaforo.cpp
//  Sincronización con semáforos — Estándar POSIX (hilos y semáforos)
//
//  Compilar en Windows/Linux con GCC:
//    g++ -O2 sincronizacion_semaforo.cpp -o sincronizacion_semaforo.exe -lpthread
//  Ejecutar:
//    .\sincronizacion_semaforo.exe
// ============================================================
#include <iostream>
#include <pthread.h>
#include <semaphore.h>
#include <vector>

// ── Variables globales y constantes ───────────────────────────
const int NUM_HILOS   = 5;
const int ITERACIONES = 1000;

int contador = 0;   // Recurso compartido (variable a incrementar)
sem_t semaforo;     // Semáforo para la exclusión mutua

// ── Función que ejecuta cada hilo ─────────────────────────────
void* incrementar(void* arg) {
    int id = *(int*)arg;

    for (int i = 0; i < ITERACIONES; i++) {
        // ENTRAR a la sección crítica (Espera / Wait)
        sem_wait(&semaforo);

        // --- INICIO DE SECCIÓN CRÍTICA ---
        contador++;
        // --- FIN DE SECCIÓN CRÍTICA ---

        // SALIR de la sección crítica (Señalización / Post)
        sem_post(&semaforo);
    }

    std::cout << "-> Hilo " << id << " finalizo sus " << ITERACIONES << " incrementos." << std::endl;
    return nullptr;
}

// ── Función principal (Main) ──────────────────────────────────
int main() {
    pthread_t hilos[NUM_HILOS];
    int ids[NUM_HILOS];

    std::cout << "====================================================" << std::endl;
    std::cout << "   Simulacion de Acceso Concurrente con Semaforos   " << std::endl;
    std::cout << "====================================================" << std::endl;
    std::cout << " Hilos a crear       : " << NUM_HILOS << std::endl;
    std::cout << " Iteraciones por hilo: " << ITERACIONES << std::endl;
    std::cout << " Valor final esperado: " << NUM_HILOS * ITERACIONES << std::endl;
    std::cout << "----------------------------------------------------" << std::endl;

    // Inicializar el semáforo con un valor de 1 (exclusión mutua)
    // El segundo parámetro (0) indica que el semáforo es compartido entre hilos del mismo proceso
    if (sem_init(&semaforo, 0, 1) != 0) {
        std::cerr << "Error al inicializar el semaforo." << std::endl;
        return 1;
    }

    // Crear los hilos concurrentes
    for (int i = 0; i < NUM_HILOS; i++) {
        ids[i] = i + 1;
        if (pthread_create(&hilos[i], nullptr, incrementar, &ids[i]) != 0) {
            std::cerr << "Error al crear el hilo " << ids[i] << std::endl;
            return 1;
        }
    }

    // Esperar a que todos los hilos terminen su ejecución
    for (int i = 0; i < NUM_HILOS; i++) {
        pthread_join(hilos[i], nullptr);
    }

    // Destruir el semáforo para liberar recursos
    sem_destroy(&semaforo);

    // Evidencia de Sincronización y resultados
    std::cout << "----------------------------------------------------" << std::endl;
    std::cout << " RESULTADO DE LA EJECUCION: " << std::endl;
    std::cout << "  Valor final del contador: " << contador << std::endl;
    std::cout << "  Valor esperado          : " << NUM_HILOS * ITERACIONES << std::endl;
    std::cout << "----------------------------------------------------" << std::endl;

    if (contador == NUM_HILOS * ITERACIONES) {
        std::cout << " >>> Sincronizacion: EXITOSA (CORRECTO) <<<" << std::endl;
    } else {
        std::cout << " >>> Sincronizacion: FALLIDA (ERROR de concurrencia) <<<" << std::endl;
    }
    std::cout << "====================================================" << std::endl;

    return 0;
}