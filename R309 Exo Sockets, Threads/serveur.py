# Importation du module socket pour la communication réseau
import socket

# Réponse à envoyer au client
reply = "active"

# Création d'une socket pour le serveur
server_socket = socket.socket()

# Liaison de la socket à l'adresse IP '0.0.0.0' (toutes les interfaces) et au port 6500
server_socket.bind(('0.0.0.0', 6500))

# Mise en écoute de la socket avec une file d'attente pour jusqu'à 5 connexions
server_socket.listen(5)

# Boucle infinie pour accepter les connexions entrantes
while True:
    # Acceptation d'une connexion entrante et récupération du socket de communication (conn) et de l'adresse du client (address)
    conn, address = server_socket.accept()
    print("Connexion depuis :", address)

    # Réception du message du client et décodage
    message = conn.recv(1024).decode()
    print("Message reçu :", message)

    # Envoi de la réponse au client, encodée en utilisant la méthode encode() pour la convertir en bytes
    conn.send(reply.encode())

    # Fermeture du socket de communication avec le client
    conn.close()

