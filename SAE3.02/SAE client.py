import socket
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextBrowser, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal

class ClientThread(QThread):
    message_received = pyqtSignal(str)
    disconnected = pyqtSignal()

    def __init__(self, host, port, username, password, room):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = None
        self.username = username
        self.password = password
        self.room = room

    def run(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))

            auth_data = f"{self.username};{self.password};{self.room}"
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
        layout.addWidget(self.text_browser)

        self.setLayout(layout)

    def authenticate(self):
        try:
            username = self.entry_username.text()
            password = self.entry_password.text()
            room = self.combo_box_room.currentText()

            self.client_thread = ClientThread(self.host, self.port, username, password, room)
            self.client_thread.message_received.connect(self.receive_message)
            self.client_thread.disconnected.connect(self.client_disconnected)
            self.client_thread.start()

            # Perform authentication
            if self.client_thread.client_socket:
                self.button_authenticate.setEnabled(False)
                self.button_send.setEnabled(True)
            else:
                print("Socket not available.")

        except Exception as e:
            print(f"Error during authentication: {e}")


    def send_message(self):
        if self.client_thread and self.client_thread.client_socket:
            message = self.entry_message.text()
            self.client_thread.client_socket.send(message.encode())
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

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5557

    app = QApplication([])

    client = ChatClient(host, port)
    client.message_received.connect(client.text_browser.append)
    client.show()

    app.exec_()
