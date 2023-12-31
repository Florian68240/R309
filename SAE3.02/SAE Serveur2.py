import socket
import threading
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os

# Connexion à la base de données
db_connection = None
try:
    db_connection = mysql.connector.connect(
        host="localhost",
        user="Flo",
        password="azerty123456",
        database="SAE302"
    )
    print("Connected to MySQL database")
except Error as e:
    print(f"Error connecting to MySQL database: {e}")

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.banned_users = set()
        self.room_verification_required = {"Informatique", "Comptabilité", "Marketing"}
        self.access_requests = {}
        self.user_statuses = {}  # Dictionnaire pour stocker l'état de chaque utilisateur

    def start(self):
        # Configuration initiale du serveur
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        while True:
            # Attente de nouvelles connexions des clients
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        username = None

        try:
            # Réception des données d'authentification du client
            auth_data = client_socket.recv(1024).decode()
            if not auth_data:
                raise Exception("Invalid authentication data")

            auth_data = auth_data.split(";")
            command = auth_data[0]

            if command == "CREATE_USER":
                # Traitement de la création d'un nouvel utilisateur
                new_username, new_password = auth_data[1], auth_data[2]
                if not self.user_exists_in_database(new_username):
                    self.save_users_from_database(new_username, new_password)
                    client_socket.send("USER_CREATED".encode())
                    username = new_username
                else:
                    client_socket.send("USER_EXISTS".encode())
            elif command == "AUTHENTICATE":
                # Traitement de l'authentification d'un utilisateur existant
                username, password, room = auth_data[1], auth_data[2], auth_data[3]
                if self.authenticate_user_in_database(username, password):
                    if username in self.banned_users:
                        client_socket.send("USER_BANNED".encode())
                        return
                    elif not self.verify_room_access(username, room):
                        client_socket.send("ROOM_VERIFICATION_REQUIRED".encode())
                        return
                    else:
                        client_socket.send("AUTH_SUCCESS".encode())
                else:
                    client_socket.send("AUTH_FAIL".encode())
                    return

            # Enregistrement du nouveau client dans la liste des clients
            self.clients[client_socket] = {"username": username, "room": room}
            print(f"Client connected: {username} (Room: {room})")

            # Informez le serveur que l'utilisateur est connecté
            self.update_user_status(username, "connected")

            while True:
                # Gestion des messages reçus du client
                message = client_socket.recv(1024).decode()
                if not message:
                    break

                if message.startswith("/kick"):
                    # Commande pour exclure un utilisateur
                    self.handle_kick_command(message)
                elif message.startswith("/ban"):
                    # Commande pour bannir un utilisateur
                    self.handle_ban_command(message)
                elif message.startswith("/kill"):
                    # Commande pour arrêter le serveur
                    self.handle_kill_command()
                elif message.startswith("/room"):
                    # Commande pour changer la salle d'un utilisateur
                    self.handle_room_command(message)
                elif message.startswith("/request"):
                    # Commande pour gérer les demandes d'accès
                    self.handle_request_command(message, client_socket)
                elif message.startswith("/verification"):
                    # Commande pour gérer les vérifications d'accès
                    self.handle_verification_command(message)
                elif message.startswith("/status"):
                    # Commande pour gérer l'information d'état de l'utilisateur
                    self.handle_status_command(message)
                else:
                    # Gestion des messages de discussion réguliers
                    sender_username = self.clients[client_socket]["username"]
                    room = self.clients[client_socket]["room"]

                    print(f"Received message from {sender_username} (Room: {room}): {message}")

                    # Sauvegarde du message dans la base de données
                    self.save_message_to_database(sender_username, room, message)

                    # Diffusion du message à tous les clients de la même salle
                    for socket_in_room, data_in_room in list(self.clients.items()):
                        try:
                            if data_in_room["room"] == room:
                                socket_in_room.send(f"{sender_username} (Room: {room}): {message}".encode())
                        except:
                            del self.clients[socket_in_room]

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            # Gestion de la déconnexion du client
            print("Client disconnected")
            try:
                del self.clients[client_socket]
                if username:
                    # Informez le serveur que l'utilisateur est déconnecté
                    self.update_user_status(username, "disconnected")
            except KeyError:
                pass

            client_socket.close()

    def handle_status_command(self, message):
        # Gestion de la commande de statut
        parts = message.split(" ")
        username = parts[1].lstrip("@")
        status = parts[2]

        # Mise à jour de l'état de l'utilisateur
        self.user_statuses[username] = status

    def update_user_status(self, username, status):
        # Mise à jour de l'état de l'utilisateur
        self.user_statuses[username] = status

    def handle_kick_command(self, message):
        # Gestion de la commande d'exclusion d'un utilisateur
        username_to_kick = message.split(" ")[1].lstrip("@")

        if username_to_kick in self.clients.values():
            for client_socket, data in list(self.clients.items()):
                if data["username"] == username_to_kick:
                    client_socket.send("You have been kicked from the server.".encode())
                    del self.clients[client_socket]
                    client_socket.close()
                    break
        else:
            print(f"User {username_to_kick} not found.")

    def handle_ban_command(self, message):
        # Gestion de la commande de bannissement d'un utilisateur
        username_to_ban = message.split(" ")[1].lstrip("@")

        if username_to_ban in self.clients.values():
            for client_socket, data in list(self.clients.items()):
                if data["username"] == username_to_ban:
                    client_socket.send("You have been banned from the server.".encode())
                    del self.clients[client_socket]
                    client_socket.close()
                    self.banned_users.add(username_to_ban)
                    break
        else:
            print(f"User {username_to_ban} not found.")

    def handle_kill_command(self):
        # Gestion de la commande d'arrêt du serveur
        for client_socket in self.clients.keys():
            try:
                client_socket.send("Server is shutting down. Goodbye.".encode())
                client_socket.close()
            except:
                pass
        print("Server is shutting down.")
        os._exit(0)

    def handle_room_command(self, message):
        # Gestion de la commande de changement de salle
        parts = message.split(" ")
        username_to_room = parts[1].lstrip("@")
        room = parts[2]

        if username_to_room in self.clients.values():
            for client_socket, data in list(self.clients.items()):
                if data["username"] == username_to_room:
                    data["room"] = room
                    client_socket.send(f"You have joined the room {room}.".encode())
                    break
        else:
            print(f"User {username_to_room} not found.")

    def handle_request_command(self, message, client_socket):
        # Gestion de la commande de demande d'accès
        username_to_request = message.split(" ")[1].lstrip("@")

        self.access_requests[username_to_request] = {"room": None, "client_socket": client_socket}

    def handle_verification_command(self, message):
        # Gestion de la commande de vérification d'accès
        parts = message.split(" ")
        username = parts[1].lstrip("@")
        action = parts[2]

        if username in self.access_requests:
            if action.lower() == "allow":
                self.access_requests[username]["client_socket"].send(f"Access to the room granted.".encode())
                print(f"{username} a obtenu l'accès à la salle.")
            elif action.lower() == "deny":
                self.access_requests[username]["client_socket"].send(f"Access to the room denied.".encode())
                print(f"{username} s'est vu refuser l'accès à la salle.")
            else:
                self.access_requests[username]["client_socket"].send(f"Invalid verification action.".encode())
                print(f"Invalid verification action for {username}.")
            del self.access_requests[username]
        else:
            print(f"No access request found for {username}.")

    def save_message_to_database(self, username, room, message):
        # Enregistrement des messages dans la base de données
        cursor = db_connection.cursor()
        query = "INSERT INTO chat_messages (username, room, message, heure_envoi) VALUES (%s, %s, %s, %s)"
        values = (username, room, message, datetime.now())
        cursor.execute(query, values)
        db_connection.commit()

    def save_users_from_database(self, username, password):
        # Enregistrement des utilisateurs dans la base de données
        cursor = db_connection.cursor()
        query = "INSERT INTO utilisateur (username, password) VALUES (%s, %s)"
        values = (username, password)
        cursor.execute(query, values)
        db_connection.commit()

    def user_exists_in_database(self, username):
        # Vérification de l'existence d'un utilisateur dans la base de données
        cursor = db_connection.cursor()
        query = "SELECT * FROM utilisateur WHERE username = %s"
        values = (username,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result is not None

    def authenticate_user_in_database(self, username, password):
        # Authentification de l'utilisateur par rapport à la base de données
        cursor = db_connection.cursor()
        query = "SELECT * FROM utilisateur WHERE username = %s AND password = %s"
        values = (username, password)
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result is not None

    def verify_room_access(self, username, room):
        # Vérification d'accès à une salle spécifique
        if room in self.room_verification_required:
            return True
        else:
            return True  # Accès autorisé à tous les autres salons


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5558

    # Configuration des tables de la base de données
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            room VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            heure_envoi DATETIME
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS utilisateur (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255)
        )
    """)

    # Démarrage du serveur
    server = ChatServer(host, port)
    server.start()
