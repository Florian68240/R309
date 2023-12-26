import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

class Fenetre(QWidget):
    def __init__(self):
        super().__init__()

        # Initialiser l'interface utilisateur
        self.initUI()

    def initUI(self):
        # Créer des widgets
        self.label_instruction = QLabel('Entrez votre prénom:')
        self.entry = QLineEdit(self)
        self.bouton_afficher = QPushButton('Afficher le message', self)
        self.label_message = QLabel(self)
        self.bouton_quitter = QPushButton('Quitter', self)

        # Connecter le bouton à la fonction afficher_message
        self.bouton_afficher.clicked.connect(self.afficher_message)
        # Connecter le bouton à la fonction close pour quitter l'interface
        self.bouton_quitter.clicked.connect(self.close)

        # Créer la mise en page verticale
        vbox = QVBoxLayout()
        vbox.addWidget(self.label_instruction)
        vbox.addWidget(self.entry)
        vbox.addWidget(self.bouton_afficher)
        vbox.addWidget(self.label_message)
        vbox.addWidget(self.bouton_quitter)

        # Appliquer la mise en page à la fenêtre principale
        self.setLayout(vbox)

        # Configurer la fenêtre principale
        self.setGeometry(300, 300, 300, 200)  # Définir la position et la taille de la fenêtre
        self.setWindowTitle('Interface PyQt')  # Définir le titre de la fenêtre
        self.show()  # Afficher la fenêtre

    def afficher_message(self):
        # Fonction appelée lorsque le bouton "Afficher le message" est cliqué
        prenom = self.entry.text()  # Obtenir le texte saisi dans le champ d'entrée
        message = "Bonjour " + prenom + "!"  # Créer un message personnalisé
        self.label_message.setText(message)  # Afficher le message dans le QLabel

if __name__ == '__main__':
    # Point d'entrée de l'application
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    sys.exit(app.exec_())  # Exécuter l'application et attendre la sortie
