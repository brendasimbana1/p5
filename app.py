import socket
import struct

BALANCER_HOST = "10.0.10.1"  
BALANCER_PORT = 8080           

REQ_STRUCT = "iii"   # 3 enteros

RESP_STRUCT = "diii"  # double + 3 ints


def enviar_kmeans_request(k, max_iters, mode=0):
    """Envia una solicitud KMeans al servidor balanceado y recibe la respuesta."""
    
    # Crear socket TCP IPv4
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"[CLIENTE] Conectando con el balanceador {BALANCER_HOST}:{BALANCER_PORT}...")
        sock.connect((BALANCER_HOST, BALANCER_PORT))

        # Empaquetar la solicitud
        req = struct.pack(REQ_STRUCT, k, max_iters, mode)

        print("[CLIENTE] Enviando solicitud...")
        sock.sendall(req)

        # ------------------------------
        # 1) Recibir ResponseHeader
        # ------------------------------
        header_size = struct.calcsize(RESP_STRUCT)
        header_data = sock.recv(header_size)

        if len(header_data) != header_size:
            print("[ERROR] No se recibió el header completo.")
            return

        cpu_time, iterations, k_resp, dim = struct.unpack(RESP_STRUCT, header_data)

        print("\n===== RESULTADO DEL SERVIDOR =====")
        print(f"Tiempo CPU:     {cpu_time:.6f} s")
        print(f"Iteraciones:    {iterations}")
        print(f"K (clusters):   {k_resp}")
        print(f"Dimensión:      {dim}")

        # ------------------------------
        # 2) Recibir cardinalidades
        # ------------------------------
        card_size = k_resp * 4   # K enteros (4 bytes cada uno)
        card_data = sock.recv(card_size)

        if len(card_data) != card_size:
            print("[ERROR] No se recibieron todas las cardinalidades.")
            return
        
        cardinalidades = struct.unpack("i" * k_resp, card_data)

        print("\nCardinalidades:")
        for i, c in enumerate(cardinalidades):
            print(f"  Cluster {i}: {c} puntos")

        print("=================================\n")

    finally:
        sock.close()


if __name__ == "__main__":
    # Ejemplo: K=5 clusters, máximo 50 iteraciones
    enviar_kmeans_request(k=5, max_iters=50)
