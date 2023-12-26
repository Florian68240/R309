import socket
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextBrowser, QComboBox, QInputDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime

class ClientThread(QThread):
    message_received = pyqtSignal(str)
    verification_response = pyqtSignal(str)
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

                if message.startswith("Access to the room granted.") or message.startswith("Access to the room denied.") or message.startswith("Invalid verification action."):
                    self.verification_response.emit(message)
                else:
                    self.message_received.emit(message)
        except Exception as e:
            print(f"Error in ClientThread: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
            self.disconnected.emit()

class ChatClient(QWidget):
    message_received = pyqtSignal(str)
    verification_response = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client_thread = None
        self.username = None
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

        self.button_kick = QPushButton('Kick User')
        self.button_kick.clicked.connect(self.kick_user)

        self.button_ban = QPushButton('Ban User')
        self.button_ban.clicked.connect(self.ban_user)

        self.button_kill = QPushButton('Kill Server')
        self.button_kill.clicked.connect(self.kill_server)

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
        layout.addWidget(self.button_kick)
        layout.addWidget(self.button_ban)
        layout.addWidget(self.button_kill)
        layout.addWidget(self.text_browser)

        self.setLayout(layout)

    def authenticate(self):
        try:
            username = self.entry_username.text()
            password = self.entry_password.text()
            room = self.combo_box_room.currentText()

            self.client_thread = ClientThread(self.host, self.port, "AUTHENTICATE", username, password, room)
            self.client_thread.message_received.connect(self.receive_message)
            self.client_thread.verification_response.connect(self.handle_verification_response)
            self.client_thread.disconnected.connect(self.client_disconnected)
            self.client_thread.start()
            # Dans la méthode authenticate, lorsque l'utilisateur se connecte avec succès
            self.send_user_status("connected")

            # Lorsque l'utilisateur se déconnecte
            self.send_user_status("disconnected")

            # Lorsque l'utilisateur est absent
            self.send_user_status("away")

        except Exception as e:
            print(f"Error during authentication: {e}")

    def handle_verification_response(self, response):
        if response == "USER_BANNED":
            print("Tu as été banni du serveur.")
            self.client_thread.client_socket.close()
        elif response == "ROOM_VERIFICATION_REQUIRED":
            # Boîte de dialogue pour demander à l'utilisateur s'il veut rejoindre le salon
            reply = QMessageBox.question(self, 'Room Verification',
                                         'Veux-tu rejoindre le salon?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # L'utilisateur veut rejoindre le salon, envoyez une réponse au serveur
                self.client_thread.client_socket.send("/verification Allow".encode())
            else:
                # L'utilisateur refuse de rejoindre le salon, envoyez une réponse au serveur
                self.client_thread.client_socket.send("/verification Deny".encode())
        elif response == "AUTH_SUCCESS":
            print("Authentication successful. You have joined the server.")
        elif response == "AUTH_FAIL":
            print("Authentication failed. Invalid username or password.")
        else:
            print("Unknown response:", response)

    def send_message(self):
        if self.client_thread and self.client_thread.client_socket:
            message = self.entry_message.text()
            datetime_str = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            message_with_datetime = f"{datetime_str} {message}"
            self.client_thread.client_socket.send(message_with_datetime.encode())
            self.entry_message.clear()
        else:
            print("Not connected to the server.")

    def receive_message(self, message):
        self.message_received.emit(message)

    def send_user_status(self, status):
        if self.client_thread and self.client_thread.client_socket:
            self.client_thread.client_socket.send(f"/status {status}".encode())
        else:
            print("Not connected to the server.")


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

    def kick_user(self):
        username = self.entry_message.text()
        self.client_thread.client_socket.send(f"/kick @{username}".encode())

    def ban_user(self):
        username = self.entry_message.text()
        self.client_thread.client_socket.send(f"/ban @{username}".encode())

    def kill_server(self):
        self.client_thread.client_socket.send("/kill".encode())

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5558

    app = QApplication([])

    client = ChatClient(host, port)
    client.message_received.connect(client.text_browser.append)
    client.show()

    app.exec_()