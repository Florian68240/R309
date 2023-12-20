import socket
from datetime import datetime
import threading
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

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        username = None  # Initialise username to avoid scope issues

        try:
            # Receive authentication data
            auth_data = client_socket.recv(1024).decode()
            if not auth_data:
                raise Exception("Invalid authentication data")

            auth_data = auth_data.split(";")
            command = auth_data[0]

            if command == "CREATE_USER":
                # Création d'un nouvel utilisateur
                new_username, new_password = auth_data[1], auth_data[2]
                if not self.user_exists_in_database(new_username):
                    self.save_users_from_database(new_username, new_password)
                    client_socket.send("USER_CREATED".encode())
                    username = new_username  # Set username upon successful creation
                else:
                    client_socket.send("USER_EXISTS".encode())
            elif command == "AUTHENTICATE":
                # Vérification des informations d'authentification
                username, password, room = auth_data[1], auth_data[2], auth_data[3]
                if self.authenticate_user_in_database(username, password):
                    client_socket.send("AUTH_SUCCESS".encode())
                else:
                    client_socket.send("AUTH_FAIL".encode())
                    return  # Ne pas continuer si l'authentification échoue

            self.clients[client_socket] = {"username": username, "room": room}
            print(f"Client connected: {username} (Room: {room})")

            while True:
                message = client_socket.recv(1024).decode()
                if not message:
                    break

                if message.startswith("/kick"):
                    self.handle_kick_command(message)
                elif message.startswith("/ban"):
                    self.handle_ban_command(message)
                elif message.startswith("/kill"):
                    self.handle_kill_command()
                else:
                    sender_username = self.clients[client_socket]["username"]
                    room = self.clients[client_socket]["room"]

                    print(f"Received message from {sender_username} (Room: {room}): {message}")

                    # Enregistrement du message dans la base de données
                    self.save_message_to_database(sender_username, room, message)

                    for socket_in_room, data_in_room in list(self.clients.items()):
                        try:
                            if data_in_room["room"] == room:
                                socket_in_room.send(f"{sender_username} (Room: {room}): {message}".encode())
                        except:
                            # Remove broken connections
                            del self.clients[socket_in_room]

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            print("Client disconnected")
            try:
                del self.clients[client_socket]
            except KeyError:
                pass  # Handle the case where the key does not exist

            client_socket.close()

    def handle_kick_command(self, message):
        # Extrait le nom d'utilisateur à partir du message (par exemple, si le message est "/kick @Mathieu", extrayez "Mathieu")
        username_to_kick = message.split(" ")[1].lstrip("@")

        # Ajoutez la logique pour expulser l'utilisateur du serveur ou prendre toute autre mesure appropriée
        if username_to_kick in [data["username"] for data in self.clients.values()]:
            # Expulsez l'utilisateur en fermant sa connexion (vous devrez adapter cela en fonction de votre implémentation)
            for client_socket, data in list(self.clients.items()):
                if data["username"] == username_to_kick:
                    client_socket.send("You have been kicked from the server.".encode())
                    del self.clients[client_socket]
                    client_socket.close()
                    break
        else:
            # Si l'utilisateur n'est pas trouvé, envoyez un message approprié
            print(f"User {username_to_kick} not found.")

    def handle_ban_command(self, message):
        # Extrait le nom d'utilisateur à partir du message (par exemple, si le message est "/ban @Mathieu", extrayez "Mathieu")
        username_to_ban = message.split(" ")[1].lstrip("@")

        # Ajoutez la logique pour bannir l'utilisateur du serveur ou prendre toute autre mesure appropriée
        if username_to_ban in [data["username"] for data in self.clients.values()]:
            # Bannissez l'utilisateur en fermant sa connexion et prenez des mesures supplémentaires si nécessaire
            for client_socket, data in list(self.clients.items()):
                if data["username"] == username_to_ban:
                    client_socket.send("You have been banned from the server.".encode())
                    del self.clients[client_socket]
                    client_socket.close()
                    # Ajoutez une logique de bannissement ici (par exemple, ajoutez le nom d'utilisateur à une liste de bannissement)
                    break
        else:
            # Si l'utilisateur n'est pas trouvé, envoyez un message approprié
            print(f"User {username_to_ban} not found.")

    def handle_kill_command(self):
        # Ajoutez la logique pour provoquer l'arrêt du serveur et avertissez les clients avant de s'arrêter
        for client_socket in self.clients.keys():
            try:
                client_socket.send("Server is shutting down. Goodbye.".encode())
                client_socket.close()
            except:
                pass
        # Vous pouvez ajouter ici toute autre logique nécessaire avant l'arrêt du serveur
        # Ensuite, vous pouvez arrêter le thread principal ou prendre d'autres mesures selon vos besoins
        print("Server is shutting down.")
        os._exit(0)  # Notez que ceci est une manière brutale d'arrêter le serveur

    def save_message_to_database(self, username, room, message):
        # Enregistrement du message dans la base de données
        cursor = db_connection.cursor()
        query = "INSERT INTO chat_messages (username, room, message, heure_envoi) VALUES (%s, %s, %s, %s)"
        values = (username, room, message, datetime.now())
        cursor.execute(query, values)
        db_connection.commit()

    def save_users_from_database(self, username, password):
        # Enregistrement du message dans la base de données
        cursor = db_connection.cursor()
        query = "INSERT INTO utilisateur (username, password) VALUES (%s, %s)"
        values = (username, password)
        cursor.execute(query, values)
        db_connection.commit()

    def user_exists_in_database(self, username):
        # Vérifie si l'utilisateur existe déjà dans la base de données
        cursor = db_connection.cursor()
        query = "SELECT * FROM utilisateur WHERE username = %s"
        values = (username,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result is not None

    def authenticate_user_in_database(self, username, password):
        # Vérifie les informations d'authentification dans la base de données
        cursor = db_connection.cursor()
        query = "SELECT * FROM utilisateur WHERE username = %s AND password = %s"
        values = (username, password)
        cursor.execute(query, values)
        result = cursor.fetchone()

        # Vérifiez si l'utilisateur est dans la liste des utilisateurs bannis
        banned_users = []  # Remplacez ceci par la vraie liste des utilisateurs bannis
        if username in banned_users:
            return False  # L'utilisateur est banni

        return result is not None


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5557

    # Création de la table chat_messages si elle n'existe pas
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

    # Création de la table Utilisateur si elle n'existe pas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS utilisateur (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255)
        )
    """)

    server = ChatServer(host, port)
    server.start()
