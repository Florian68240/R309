import socket

# Paramètres du serveur
HOST = '127.0.0.1'
PORT = 6500

# Dictionnaire pour stocker les connexions des clients
clients = {}


# Fonction pour gérer la connexion d'un client
def handle_client(client_socket, client_address):
    try:
        while True:
            # Recevoir le message du client
            message = client_socket.recv(1024).decode('utf-8')

            # Vérifier le message de protocole
            if message == 'bye':
                print(f"Client {client_address} a demandé de se déconnecter.")
                break
            elif message == 'arret':
                print(f"Arrêt du client {client_address}.")
                break
            else:
                # Afficher le message du client
                print(f"Message du client {client_address}: {message}")

                # Envoyer une réponse au client
                response = input("Réponse au client: ")
                client_socket.send(response.encode('utf-8'))
    except ConnectionResetError:
        print(f"Connexion avec {client_address} perdue.")
    finally:
        # Supprimer le client de la liste après la déconnexion
        del clients[client_address]
        client_socket.close()


# Configuration du serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Serveur en attente sur {HOST}:{PORT}...")

# Accepter les connexions des clients
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connexion acceptée depuis {client_address}")

    # Ajouter le client à la liste
    clients[client_address] = client_socket

    # Démarrer la gestion du client dans le même thread
    handle_client(client_socket, client_address)
