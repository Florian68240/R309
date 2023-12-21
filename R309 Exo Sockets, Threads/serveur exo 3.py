import socket
import threading

# Utilisation d'un objet Event pour permettre l'arrêt du serveur depuis une fonction externe
server_stopped_event = threading.Event()


# Fonction gérant la réception des messages du client
def handle_client_receive(client_socket):
    try:
        while True:
            # Réception des données du client et décodage
            client_data = client_socket.recv(1024).decode('utf-8')

            # Vérification si le client s'est déconnecté
            if not client_data:
                print("Le client s'est déconnecté")
                break

            print(f"Client dit : {client_data}")

            # Vérification de commandes spéciales du client
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
        # Fermeture du socket client
        client_socket.close()


# Fonction gérant l'envoi des messages au client
def handle_client_send(client_socket):
    try:
        while True:
            # Saisie de la réponse du serveur depuis la console
            server_response = input("Réponse du serveur : ")

            # Envoi de la réponse au client
            client_socket.send(server_response.encode('utf-8'))

            # Vérification de commandes spéciales du serveur
            if server_response == "arret":
                print("Le serveur a été arrêté par le client")
                server_stopped_event.set()
                break

    except ConnectionError as e:
        print(f"Erreur de connexion : {e}")

    finally:
        # Fermeture du socket client
        client_socket.close()


# Fonction principale démarrant le serveur
def start_server():
    # Création de la socket serveur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Définition de l'adresse et du port du serveur
    host = '127.0.0.1'
    port = 12347

    try:
        # Liaison de la socket à l'adresse et au port spécifiés
        server_socket.bind((host, port))
    except OSError as e:
        if e.errno == 10048:
            print(f"Le port {port} est déjà utilisé. Assurez-vous qu'aucun autre programme n'utilise ce port.")
            exit()
        else:
            raise

    # Mise en écoute de la socket avec une file d'attente pour jusqu'à 5 connexions
    server_socket.listen(5)
    print(f"Le serveur écoute sur {host}:{port}")

    while not server_stopped_event.is_set():
        print("En attente d'un client...")

        # Acceptation d'une connexion entrante et récupération du socket de communication (client_socket) et de l'adresse du client (client_address)
        client_socket, client_address = server_socket.accept()
        print(f"Connexion entrante de {client_address}")

        # Création de deux threads pour gérer la réception et l'envoi avec le client simultanément
        client_thread_receive = threading.Thread(target=handle_client_receive, args=(client_socket,))
        client_thread_send = threading.Thread(target=handle_client_send, args=(client_socket,))

        # Démarrage des threads
        client_thread_receive.start()
        client_thread_send.start()

        # Attente de la fin des threads avant de passer à la prochaine connexion
        client_thread_receive.join()
        client_thread_send.join()

    # Fermeture de la socket serveur lorsque le serveur s'arrête
    server_socket.close()


# Point d'entrée du programme
if __name__ == "__main__":
    start_server()
