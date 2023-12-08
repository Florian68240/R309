import socket
import threading

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
            if len(auth_data) != 3:
                raise Exception("Invalid authentication data")

            username, password, room = auth_data

            # Vérification des informations d'authentification
            if username in user_credentials and user_credentials[username]["Password"] == password:
                user_credentials[username]["Room"] = room
            else:
                raise Exception("Authentication failed")

            self.clients[client_socket] = {"username": username, "room": room}

            print(f"Client connected: {username} (Room: {room})")

            while True:
                message = client_socket.recv(1024).decode()
                if not message:
                    break

                sender_username = self.clients[client_socket]["username"]
                room = self.clients[client_socket]["room"]

                print(f"Received message from {sender_username} (Room: {room}): {message}")

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

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5557

    server = ChatServer(host, port)
    server.start()
