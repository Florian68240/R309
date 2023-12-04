import socket
import threading
server_stopped_event = threading.Event()

def handle_client_receive(client_socket):
    try:
        while True:
            client_data = client_socket.recv(1024).decode('utf-8')
            if not client_data:
                print("Le client s'est déconnecté")
                break
            print(f"Client dit : {client_data}")
            if client_data == "arret":
                print("Le serveur a été arrêté par le client")
                server_stopped_event.set()
                break
            elif client_data == "bye":
                print("Le client s'est déconnecté")
                break
    except ConnectionError as e:
        print(f"Erreur de connexion : {e}")

    finally:
        client_socket.close()

def handle_client_send(client_socket):
    try:
        while True:
            server_response = input("Réponse du serveur : ")
            client_socket.send(server_response.encode('utf-8'))

            if server_response == "arret":
                print("Le serveur a été arrêté par le client")
                server_stopped_event.set()
                break

    except ConnectionError as e:
        print(f"Erreur de connexion : {e}")

    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12347

    try:
        server_socket.bind((host, port))
    except OSError as e:
        if e.errno == 10048:
            print(f"Le port {port} est déjà utilisé. Assurez-vous qu'aucun autre programme n'utilise ce port.")
            exit()
        else:
            raise

    server_socket.listen(5)
    print(f"Le serveur écoute sur {host}:{port}")

    while not server_stopped_event.is_set():
        print("En attente d'un client...")
        client_socket, client_address = server_socket.accept()
        print(f"Connexion entrante de {client_address}")
        client_thread_receive = threading.Thread(target=handle_client_receive, args=(client_socket,))
        client_thread_send = threading.Thread(target=handle_client_send, args=(client_socket,))
        client_thread_receive.start()
        client_thread_send.start()
        client_thread_receive.join()
        client_thread_send.join()

    server_socket.close()

if __name__ == "__main__":
    start_server()