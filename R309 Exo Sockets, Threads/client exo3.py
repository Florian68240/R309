import socket
import threading


# Fonction pour recevoir les messages du serveur
def receive_messages(client_socket):
    try:
        while True:
            # Réception des données du serveur (jusqu'à 1024 octets) et décodage en UTF-8
            server_response = client_socket.recv(1024).decode('utf-8')

            # Vérification si la connexion au serveur a été interrompue
            if not server_response:
                print("La connexion au serveur a été interrompue.")
                break

            print(f"Réponse du serveur : {server_response}")

            # Vérification de commandes spéciales du serveur
            if server_response == "arret":
                print("Le serveur a été arrêté par le client")
                break

    except ConnectionError as e:
        print(f"Erreur de connexion : {e}")

    finally:
        # Fermeture du socket client
        client_socket.close()


# Fonction principale du client
def main():
    # Création du socket client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Définition de l'adresse et du port du serveur
    server_address = ('127.0.0.1', 12347)

    try:
        # Connexion au serveur
        client_socket.connect(server_address)

        # Création d'un thread pour recevoir les messages du serveur
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
            # Saisie du message du client depuis la console
            client_message = input("Message du client : ")

            # Envoi du message au serveur
            client_socket.send(client_message.encode('utf-8'))

            # Vérification de commandes spéciales du client
            if client_message in ["arret", "bye"]:
                print("Le client se déconnecte.")
                break

    except ConnectionRefusedError:
        print("La connexion au serveur a été refusée. Assurez-vous que le serveur est en cours d'exécution.")
    except ConnectionError as e:
        print(f"Erreur de connexion : {e}")

    finally:
        # Fermeture du socket client
        client_socket.close()


# Point d'entrée du programme
if __name__ == "__main__":
    main()
