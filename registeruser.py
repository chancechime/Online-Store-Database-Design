import sys
import re
import bcrypt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from database import get_connection

# Initialize Supabase connection
connection = get_connection()

class RegisterUser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Registration")
        self.setGeometry(100, 100, 300, 500)
        self.setFixedSize(300, 500)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())

        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout()

        first_name_label = QLabel("First Name:")
        layout.addWidget(first_name_label)
        self.first_name_entry = QLineEdit()
        layout.addWidget(self.first_name_entry)

        last_name_label = QLabel("Last Name:")
        layout.addWidget(last_name_label)
        self.last_name_entry = QLineEdit()
        layout.addWidget(self.last_name_entry)

        username_label = QLabel("Username:")
        layout.addWidget(username_label)
        self.username_entry = QLineEdit()
        layout.addWidget(self.username_entry)

        password_label = QLabel("Password:")
        layout.addWidget(password_label)
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        confirm_password_label = QLabel("Confirm Password:")
        layout.addWidget(confirm_password_label)
        self.confirm_password_entry = QLineEdit()
        self.confirm_password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_entry)

        email_label = QLabel("Email:")
        layout.addWidget(email_label)
        self.email_entry = QLineEdit()
        layout.addWidget(self.email_entry)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register_button_click)
        layout.addWidget(register_button)
        
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_button_click)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.cancel_button_click()
        if event.key() == Qt.Key_Return:
            self.register_button_click()
        super().keyPressEvent(event)
        
    def register_button_click(self):
        first_name = self.first_name_entry.text()
        last_name = self.last_name_entry.text()
        username = self.username_entry.text()
        password = self.password_entry.text()
        confirm_password = self.confirm_password_entry.text()
        email = self.email_entry.text()
        
        if not first_name or not last_name or not username or not password or not confirm_password or not email:
            QMessageBox.information(self, "Error", "Please fill in all fields")
        if self.check_matching_password(password, confirm_password):
            if self.is_valid_email(email):
                hashed_password = self.hash_password(password)
                self.register_user(username, hashed_password, first_name, last_name, email)
            else:
                QMessageBox.information(self, "Error", "Invalid email format")
        else:
            QMessageBox.information(self, "Error", "Passwords do not match")

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

    def register_user(self, username, hashed_password, first_name, last_name, email):
        if not connection:
            QMessageBox.critical(self, "Error", "Failed to connect to the database.")
            return

        try:
            response = connection.table('user').insert({
                'username': username,
                'password': hashed_password.decode('utf-8'),
                'firstName': first_name,
                'lastName': last_name,
                'email': email
            }).execute()

            if response:
                QMessageBox.information(self, "Success", "User registered successfully!")
                self.close()
            else:
                QMessageBox.warning(self, "Error", f"Failed to register user: {response.error}")
                print(f"Response Status: {response.status}, Error: {response.error}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error while registering user: {e}")
            print(f"Exception during user registration: {e}")
            
    def cancel_button_click(self):
        self.close()

    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def check_matching_password(self, password, confirm_password):
        return password == confirm_password