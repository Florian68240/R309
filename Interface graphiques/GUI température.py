from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
import sys

class TemperatureConverter(QWidget):
    def __init__(self):
        super().__init__()

        # Initialiser l'interface utilisateur
        self.init_ui()

    def init_ui(self):
        # Widgets de l'interface utilisateur
        self.label_instruction = QLabel("Entrez la température:")
        self.entry = QLineEdit()

        self.unit_combobox_from = QComboBox()
        self.unit_combobox_from.addItems(["Celsius", "Kelvin"])
        self.unit_combobox_from.setCurrentText("Celsius")

        self.unit_combobox_to = QComboBox()
        self.unit_combobox_to.addItems(["Celsius", "Kelvin"])
        self.unit_combobox_to.setCurrentText("Kelvin")

        self.label_result = QLabel()

        self.convert_button = QPushButton("Convertir")
        self.convert_button.clicked.connect(self.on_convert_button_click)

        self.help_button = QPushButton("?")
        self.help_button.clicked.connect(self.show_help_message)

        # Mise en page des widgets
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.label_instruction)
        input_layout.addWidget(self.entry)
        input_layout.addWidget(self.unit_combobox_from)
        input_layout.addWidget(QLabel("vers"))
        input_layout.addWidget(self.unit_combobox_to)

        result_layout = QHBoxLayout()
        result_layout.addWidget(self.label_result)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.help_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(result_layout)
        main_layout.addLayout(button_layout)

        # Définir la mise en page principale de la fenêtre
        self.setLayout(main_layout)
        self.setWindowTitle("Convertisseur Celsius/Kelvin")

    def on_convert_button_click(self):
        # Appelé lorsqu'on clique sur le bouton de conversion
        self.update_result()

    def update_result(self):
        # Mettre à jour le résultat de la conversion
        temperature = self.entry.text()
        unit_from = self.unit_combobox_from.currentText()
        unit_to = self.unit_combobox_to.currentText()

        try:
            if unit_from == unit_to:
                self.show_error("Veuillez choisir des unités différentes.")
            elif unit_from == "Celsius" and unit_to == "Kelvin":
                kelvin = round(float(temperature) + 273.15, 2)
                self.label_result.setText(f"Température en Kelvin: {kelvin} K")
            elif unit_from == "Kelvin" and unit_to == "Celsius":
                celsius = round(float(temperature) - 273.15, 2)
                self.label_result.setText(f"Température en Celsius: {celsius} °C")
        except ValueError:
            self.show_error("Veuillez entrer une température valide.")

    def show_error(self, message):
        # Afficher une boîte de dialogue d'erreur
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Erreur")
        msg_box.setText(message)
        msg_box.exec()

    def show_help_message(self):
        # Afficher une boîte de dialogue d'aide
        help_msg = "Permet de convertir un nombre de Kelvin à Celsius ou inversement."
        QMessageBox.information(self, "Aide", help_msg)

if __name__ == '__main__':
    # Point d'entrée de l'application
    app = QApplication(sys.argv)
    converter = TemperatureConverter()
    converter.show()
    sys.exit(app.exec())
