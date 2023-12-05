## https://github.com/Florian68240/R309

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QIntValidator
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from PyQt5.QtCore import QThread, pyqtSignal

class ConnexionThread(QThread):
    nouvelle_connexion = pyqtSignal()

    def __init__(self, tcp_server):
        super().__init__()
        self.tcp_server = tcp_server

    def run(self):
        # Boucle d'acceptation des connexions
        while self.tcp_server.isListening():
            if self.tcp_server.waitForNewConnection(-1):
                self.nouvelle_connexion.emit()

class ReceptionThread(QThread):
    message_recu = pyqtSignal(str)

    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    def run(self):
        while True:
            message = self.socket.readLine().data().decode()
            if message == "deco-server":
                break
            self.message_recu.emit(message)

class Fenetre(QWidget):
    # Liste globale pour stocker les connexions de sockets
    connexions_sockets = []

    def __init__(self):
        super().__init__()

        # Ajouter un attribut pour suivre l'état du serveur
        self.serveur_demarre = False

        # Paramètres par défaut
        self.adresse_serveur = "0.0.0.0"
        self.port_serveur = 10000
        self.clients_max = 5

        # Créer un serveur TCP
        self.tcp_server = QTcpServer(self)

        # Créer une instance de la thread de connexion
        self.connexion_thread = ConnexionThread(self.tcp_server)
        self.connexion_thread.nouvelle_connexion.connect(self.connexion_client)

        self.initUI()

    def initUI(self):
        # Créer des widgets
        self.label_serveur = QLabel('Serveur :')
        self.entry_serveur = QLineEdit(self)
        self.entry_serveur.setText(self.adresse_serveur)

        self.label_port = QLabel('Port :')
        self.entry_port = QLineEdit(self)
        self.entry_port.setText(str(self.port_serveur))
        validateur_port = QIntValidator()
        self.entry_port.setValidator(validateur_port)

        self.label_clients_max = QLabel('Nombre de clients maximum :')
        self.entry_clients_max = QLineEdit(self)
        self.entry_clients_max.setText(str(self.clients_max))
        validateur_clients_max = QIntValidator()
        self.entry_clients_max.setValidator(validateur_clients_max)

        self.label_clients_affichage = QLabel('Affichage des clients :')
        self.entry_clients_affichage = QLineEdit(self)
        self.entry_clients_affichage.setReadOnly(True)

        self.label_message = QLabel(self)
        self.bouton_afficher = QPushButton('Démarrer le serveur', self)
        self.label_message = QLabel(self)
        self.bouton_quitter = QPushButton('Quitter', self)

        # Connecter le bouton à la fonction toggle_serveur pour changer l'état du serveur
        self.bouton_afficher.clicked.connect(self.toggle_serveur)
        # Connecter le bouton à la fonction close pour quitter l'interface
        self.bouton_quitter.clicked.connect(self.close)

        # Créer la mise en page
        vbox = QVBoxLayout()
        vbox.addWidget(self.label_serveur)
        vbox.addWidget(self.entry_serveur)
        vbox.addWidget(self.label_port)
        vbox.addWidget(self.entry_port)

        vbox.addWidget(self.label_clients_max)
        vbox.addWidget(self.entry_clients_max)

        vbox.addWidget(self.label_clients_affichage)
        vbox.addWidget(self.entry_clients_affichage)

        vbox.addWidget(self.label_message)
        vbox.addWidget(self.bouton_afficher)
        vbox.addWidget(self.bouton_quitter)

        self.setLayout(vbox)

        # Configurer la fenêtre principale
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Interface PyQt')
        self.show()

    def toggle_serveur(self):
        if not self.serveur_demarre:
            # Démarrer le serveur avec les informations indiquées dans les fenêtres
            self.adresse_serveur = self.entry_serveur.text()
            self.port_serveur = int(self.entry_port.text())
            self.clients_max = int(self.entry_clients_max.text())

            # Appeler la fonction de démarrage du serveur dans la thread
            self.connexion_thread.start()

            if self.serveur_demarre:
                self.bouton_afficher.setText('Arrêter le serveur')
                self.entry_serveur.setReadOnly(True)
                self.entry_port.setReadOnly(True)
                self.entry_clients_max.setReadOnly(True)
                self.entry_clients_affichage.setText("Serveur démarré. Attente de clients.")
            else:
                self.entry_clients_affichage.setText("Erreur: Impossible de démarrer le serveur.")
        else:
            # Arrêter le serveur
            self.tcp_server.close()
            self.serveur_demarre = False
            self.bouton_afficher.setText('Démarrer le serveur')
            self.entry_serveur.setReadOnly(False)
            self.entry_port.setReadOnly(False)
            self.entry_clients_max.setReadOnly(False)
            self.entry_clients_affichage.setText("Serveur arrêté.")

    def __demarrage(self):
        # Démarrer le serveur en écoutant sur l'adresse et le port spécifiés
        if self.tcp_server.listen(QHostAddress(self.adresse_serveur), self.port_serveur):
            self.serveur_demarre = True
            self.entry_clients_affichage.setText("Serveur démarré. Attente de clients.")
        else:
            self.entry_clients_affichage.setText("Erreur: Impossible de démarrer le serveur.")

    def connexion_client(self):
        # Accepter la connexion d'un client
        client_socket = self.tcp_server.nextPendingConnection()
        Fenetre.connexions_sockets.append(client_socket)

        # Créer une thread de réception pour ce client
        reception_thread = ReceptionThread(client_socket)
        reception_thread.message_recu.connect(self.afficher_message_client)
        reception_thread.start()

        self.entry_clients_affichage.setText("Nouvelle connexion client.")

    def afficher_message_client(self, message):
        self.entry_clients_affichage.setText(f"Message reçu du client : {message}")

        # Ajouter ici le traitement du message, par exemple vérifier s'il s'agit de "deco-server"
        if message == "deco-server":
            # Effectuer les actions nécessaires pour gérer la déconnexion du client
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    sys.exit(app.exec_())


