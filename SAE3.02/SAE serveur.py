import socket
import threading
import mysql.connector

# Connexion à la base de données MySQL
db = mysql.connector.connect(
    host="127.0.0.1",
    user="toto",
    password="toto",
    database="SAE302"
)
cursor = db.cursor()

# Initialisation de la base de données
cursor.execute('CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), password VARCHAR(255))')
cursor.execute('CREATE TABLE IF NOT EXISTS conversations (username VARCHAR(255), message TEXT)')
db.commit()

# Fonction pour gérer la connexion client
def handle_client(client_socket):
    # Authentification du client
    auth_data = client_socket.recv(1024).decode().split(';')
    username = auth_data[0]
    password = auth_data[1]

    # Vérification des identifiants dans la base de données
    cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
    user = cursor.fetchone()

    if user is None:
        client_socket.send("Authentification failed".encode())
        client_socket.close()
        return

    # Authentification réussie
    client_socket.send("Authentification successful".encode())

    while True:
        try:
            # Recevoir et enregistrer la conversation
            message = client_socket.recv(1024).decode()
            if not message:
                break  # Si le client se déconnecte, le thread se termine
            cursor.execute('INSERT INTO conversations VALUES (%s, %s)', (username, message))
            db.commit()
        except Exception as e:
            print(f"Error: {e}")
            break

    client_socket.close()

# Paramètres du serveur
host = '127.0.0.1'
port = 5557

# Mise en place du serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)

print(f"[*] Server listening on {host}:{port}")

# Attente de connexions clientes
while True:
    client, addr = server.accept()
    print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

    # Démarrer un thread pour gérer le client
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
