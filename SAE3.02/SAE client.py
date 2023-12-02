import socket
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import mysql.connector

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Chat Client')

        self.label_username = QLabel('Username:')
        self.entry_username = QLineEdit()

        self.label_password = QLabel('Password:')
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)

        self.button_authenticate = QPushButton('Authenticate')
        self.button_authenticate.clicked.connect(self.authenticate)

        self.label_message = QLabel('Message:')
        self.entry_message = QLineEdit()

        self.button_send = QPushButton('Send')
        self.button_send.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.entry_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.entry_password)
        layout.addWidget(self.button_authenticate)
        layout.addWidget(self.label_message)
        layout.addWidget(self.entry_message)
        layout.addWidget(self.button_send)

        self.setLayout(layout)

    def authenticate(self):
        username = self.entry_username.text()
        password = self.entry_password.text()

        client_socket.send(username.encode())
        client_socket.send(password.encode())

        result = client_socket.recv(1024).decode()

        if result == "Authentification successful":
            QMessageBox.information(self, 'Authentification', 'Authentification réussie!')
        else:
            QMessageBox.critical(self, 'Authentification', 'Authentification échouée.')

    def send_message(self):
        message = self.entry_message.text()
        client_socket.send(message.encode())

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5556

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    app = QApplication([])
    client = ChatClient()
    client.show()
    app.exec_()
