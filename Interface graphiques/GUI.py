import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

class Fenetre(QWidget):
    def __init__(self):
        super().__init__()

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

        # Créer la mise en page
        vbox = QVBoxLayout()
        vbox.addWidget(self.label_instruction)
        vbox.addWidget(self.entry)
        vbox.addWidget(self.bouton_afficher)
        vbox.addWidget(self.label_message)
        vbox.addWidget(self.bouton_quitter)

        self.setLayout(vbox)

        # Configurer la fenêtre principale
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Interface PyQt')
        self.show()

    def afficher_message(self):
        prenom = self.entry.text()
        message = "Bonjour " + prenom + "!"
        self.label_message.setText(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    sys.exit(app.exec_())
