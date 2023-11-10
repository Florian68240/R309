import socket
import threading

# Paramètres du serveur
HOST = '127.0.0.1'
PORT = 6500

# Liste des clients connectés
clients = []


# Fonction de gestion des clients
def handle_client(client_socket):
    while True:
        # Acquérir le message du client
        message = client_socket.recv(1024).decode('utf-8')

        # Vérifier le message de protocole
        if message == 'bye':
            print(f"Client {client_socket} a demandé de se déconnecter.")
            break
        elif message == 'arret':
            print(f"Arrêt du serveur à la demande du client {client_socket}.")
            for c in clients:
                c.send('arret'.encode('utf-8'))
            server_socket.close()
            break
        else:
            # Afficher le message du client
            print(f"Message du client {client_socket}: {message}")

            # Répondre au client
            response = input("Réponse au client: ")
            client_socket.send(response.encode('utf-8'))


# Configuration du serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Serveur en attente sur {HOST}:{PORT}...")

# Accepter les connexions des clients
while True:
    client_socket, addr = server_socket.accept()
    print(f"Connexion acceptée depuis {addr}")

    # Ajouter le client à la liste
    clients.append(client_socket)

    # Démarrer un thread pour gérer le client
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
