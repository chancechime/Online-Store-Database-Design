import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QCloseEvent
from database import get_connection
import bcrypt
from registeruser import RegisterUser
from homepage import HomePage
from securecoding import AppDelegate, NSApplication

# Initialize Supabase connection
connection = get_connection()

class LoginUser(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.register_window = None  # Initialize register_window to None
        self.home_window = None  # Initialize home_window to None

    def initUI(self):
        self.setWindowTitle('User Login')
        self.setGeometry(100, 100, 400, 200)
        self.setFixedSize(300, 200)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        
        
        # Create widgets
        self.username_label = QLabel('Username:')
        self.username_entry = QLineEdit()
        
        self.password_label = QLabel('Password:')
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.check_login)
        
        self.register_button = QPushButton('Register')
        self.register_button.clicked.connect(self.open_register_user)
        
        self.quit_button = QPushButton('Quit')
        self.quit_button.clicked.connect(self.closeEvent)
        
        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        layout.addWidget(self.quit_button)
        
        self.setLayout(layout)
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.closeEvent(event)
        if event.key() == Qt.Key_Return:
            self.check_login()
        super().keyPressEvent(event)

    def check_login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        if not connection:
            QMessageBox.critical(self, 'Error', 'Failed to connect to the database.')
            return

        try:
            response = connection.table('user').select('password, firstName, lastName').eq('username', username).execute()

            if response.data:
                stored_password = response.data[0]['password']
                firstName = response.data[0]['firstName']
                lastName = response.data[0]['lastName']
                horse = r'''
                .''
      ._.-.___.' (`\
     //(        ( `'
    '/ )\ ).__. )
    ' <' `\ ._/'\
  the  `   \     \  is in the stable, i repeat, the horse is in the stable'''
                
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    QMessageBox.information(self, 'Welcome', f"Welcome {firstName} {lastName}!")
                    if self.home_window is None or not self.home_window.isVisible():
                        print(f"\n\t\t\tOpening home window for user, {username}!\n\t {horse} {firstName} {lastName} :D\n\n")
                        self.home_window = HomePage(firstName, lastName, username)
                        self.home_window.show()
                else:
                    QMessageBox.warning(self, 'Error', 'Invalid username or password')
            else:
                QMessageBox.warning(self, 'Error', 'Invalid username or password')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"Error while fetching user data: {e}")
            print(f"Exception during login check: {e}")

    def open_register_user(self):
        if self.register_window is None or not self.register_window.isVisible():
            self.register_window = RegisterUser()
            self.register_window.show()

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Question)
        reply.setWindowTitle('Message')
        reply.setText('Are you sure you want to quit?')
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply.setDefaultButton(QMessageBox.No)

        # Set focus policy and current button
        reply.setFocusPolicy(Qt.StrongFocus)
        yes_button = reply.button(QMessageBox.Yes)
        no_button = reply.button(QMessageBox.No)
        yes_button.setFocusPolicy(Qt.StrongFocus)
        no_button.setFocusPolicy(Qt.StrongFocus)
        no_button.setFocus()  # Set default focus to "No" button

        def navigate_buttons(event):
            if event.key() == Qt.Key_Left:
                yes_button.setFocus()
            elif event.key() == Qt.Key_Right:
                no_button.setFocus()

        reply.keyPressEvent = navigate_buttons
        result = reply.exec_()

        if result == QMessageBox.Yes or event.key() == Qt.Key_Escape:
            if self.register_window and self.register_window.isVisible():
                self.register_window.close()
            if self.home_window and self.home_window.isVisible():
                self.home_window.close()
            QApplication.quit() # Note: Don't add event.accept() here, throws an error in terminal
            print("\n\t\t\tGoodbye! :) \n\t\t\t ~ Chance\n\n")
        else:
            event.ignore()

if __name__ == "__main__":
    NSApplication.sharedApplication().setDelegate_(AppDelegate()) # To remove Secure Coding Warning
    app = QApplication(sys.argv)
    window = LoginUser()
    window.show()
    sys.exit(app.exec_())