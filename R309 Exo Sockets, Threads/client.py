# Importation du module socket pour la communication réseau
import socket

# Message à envoyer au serveur
message = "bonjour"

# Création d'une socket pour le client
with socket.socket() as client_socket:
    # Connexion à l'adresse IP et au port du serveur
    client_socket.connect(("127.0.0.1", 6500))

    # Envoi du message encodé en utilisant la méthode encode() pour le convertir en bytes
    client_socket.send(message.encode())

    # Réception de la réponse du serveur et décodage
    reply = client_socket.recv(1024).decode()

# Affichage de la réponse du serveur
print("Réponse du serveur :", reply)
