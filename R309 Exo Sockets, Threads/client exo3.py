import socket
import threading

# Paramètres du client
HOST = '127.0.0.1'
PORT = 5553

# Configuration du client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))


# Fonction pour envoyer des messages au serveur
def send_message(message):
    client_socket.send(message.encode('utf-8'))


# Fonction pour gérer la réception de messages du serveur
def receive_messages():
    try:
        while True:
            # Recevoir la réponse du serveur
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Réponse du serveur: {response}")
    except ConnectionResetError:
        print("Connexion avec le serveur perdue.")


# Démarrer un thread pour recevoir les messages du serveur
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Boucle principale du client
while True:
    # Saisir le message à envoyer
    message = input("Votre message (ou 'bye' pour déconnecter, 'arret' pour arrêter le client): ")

    # Envoyer le message au serveur
    send_message(message)

    # Vérifier le message de protocole
    if message == 'bye':
        print("Déconnexion du client.")
        client_socket.close()
        break
    elif message == 'arret':
        print("Arrêt du client.")
        break
