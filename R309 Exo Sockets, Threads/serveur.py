import socket

reply = "active"
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 6500))
server_socket.listen(5)  # Permet jusqu'à 5 connexions en attente

while True:
    conn, address = server_socket.accept()
    print("Connexion depuis :", address)

    message = conn.recv(1024).decode()
    print("Message reçu :", message)

    conn.send(reply.encode())
    conn.close()
