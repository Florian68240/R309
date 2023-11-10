import socket

message = "bonjour"

with socket.socket() as client_socket:
    client_socket.connect(("127.0.0.1", 6500))
    client_socket.send(message.encode())
    reply = client_socket.recv(1024).decode()

print("Réponse du serveur :", reply)