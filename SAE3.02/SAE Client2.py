import socket
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextBrowser, QComboBox, QInputDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime

class ClientThread(QThread):
    """Thread pour gérer la communication client-serveur en arrière-plan."""

    message_received = pyqtSignal(str)
    verification_response = pyqtSignal(str)
    disconnected = pyqtSignal()

    def __init__(self, host, port, command, *args):
        """
        Initialise le thread client.

        :param host: Adresse IP du serveur.
        :param port: Port du serveur.
        :param command: Commande d'authentification ou d'action.
        :param args: Arguments supplémentaires pour la commande.
        """
        super().__init__()
        self.host = host
        self.port = port
        self.command = command
        self.args = args
        self.client_socket = None

    def run(self):
        """Exécute le thread. Se connecte au serveur et gère la communication."""
        try:
            # Crée et connecte le socket client au serveur
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))

            # Construit la chaîne d'authentification avec la commande et les arguments
            data = ";".join([str(arg) for arg in self.args])
            auth_data = f"{self.command};{data}"
            # Envoie les données d'authentification au serveur
            self.client_socket.send(auth_data.encode())

            while True:
                # Reçoit les messages du serveur en continu
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break

                # Émet des signaux en fonction du type de message reçu
                if message.startswith("Access to the room granted.") or message.startswith(
                        "Access to the room denied.") or message.startswith("Invalid verification action."):
                    self.verification_response.emit(message)
                else:
                    self.message_received.emit(message)
        except Exception as e:
            print(f"Error in ClientThread: {e}")
        finally:
            # Ferme le socket client et émet un signal de déconnexion
            if self.client_socket:
                self.client_socket.close()
            self.disconnected.emit()

class ChatClient(QWidget):
    """Interface graphique du client de chat PyQt."""

    message_received = pyqtSignal(str)
    verification_response = pyqtSignal(str)

    def __init__(self, host, port):
        """
        Initialise l'interface graphique du client de chat.

        :param host: Adresse IP du serveur.
        :param port: Port du serveur.
        """
        super().__init__()
        self.host = host
        self.port = port
        self.room_verification_required = ["Informatique", "Comptabilité", "Marketing"]
        self.client_thread = None
        self.username = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface graphique."""
        self.setWindowTitle('Chat Client')

        # Éléments d'interface utilisateur
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

        # Bouton d'authentification
        self.button_authenticate = QPushButton('Authenticate')
        self.button_authenticate.clicked.connect(self.authenticate)

        # Zone de message
        self.label_message = QLabel('Message:')
        self.entry_message = QLineEdit()

        # Bouton d'envoi de message (initialisé comme désactivé)
        self.button_send = QPushButton('Send')
        self.button_send.clicked.connect(self.send_message)
        self.button_send.setEnabled(True)  # Désactiver le bouton tant que l'authentification n'est pas effectuée

        self.button_create_user = QPushButton('New User')
        self.button_create_user.clicked.connect(self.handle_create_user)

        self.button_kick = QPushButton('Kick User')
        self.button_kick.clicked.connect(self.kick_user)

        self.button_ban = QPushButton('Ban User')
        self.button_ban.clicked.connect(self.ban_user)

        self.button_kill = QPushButton('Kill Server')
        self.button_kill.clicked.connect(self.kill_server)

        self.text_browser = QTextBrowser()

        # Agencement des éléments d'interface utilisateur
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
        # ... (autres éléments d'interface utilisateur)
        layout.addWidget(self.text_browser)

        self.setLayout(layout)

    def authenticate(self):
        """Méthode appelée lorsqu'un utilisateur tente de s'authentifier."""
        try:
            username = self.entry_username.text()
            password = self.entry_password.text()
            room = self.combo_box_room.currentText()

            # Crée un thread client pour gérer la communication avec le serveur
            self.client_thread = ClientThread(self.host, self.port, "AUTHENTICATE", username, password, room)
            # Connecte des signaux aux méthodes correspondantes
            self.client_thread.message_received.connect(self.receive_message)
            self.client_thread.verification_response.connect(self.handle_verification_response)
            self.client_thread.disconnected.connect(self.client_disconnected)
            # Démarre le thread client
            self.client_thread.start()

        except Exception as e:
            print(f"Error during authentication: {e}")

    def handle_verification_response(self, response):
        """Gère la réponse du serveur à la demande d'authentification."""
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
            self.button_send.setEnabled(True)  # Activer le bouton d'envoi après une authentification réussie
        elif response == "AUTH_FAIL":
            print("Authentication failed. Invalid username or password.")
        else:
            print("Unknown response:", response)

    def send_message(self):
        """Envoyer un message au serveur."""
        if self.client_thread and self.client_thread.client_socket:
            message = self.entry_message.text()
            datetime_str = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            message_with_datetime = f"{datetime_str} {message}"
            self.client_thread.client_socket.send(message_with_datetime.encode())
            self.entry_message.clear()
        else:
            print("Not connected to the server.")

    def receive_message(self, message):
        """Méthode appelée lorsqu'un message est reçu du serveur."""
        self.message_received.emit(message)

    def client_disconnected(self):
        """Gère la déconnexion du client."""
        if self.client_thread:
            self.client_thread.quit()
            self.client_thread.wait()
            self.client_thread = None  # Ajoutez cette ligne
        self.button_authenticate.setEnabled(True)
        self.button_send.setEnabled(False)

    def handle_create_user(self):
        """Gère la création d'un nouvel utilisateur."""
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
        """Gère la réponse du serveur à la création d'un nouvel utilisateur."""
        if response == "USER_CREATED":
            print("User created successfully")
        elif response == "USER_EXISTS":
            print("User already exists")
        else:
            print("Error creating user: Unknown response")

    def kick_user(self):
        """Envoie une commande au serveur pour exclure un utilisateur."""
        username = self.entry_message.text()
        self.client_thread.client_socket.send(f"/kick @{username}".encode())

    def ban_user(self):
        """Envoie une commande au serveur pour bannir un utilisateur."""
        username = self.entry_message.text()
        self.client_thread.client_socket.send(f"/ban @{username}".encode())

    def kill_server(self):
        """Envoie une commande au serveur pour arrêter le serveur."""
        self.client_thread.client_socket.send("/kill".encode())

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5558

    app = QApplication([])

    client = ChatClient(host, port)
    client.message_received.connect(client.text_browser.append)
    client.show()

    app.exec_()