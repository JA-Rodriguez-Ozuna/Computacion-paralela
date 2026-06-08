"""
Aplicacion 2: Cliente RPC con xmlrpc
Asignatura: Sistemas Distribuidos - Semana 5
Descripcion: Solicita al usuario un numero entero, llama a la funcion
             remota 'calcular_cuadrado' en el servidor RPC y muestra el resultado.

Instrucciones de uso (Windows / VS Code):
  1. Primero ejecutar el servidor: python Rpc_server.py
  2. Luego en OTRA terminal: python Rpc_client.py
  3. Ingresar un numero entero cuando se solicite
"""

import xmlrpc.client


# ─── Configuracion (debe coincidir con rpc_server.py) ─────────────────────────
URL_SERVIDOR = 'http://127.0.0.1:8000/'


def solicitar_cuadrado():
    """Conecta al servidor RPC, invoca la funcion remota y muestra el resultado."""

    # ServerProxy actua como STUB del cliente:
    # cualquier atributo que se llame sobre 'proxy' se convierte en una
    # llamada remota serializada en XML y enviada por HTTP.
    proxy = xmlrpc.client.ServerProxy(URL_SERVIDOR)

    print("=== Cliente RPC: Calculadora de Cuadrados ===\n")

    try:
        # Solicita el numero al usuario con validacion de entrada
        entrada = input("Ingrese un numero entero: ").strip()
        numero = int(entrada)

    except ValueError:
        print("[ERROR] El valor ingresado no es un numero entero valido.")
        return

    try:
        print(f"\n[CLIENTE RPC] Invocando calcular_cuadrado({numero}) en el servidor...")

        # Esta linea parece una llamada local, pero en realidad:
        #  1. Serializa (numero) en XML
        #  2. Envia HTTP POST a localhost:8000
        #  3. Deserializa la respuesta XML
        #  4. Retorna el entero resultado
        resultado = proxy.calcular_cuadrado(numero)

        print(f"[CLIENTE RPC] Resultado recibido del servidor.")
        print(f"\n>>> El cuadrado de {numero} es: {resultado} <<<")

    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar al servidor RPC en {URL_SERVIDOR}")
        print("        Asegurese de ejecutar rpc_server.py primero.")
    except xmlrpc.client.Fault as fallo:
        print(f"[ERROR RPC] El servidor reporto un error: {fallo.faultString}")
    except Exception as e:
        print(f"[ERROR] Ocurrio un problema inesperado: {e}")


if __name__ == "__main__":
    solicitar_cuadrado()