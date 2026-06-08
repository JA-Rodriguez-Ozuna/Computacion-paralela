"""
Aplicacion 2: Servidor RPC con xmlrpc
Asignatura: Sistemas Distribuidos - Semana 5
Descripcion: Servidor que expone la funcion remota 'calcular_cuadrado'.
             Recibe un numero entero y devuelve su cuadrado.

Instrucciones de uso (Windows / VS Code):
  1. Abrir una terminal en VS Code
  2. Ejecutar: python Rpc_server.py
  3. En OTRA terminal ejecutar el cliente: python Rpc_client.py
  4. Para detener el servidor: Ctrl + C
"""

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


# ─── Configuracion ────────────────────────────────────────────────────────────
HOST = '127.0.0.1'
PORT = 8000


# ─── Handler silencioso (sin logs HTTP en consola) ────────────────────────────
class HandlerSilencioso(SimpleXMLRPCRequestHandler):
    """Suprime los mensajes de log HTTP para una salida mas limpia."""
    def log_message(self, formato, *args):
        pass  # No imprimir cada solicitud HTTP


# ─── Funcion remota ───────────────────────────────────────────────────────────
def calcular_cuadrado(numero):
    """
    Funcion remota disponible via RPC.
    Recibe un numero entero y retorna su cuadrado.

    Args:
        numero (int): El entero cuyo cuadrado se desea calcular.

    Returns:
        int: El cuadrado de 'numero'.
    """
    print(f"[SERVIDOR RPC] Solicitud recibida: calcular_cuadrado({numero})")
    resultado = numero * numero
    print(f"[SERVIDOR RPC] Resultado calculado: {resultado}")
    return resultado


# ─── Inicio del servidor ──────────────────────────────────────────────────────
def iniciar_servidor_rpc():
    """Crea y pone en marcha el servidor XML-RPC."""
    servidor = SimpleXMLRPCServer(
        (HOST, PORT),
        requestHandler=HandlerSilencioso,
        allow_none=True    # Permite retornar None si fuera necesario
    )

    # Registra la funcion para que sea invocable remotamente
    servidor.register_function(calcular_cuadrado, 'calcular_cuadrado')

    # Tambien expone introspection (permite listar funciones disponibles)
    servidor.register_introspection_functions()

    print(f"[SERVIDOR RPC] Servidor XML-RPC iniciado en http://{HOST}:{PORT}/")
    print("[SERVIDOR RPC] Funcion disponible: calcular_cuadrado(numero)")
    print("[SERVIDOR RPC] Esperando llamadas remotas... (Ctrl+C para detener)\n")

    try:
        # Bucle infinito que atiende solicitudes entrantes
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVIDOR RPC] Servidor detenido por el usuario.")


if __name__ == "__main__":
    iniciar_servidor_rpc()