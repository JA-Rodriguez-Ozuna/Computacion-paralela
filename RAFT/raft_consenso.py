"""
raft_consenso.py
Simulacion del algoritmo de consenso Raft con 5 nodos
Implementa: eleccion de lider, replicacion de log y tolerancia a fallos

Ejecutar: python raft_consenso.py
No requiere librerias externas.
"""

import random
import time

# ── Configuracion ────────────────────────────────────────────
NUM_NODOS      = 5
QUORUM         = NUM_NODOS // 2 + 1  # mayoria: 3 de 5
TIMEOUT_MIN    = 1.5
TIMEOUT_MAX    = 3.0

# ── Estados posibles de un nodo ──────────────────────────────
SEGUIDOR  = "SEGUIDOR"
CANDIDATO = "CANDIDATO"
LIDER     = "LIDER"
CAIDO     = "CAIDO"

# ════════════════════════════════════════════════════════════
# CLASE NODO
# ════════════════════════════════════════════════════════════
class Nodo:
    def __init__(self, nid, total):
        self.nid          = nid          # identificador del nodo
        self.estado       = SEGUIDOR     # estado inicial
        self.termino      = 0            # termino actual (epoch)
        self.voto_para    = None         # a quien voto en este termino
        self.log          = []           # registro de entradas confirmadas
        self.valor_commit = None         # ultimo valor confirmado
        self.votos_recibidos = 0
        self.total        = total
        self.caido        = False

    def __str__(self):
        return (f"Nodo {self.nid} [{self.estado}] "
                f"termino={self.termino} "
                f"log={self.log} "
                f"commit={self.valor_commit}")


# ════════════════════════════════════════════════════════════
# SIMULACION RAFT
# ════════════════════════════════════════════════════════════
class SimulacionRaft:

    def __init__(self):
        self.nodos = [Nodo(i, NUM_NODOS) for i in range(NUM_NODOS)]
        self.lider_actual = None
        self.log_eventos  = []

    def log(self, msg):
        print(msg)
        self.log_eventos.append(msg)

    # ── FASE 1: Eleccion de lider ────────────────────────────
    def eleccion_lider(self, candidato_id=None):
        self.log("\n" + "="*55)
        self.log(" FASE 1: ELECCION DE LIDER")
        self.log("="*55)

        # Si no se especifica candidato, elegir el primero activo
        if candidato_id is None:
            candidato_id = next(n.nid for n in self.nodos if not n.caido)

        candidato = self.nodos[candidato_id]
        candidato.estado  = CANDIDATO
        candidato.termino += 1
        candidato.voto_para = candidato_id
        candidato.votos_recibidos = 1  # voto por si mismo

        self.log(f"\n[Nodo {candidato_id}] Se postula como CANDIDATO "
                 f"para termino {candidato.termino}")
        self.log(f"[Nodo {candidato_id}] Vota por si mismo (1/{QUORUM} votos)")

        # Solicitar votos a los demas nodos
        for nodo in self.nodos:
            if nodo.nid == candidato_id or nodo.caido:
                continue

            # El nodo vota si no ha votado en este termino
            if nodo.voto_para is None or nodo.termino < candidato.termino:
                nodo.voto_para = candidato_id
                nodo.termino   = candidato.termino
                candidato.votos_recibidos += 1
                self.log(f"[Nodo {nodo.nid}] Vota por Nodo {candidato_id} "
                         f"(voto {candidato.votos_recibidos}/{QUORUM})")
            else:
                self.log(f"[Nodo {nodo.nid}] Rechaza voto "
                         f"(ya voto en termino {nodo.termino})")

            # Verificar si ya alcanzamos quorum
            if candidato.votos_recibidos >= QUORUM:
                break

        # Verificar resultado
        if candidato.votos_recibidos >= QUORUM:
            candidato.estado   = LIDER
            self.lider_actual  = candidato_id

            # Actualizar estado de los demas como seguidores
            for nodo in self.nodos:
                if nodo.nid != candidato_id and not nodo.caido:
                    nodo.estado = SEGUIDOR

            self.log(f"\n[Nodo {candidato_id}] ELEGIDO COMO LIDER con "
                     f"{candidato.votos_recibidos}/{NUM_NODOS} votos "
                     f"en termino {candidato.termino}")
            return True
        else:
            candidato.estado = SEGUIDOR
            self.log(f"[Nodo {candidato_id}] No alcanzo quorum. "
                     f"Nueva eleccion necesaria.")
            return False

    # ── FASE 2: Replicacion de entrada en el log ─────────────
    def replicar_entrada(self, valor):
        self.log("\n" + "="*55)
        self.log(f" FASE 2: REPLICACION DE LOG — valor='{valor}'")
        self.log("="*55)

        if self.lider_actual is None:
            self.log("ERROR: No hay lider activo.")
            return False

        lider = self.nodos[self.lider_actual]
        entrada = {"termino": lider.termino, "valor": valor}

        # Lider agrega al log primero
        lider.log.append(entrada)
        self.log(f"\n[Nodo {self.lider_actual}] LIDER agrega entrada al log: {entrada}")

        # Replicar a seguidores
        replicados = 1   # el lider ya la tiene
        for nodo in self.nodos:
            if nodo.nid == self.lider_actual or nodo.caido:
                if nodo.caido:
                    self.log(f"[Nodo {nodo.nid}] CAIDO — no recibe replicacion")
                continue

            nodo.log.append(entrada)
            replicados += 1
            self.log(f"[Nodo {nodo.nid}] Replica entrada: {entrada} "
                     f"({replicados}/{QUORUM} confirmaciones)")

            if replicados >= QUORUM:
                break

        # Commit si hay quorum
        if replicados >= QUORUM:
            self.log(f"\n[Nodo {self.lider_actual}] QUORUM alcanzado "
                     f"({replicados}/{NUM_NODOS}) — COMMIT '{valor}'")

            # Confirmar en todos los nodos activos
            for nodo in self.nodos:
                if not nodo.caido:
                    nodo.valor_commit = valor

            self.log(f"[CONSENSO] Valor '{valor}' confirmado en todos los nodos activos")
            return True
        else:
            self.log(f"ERROR: Solo {replicados} nodos disponibles, quorum={QUORUM}")
            return False

    # ── FASE 3: Simular fallo del lider ──────────────────────
    def simular_fallo_lider(self):
        self.log("\n" + "="*55)
        self.log(" FASE 3: FALLO DEL LIDER")
        self.log("="*55)

        if self.lider_actual is None:
            self.log("No hay lider que derribar.")
            return

        lider_caido = self.lider_actual
        self.nodos[lider_caido].caido  = True
        self.nodos[lider_caido].estado = CAIDO
        self.lider_actual = None

        self.log(f"\n[!] NODO {lider_caido} (LIDER) HA CAIDO")
        self.log(f"    Nodos activos restantes: "
                 f"{[n.nid for n in self.nodos if not n.caido]}")

        # Detectar timeout y lanzar nueva eleccion
        self.log(f"\n[Sistema] Timeout detectado — iniciando nueva eleccion...")

        # Elegir nuevo candidato (el primer seguidor activo)
        nuevo_candidato = next(
            (n.nid for n in self.nodos
             if not n.caido and n.estado == SEGUIDOR), None
        )

        if nuevo_candidato is not None:
            # Resetear votos para nueva eleccion
            for nodo in self.nodos:
                if not nodo.caido:
                    nodo.voto_para = None
            return nuevo_candidato
        else:
            self.log("ERROR: No hay candidatos disponibles.")
            return None

    # ── Mostrar estado de todos los nodos ────────────────────
    def mostrar_estado(self):
        self.log("\n" + "-"*55)
        self.log(" ESTADO ACTUAL DE LOS NODOS")
        self.log("-"*55)
        for nodo in self.nodos:
            estado_str = f"[{nodo.estado}]"
            if nodo.caido:
                estado_str = "[CAIDO]"
            self.log(f"  Nodo {nodo.nid} {estado_str:12} "
                     f"termino={nodo.termino}  "
                     f"commit='{nodo.valor_commit}'  "
                     f"log={[e['valor'] for e in nodo.log]}")
        self.log("-"*55)


