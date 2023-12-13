import socket
from datetime import datetime
import threading
import mysql.connector
from mysql.connector import Error

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

# Dictionnaire pour stocker les informations d'authentification des utilisateurs
user_credentials = {
    "Flo": {"Password": "toto", "Room": None},
    "Mathieu": {"Password": "toto", "Room": None}
}

# Liste pour stocker les connexions des clients
client_connections = []

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
                if new_username not in user_credentials:
                    user_credentials[new_username] = {"Password": new_password, "Room": None}
                    client_socket.send("USER_CREATED".encode())
                else:
                    client_socket.send("USER_EXISTS".encode())
            elif command == "AUTHENTICATE":
                # Vérification des informations d'authentification
                username, password, room = auth_data[1], auth_data[2], auth_data[3]
                if username in user_credentials and user_credentials[username]["Password"] == password:
                    user_credentials[username]["Room"] = room
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

                sender_username = self.clients[client_socket]["username"]
                room = self.clients[client_socket]["room"]

                print(f"Received message from {sender_username} (Room: {room}): {message}")

                # Enregistrement du message dans la base de données
                self.save_message_to_database(username, room, message)

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

    def save_message_to_database(self, username, room, message):
        # Enregistrement du message dans la base de données
        cursor = db_connection.cursor()
        query = "INSERT INTO chat_messages (username, room, message, heure_envoi) VALUES (%s, %s, %s, %s)"
        values = (username, room, message, datetime.now())
        cursor.execute(query, values)
        db_connection.commit()


    def save_users_from_database(self, username):
        # Enregistrement du message dans la base de données
        cursor = db_connection.cursor()
        query = "INSERT INTO utilisateur (username) VALUES (%s)"
        value = (username)
        cursor.execute(query, value)
        db_connection.commit()

    def save_channel_from_database(self, username):
        # Enregistrement du message dans la base de données
        cursor = db_connection.cursor()
        query = "INSERT INTO channel (username) VALUES (%s)"
        value = (username)
        cursor.execute(query, value)
        db_connection.commit()



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
    db_connection.commit()


    # Création de la table Utilisateur si elle n'existe pas
    cursor = db_connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS utilisateur (
            username VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255)
        )
    """)
    db_connection.commit()

    # Création de la table Utilisateur si elle n'existe pas
    cursor = db_connection.cursor()
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS channel (
              id INT AUTO_INCREMENT PRIMARY KEY,
              username VARCHAR(255),
              message TEXT,
              heure_envoi DATETIME,
              FOREIGN KEY (utilisateur_username) REFERENCES utilisateur(username)
          )
      """)
    db_connection.commit()



    server = ChatServer(host, port)
    server.start()