import socket

# Paramètres du client
HOST = '127.0.0.1'
PORT = 6500

# Configuration du client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))


# Fonction pour envoyer des messages au serveur
def send_message(message):
    client_socket.send(message.encode('utf-8'))


# Boucle principale du client
while True:
    # Saisir le message à envoyer
    message = input("Votre message (ou 'bye' pour déconnecter, 'arret' pour arrêter le serveur): ")

    # Envoyer le message au serveur
    send_message(message)

    # Vérifier le message de protocole
    if message == 'bye':
        print("Déconnexion du client.")
        client_socket.close()
        break
    elif message == 'arret':
        print("Demande d'arrêt du serveur.")
        break

    # Recevoir la réponse du serveur
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Réponse du serveur: {response}")