# ════════════════════════════════════════════════════════════
# EJECUCION PRINCIPAL
# ════════════════════════════════════════════════════════════
def main():
    print("="*55)
    print(" SIMULACION ALGORITMO RAFT — CONSENSO DISTRIBUIDO")
    print(f" Nodos: {NUM_NODOS}  |  Quorum: {QUORUM}")
    print("="*55)

    sim = SimulacionRaft()

    # ── RONDA 1: Eleccion inicial ─────────────────────────────
    sim.eleccion_lider(candidato_id=0)
    sim.mostrar_estado()

    # ── RONDA 1: Replicar primer valor ───────────────────────
    sim.replicar_entrada("A=1")
    sim.mostrar_estado()

    # ── RONDA 1: Replicar segundo valor ──────────────────────
    sim.replicar_entrada("B=2")
    sim.mostrar_estado()

    # ── RONDA 2: Simular fallo del lider ─────────────────────
    nuevo_candidato = sim.simular_fallo_lider()

    # ── RONDA 2: Nueva eleccion tras el fallo ────────────────
    if nuevo_candidato is not None:
        sim.eleccion_lider(candidato_id=nuevo_candidato)
        sim.mostrar_estado()

        # Replicar nuevo valor con el nuevo lider
        sim.replicar_entrada("C=3")
        sim.mostrar_estado()

    # ── Resumen final ─────────────────────────────────────────
    print("\n" + "="*55)
    print(" RESUMEN FINAL")
    print("="*55)
    activos = [n for n in sim.nodos if not n.caido]
    caidos  = [n for n in sim.nodos if n.caido]
    print(f"  Nodos activos : {len(activos)}")
    print(f"  Nodos caidos  : {len(caidos)} "
          f"({[n.nid for n in caidos]})")
    print(f"  Lider actual  : Nodo {sim.lider_actual}")
    print(f"  Ultimo commit : '{activos[0].valor_commit if activos else None}'")
    print(f"  Consenso      : "
          f"{'EXITOSO' if all(n.valor_commit == activos[0].valor_commit for n in activos) else 'FALLIDO'}")
    print("="*55)


if __name__ == "__main__":
    main()