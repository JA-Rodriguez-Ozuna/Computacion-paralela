"""
Aplicacion 1: Servidor con Sockets TCP
Asignatura: Sistemas Distribuidos - Semana 5
Descripcion: Servidor que espera una conexion entrante, lee el mensaje
             del cliente y responde con una confirmacion.

Instrucciones de uso (Windows / VS Code):
  1. Abrir una terminal en VS Code (Terminal > New Terminal)
  2. Ejecutar: python Socket_server.py
  3. En OTRA terminal ejecutar el cliente: python Socket_client.py
"""

import socket

# ─── Configuracion ────────────────────────────────────────────────────────────
HOST = '127.0.0.1'   # Loopback local (misma maquina)
PORT = 65432         # Puerto de escucha (>1024 no requiere admin)
BUFFER_SIZE = 1024   # Bytes maximos a recibir por recv()


def iniciar_servidor():
    """Crea el socket, espera conexiones en bucle y las atiende."""

    # AF_INET = IPv4 | SOCK_STREAM = TCP (orientado a conexion, confiable)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:

        # Permite reusar el puerto inmediatamente tras reiniciar (evita 'Address already in use')
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Asocia el socket a la direccion y puerto
        servidor.bind((HOST, PORT))

        # Pone el socket en modo escucha; backlog=1 = hasta 1 conexion pendiente
        servidor.listen(1)
        print(f"[SERVIDOR] Escuchando en {HOST}:{PORT} ...")
        print("[SERVIDOR] Esperando conexiones de clientes... (Ctrl+C para detener)\n")

        try:
            while True:
                # Bloquea hasta que un cliente se conecta
                conn, addr = servidor.accept()

                with conn:
                    print(f"[SERVIDOR] Conexion establecida desde {addr}")

                    # Recibe hasta BUFFER_SIZE bytes del cliente
                    datos = conn.recv(BUFFER_SIZE)

                    if datos:
                        mensaje_recibido = datos.decode('utf-8')
                        print(f"[SERVIDOR] Mensaje del cliente: '{mensaje_recibido}'")

                        # Prepara y envia la respuesta de confirmacion
                        respuesta = f"Mensaje recibido correctamente: '{mensaje_recibido}'"
                        conn.sendall(respuesta.encode('utf-8'))
                        print(f"[SERVIDOR] Confirmacion enviada al cliente.")
                    else:
                        print("[SERVIDOR] El cliente cerro la conexion sin enviar datos.")

                print("[SERVIDOR] Conexion cerrada. Esperando nueva conexion...\n")
        except KeyboardInterrupt:
            print("\n[SERVIDOR] Servidor detenido por el usuario.")


if __name__ == "__main__":
    try:
        iniciar_servidor()
    except OSError as e:
        print(f"[ERROR] No se pudo iniciar el servidor: {e}")
        print(f"        Verifique que el puerto {PORT} no este en uso.")