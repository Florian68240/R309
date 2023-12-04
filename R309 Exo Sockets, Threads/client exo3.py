import socket
import threading

def receive_messages(client_socket):
    try:
        while True:
            server_response = client_socket.recv(1024).decode('utf-8')
            if not server_response:
                print("La connexion au serveur a été interrompue.")
                break

            print(f"Réponse du serveur : {server_response}")

            if server_response == "arret":
                print("Le serveur a été arrêté par le client")
                break

    except ConnectionError as e:
        print(f"Erreur de connexion : {e}")

    finally:
        client_socket.close()

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', 12347)

    try:
        client_socket.connect(server_address)

        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
            client_message = input("Message du client : ")
            client_socket.send(client_message.encode('utf-8'))

            if client_message in ["arret", "bye"]:
                print("Le client se déconnecte.")
                break

    except ConnectionRefusedError:
        print("La connexion au serveur a été refusée. Assurez-vous que le serveur est en cours d'exécution.")
    except ConnectionError as e:
        print(f"Erreur de connexion : {e}")

    finally:
        client_socket.close()

if __name__ == "__main__":
    main()