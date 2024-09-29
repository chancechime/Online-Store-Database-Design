# main.py is used to run the main program loginuser.py
from loginuser import LoginUser
from PyQt5.QtWidgets import QApplication
from securecoding import AppDelegate, NSApplication

# Run the main program
if __name__ == "__main__":
    NSApplication.sharedApplication().setDelegate_(AppDelegate()) # To remove Secure Coding Warning
    app = QApplication([])
    login_user = LoginUser()
    login_user.show()
    app.exec_()