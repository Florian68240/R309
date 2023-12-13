import socket
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextBrowser, QComboBox, QInputDialog
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime
import mysql.connector

# Connexion à la base de données MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    user="Flo",
    password="azerty123456",
    database="SAE302"
)

class ClientThread(QThread):
    message_received = pyqtSignal(str)
    disconnected = pyqtSignal()

    def __init__(self, host, port, command, *args):
        super().__init__()
        self.host = host
        self.port = port
        self.command = command
        self.args = args
        self.client_socket = None

    def run(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))

            data = ";".join([str(arg) for arg in self.args])
            auth_data = f"{self.command};{data}"
            self.client_socket.send(auth_data.encode())

            while True:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break
                self.message_received.emit(message)
        except Exception as e:
            print(f"Error in ClientThread: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
            self.disconnected.emit()

class ChatClient(QWidget):
    message_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client_thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Chat Client')

        self.label_username = QLabel('Username:')
        self.entry_username = QLineEdit()

        self.label_password = QLabel('Password:')
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)

        self.label_room = QLabel('Room:')
        self.combo_box_room = QComboBox()
        self.combo_box_room.addItem("Général")
        self.combo_box_room.addItem("Blabla")
        self.combo_box_room.addItem("Comptabilité")
        self.combo_box_room.addItem("Informatique")
        self.combo_box_room.addItem("Marketing")

        self.button_authenticate = QPushButton('Authenticate')
        self.button_authenticate.clicked.connect(self.authenticate)

        self.label_message = QLabel('Message:')
        self.entry_message = QLineEdit()

        self.button_send = QPushButton('Send')
        self.button_send.clicked.connect(self.send_message)
        self.button_send.setEnabled(True)

        self.button_create_user = QPushButton('New User')
        self.button_create_user.clicked.connect(self.handle_create_user)

        self.button_fetch_users = QPushButton('Fetch Users')
        self.button_fetch_users.clicked.connect(self.fetch_users)

        self.text_browser = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.entry_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.entry_password)
        layout.addWidget(self.label_room)
        layout.addWidget(self.combo_box_room)
        layout.addWidget(self.button_authenticate)
        layout.addWidget(self.label_message)
        layout.addWidget(self.entry_message)
        layout.addWidget(self.button_send)
        layout.addWidget(self.button_create_user)
        layout.addWidget(self.button_fetch_users)
        layout.addWidget(self.text_browser)

        self.setLayout(layout)

    def authenticate(self):
        try:
            username = self.entry_username.text()
            password = self.entry_password.text()
            room = self.combo_box_room.currentText()

            self.client_thread = ClientThread(self.host, self.port, "AUTHENTICATE", username, password, room)
            self.client_thread.message_received.connect(self.receive_message)
            self.client_thread.disconnected.connect(self.client_disconnected)
            self.client_thread.start()

        except Exception as e:
            print(f"Error during authentication: {e}")

    def send_message(self):
        if self.client_thread and self.client_thread.client_socket:
            message = self.entry_message.text()
            # Obtenir la date et l'heure actuelles
            QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            message_with_datetime = f" {message}"
            self.client_thread.client_socket.send(message_with_datetime.encode())
            self.entry_message.clear()
        else:
            print("Not connected to the server.")

    def receive_message(self, message):
        self.message_received.emit(message)

    def client_disconnected(self):
        self.client_thread.quit()
        self.client_thread.wait()

        self.button_authenticate.setEnabled(True)
        self.button_send.setEnabled(True)

    def handle_create_user(self):
        try:
            username, ok = QInputDialog.getText(self, 'New User', 'Enter username:')
            if ok:
                password, ok = QInputDialog.getText(self, 'New User', 'Enter password:')
                if ok:
                    self.client_thread = ClientThread(self.host, self.port, "CREATE_USER", username, password)
                    self.client_thread.message_received.connect(self.handle_create_user_response)
                    self.client_thread.disconnected.connect(self.client_disconnected)
                    self.client_thread.start()

        except Exception as e:
            print(f"Error creating user: {e}")

    def handle_create_user_response(self, response):
        if response == "USER_CREATED":
            print("User created successfully")
        elif response == "USER_EXISTS":
            print("User already exists")
        else:
            print("Error creating user: Unknown response")

    def fetch_users(self):
        try:
            self.client_thread = ClientThread(self.host, self.port, "SELECT_USERS")
            self.client_thread.message_received.connect(self.receive_message)
            self.client_thread.disconnected.connect(self.client_disconnected)
            self.client_thread.start()

        except Exception as e:
            print(f"Error fetching users: {e}")

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5557

    app = QApplication([])

    client = ChatClient(host, port)
    client.message_received.connect(client.text_browser.append)
    client.show()

    app.exec_()
