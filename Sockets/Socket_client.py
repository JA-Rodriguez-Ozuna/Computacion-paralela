"""
Aplicacion 1: Cliente con Sockets TCP
Asignatura: Sistemas Distribuidos - Semana 5
Descripcion: Cliente que se conecta al servidor, envia un mensaje
             ingresado por el usuario y muestra la respuesta.

Instrucciones de uso (Windows / VS Code):
  1. Primero ejecutar el servidor: python Socket_server.py
  2. Luego en OTRA terminal: python Socket_client.py
  3. Escribir el mensaje cuando se solicite y presionar Enter
"""

import socket

# ─── Configuracion (debe coincidir con socket_server.py) ──────────────────────
HOST = '127.0.0.1'   # Direccion IP del servidor
PORT = 65432         # Puerto del servidor
BUFFER_SIZE = 1024   # Bytes maximos a recibir


def conectar_y_enviar():
    """Conecta al servidor, envia el mensaje del usuario y muestra la respuesta."""

    # Solicita el mensaje al usuario
    mensaje = input("Ingrese el mensaje a enviar al servidor: ").strip()

    if not mensaje:
        print("[CLIENTE] No se ingreso ningun mensaje. Abortando.")
        return

    # AF_INET = IPv4 | SOCK_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:

        # Establece un tiempo de espera maximo para operaciones de red (10 segundos)
        cliente.settimeout(10.0)

        print(f"\n[CLIENTE] Conectando a {HOST}:{PORT} ...")

        try:
            # Establece la conexion TCP (Three-Way Handshake)
            cliente.connect((HOST, PORT))
            print(f"[CLIENTE] Conexion establecida exitosamente.")

            # Envia el mensaje codificado en bytes (UTF-8)
            cliente.sendall(mensaje.encode('utf-8'))
            print(f"[CLIENTE] Mensaje enviado: '{mensaje}'")

            # Espera la respuesta del servidor (bloquea hasta recibirla)
            respuesta = cliente.recv(BUFFER_SIZE)
            print(f"[CLIENTE] Respuesta del servidor: '{respuesta.decode('utf-8')}'")

        except ConnectionRefusedError:
            print(f"[ERROR] Conexion rechazada. Asegurese de que el servidor")
            print(f"        este ejecutandose en {HOST}:{PORT}")
        except socket.timeout:
            print("[ERROR] Tiempo de espera agotado. El servidor no responde.")
        except Exception as e:
            print(f"[ERROR] Ocurrio un problema en la comunicacion: {e}")

    print("[CLIENTE] Conexion cerrada.")


if __name__ == "__main__":
    conectar_y_enviar()