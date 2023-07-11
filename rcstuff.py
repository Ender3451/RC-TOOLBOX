import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QLineEdit,
    QDialog,
    QHBoxLayout,
    QGridLayout,
)
from PyQt5.QtCore import Qt
import csv

# Penalty points for each incident
penalties = {
    "Contact": {
        "Minor contact": 1,
        "Wreck": 4,
    },
    "Driving": {
        "Off-road": 1,
        "Corner cut": 2,
        "Reckless/endangering driving": 3,
    },
    "Misbehavior": {
        "Failure to comply": 2,
        "Not listening to EM": 4,
        "Disrupting the race": 5,
    },
}

MAX_PENALTY_POINTS = 21


class RCToolbox(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_penalties = {}
        self.names = []
        self.selected_name = None  # Track the currently selected name

        self.setWindowTitle("RC Toolbox")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(50, 50, 50, 50)

        self.title_label = QLabel("RC Toolbox")
        self.title_label.setStyleSheet("font-size: 20pt; font-weight: bold;")
        self.layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        self.names_widget = QWidget(self.central_widget)
        self.names_layout = QVBoxLayout(self.names_widget)

        self.names_label = QLabel("Enter names:")
        self.names_layout.addWidget(self.names_label)

        self.names_entry = QLineEdit()
        self.names_entry.returnPressed.connect(self.add_name)
        self.names_layout.addWidget(self.names_entry)

        self.add_button = QPushButton("Add Name")
        self.add_button.clicked.connect(self.add_name)
        self.names_layout.addWidget(self.add_button)

        self.layout.addWidget(self.names_widget)

        self.output_button = QPushButton("Output Selected Penalties")
        self.output_button.clicked.connect(self.output_penalties)
        self.layout.addWidget(self.output_button, alignment=Qt.AlignCenter)

        self.penalty_buttons = {}

        self.penalty_dialog = QDialog(self)
        self.penalty_dialog.setWindowTitle("Select Penalties")

        self.import_button = QPushButton("Import Penalties")
        self.import_button.clicked.connect(self.import_penalties)
        self.layout.addWidget(self.import_button, alignment=Qt.AlignCenter)

        # Use QGridLayout for the buttons
        self.buttons_layout = QGridLayout()
        self.names_layout.addLayout(self.buttons_layout)

    def display_penalties(self, name):
        def add_penalty(offense, incident):
            self.selected_penalties[name].append((offense, incident))
            QMessageBox.information(
                self,
                "Penalty Saved",
                f"The penalty '{incident}' has been saved for {name}",
            )
            self.update_penalty_counts(name)

        def remove_penalty(offense, incident):
            self.selected_penalties[name].remove((offense, incident))
            QMessageBox.information(
                self,
                "Penalty Removed",
                f"The penalty '{incident}' has been removed for {name}",
            )
            self.update_penalty_counts(name)

        self.penalty_dialog = QDialog(self)  # Create a new penalty dialog instance
        self.penalty_dialog.setWindowTitle("Select Penalties")

        penalty_layout = QVBoxLayout(self.penalty_dialog)
        penalty_layout.setSpacing(20)

        title_label = QLabel(f"Select penalties for {name}:")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        penalty_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        for offense, penalty_list in penalties.items():
            group_label = QLabel(offense)
            group_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
            penalty_layout.addWidget(group_label, alignment=Qt.AlignLeft)

            for incident, points in penalty_list.items():
                button = QPushButton(f"{incident} ({points} penalty points)")
                button.clicked.connect(
                    lambda _, o=offense, i=incident: add_penalty(o, i)
                )
                penalty_layout.addWidget(button, alignment=Qt.AlignLeft)

        remove_layout = QHBoxLayout()
        remove_label = QLabel("Remove penalty:")
        remove_layout.addWidget(remove_label)

        for offense, incident in self.selected_penalties[name]:
            button = QPushButton(f"{incident}")
            button.clicked.connect(
                lambda _, o=offense, i=incident: remove_penalty(o, i)
            )
            remove_layout.addWidget(button, alignment=Qt.AlignLeft)

        penalty_layout.addLayout(remove_layout)

        self.penalty_dialog.exec_()

    def update_penalty_counts(self, name):
        total_points = sum(
            penalties[offense][incident]
            for offense, incident in self.selected_penalties[name]
        )
        if name in self.penalty_buttons:
            self.penalty_buttons[name].setText(f"{name}: {total_points}/{MAX_PENALTY_POINTS}")
        else:
            button = QPushButton(name)
            button.setFixedWidth(200)
            button.setFixedHeight(40)
            button.setStyleSheet(
                """
                QPushButton {
                    font-size: 12pt;
                }
                """
            )
            button.clicked.connect(lambda _, n=name: self.display_penalties(n))

            self.penalty_buttons[name] = button
            self.names_layout.addWidget(button)

        if total_points >= MAX_PENALTY_POINTS:
            self.penalty_buttons[name].setDisabled(True)
        else:
            self.penalty_buttons[name].setEnabled(True)

    def output_penalties(self):
        if not self.selected_penalties:
            QMessageBox.information(
        self, "No Penalties", "No penalties have been selected."
            )
            return

        default_path = os.path.dirname(os.path.abspath(__file__))

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Penalties", default_path, "CSV Files (*.csv)"
        )

        if file_path:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Incident", "Penalty Points"])
                for name, incidents in self.selected_penalties.items():
                    if name != "player":
                        penalty_points = 0
                        for offense, incident in incidents:
                            points = penalties[offense][incident]
                            penalty_points += points
                        writer.writerow(
                            [name, "Total Penalty Points", penalty_points]
                        )

            QMessageBox.information(
                self,
                "File Saved",
                f"The penalty details have been saved to '{file_path}'.",
            )

    def import_penalties(self):
        default_path = os.path.dirname(os.path.abspath(__file__))

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Penalties", default_path, "CSV Files (*.csv)"
        )

        if file_path:
            with open(file_path, "r", newline="") as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row
                for row in reader:
                    name, incident, points = row
                    if name not in self.selected_penalties:
                        self.names.append(name)
                        self.selected_penalties[name] = []
                        button = QPushButton(name)
                        button.setFixedWidth(200)
                        button.setFixedHeight(40)
                        button.setStyleSheet(
                            """
                            QPushButton {
                                font-size: 12pt;
                            }
                            """
                        )
                        button.clicked.connect(
                            lambda _, n=name: self.display_penalties(n)
                        )
                        self.penalty_buttons[name] = button
                        self.names_layout.addWidget(button)

                    points = int(points)
                    for offense, incidents in penalties.items():
                        if incident in incidents:
                            self.selected_penalties[name].append((offense, incident))
                            break

            QMessageBox.information(
                self,
                "Penalties Imported",
                f"The penalties have been imported from '{file_path}'.",
            )

    def add_name(self):
        name = self.names_entry.text()
        if name:
            self.names.append(name)
            self.names_entry.clear()
            self.selected_penalties[name] = []

            button = QPushButton(name)
            button.setFixedWidth(200)
            button.setFixedHeight(40)
            button.setStyleSheet(
                """
                QPushButton {
                    font-size: 12pt;
                }
                """
            )
            button.clicked.connect(lambda _, n=name: self.display_penalties(n))

            self.penalty_buttons[name] = button
            self.names_layout.addWidget(button)

        else:
            QMessageBox.warning(self, "Invalid Name", "Please enter a name.")

    def closeEvent(self, event):
        self.selected_name = None  # Reset the selected name on window close
        event.accept()

    def changeEvent(self, event):
        # Track window state changes to reset the selected name
        if event.type() == event.WindowStateChange:
            if self.isMinimized():
                self.selected_name = None
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
        QMainWindow {
           background-color: #F0F0F0;
        }

        QLabel {
            color: #444444;
        }

        QPushButton {
            background-color: #DDDDDD;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }

        QPushButton:hover {
            background-color: #CCCCCC;
        }

        QLineEdit {
            padding: 8px;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
        }
        """
    )

    toolbox = RCToolbox()
    toolbox.show()
    sys.exit(app.exec_())
