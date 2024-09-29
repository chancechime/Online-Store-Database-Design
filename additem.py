import datetime
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from database import get_connection

connection = get_connection()

class AddItem(QWidget):
    def __init__(self, creator):
        super().__init__()
        self.creator = creator
        self.setWindowTitle("Add Item")
        self.setGeometry(100, 100, 300, 500)
        self.setFixedSize(300, 300)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        
        self.create_widgets()
    
    def create_widgets(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Title:")
        layout.addWidget(title_label)
        self.title_entry = QLineEdit()
        layout.addWidget(self.title_entry)
        
        description_label = QLabel("Description:")
        layout.addWidget(description_label)
        self.description_entry = QLineEdit()
        layout.addWidget(self.description_entry)
        
        category_label = QLabel("Category:")
        layout.addWidget(category_label)
        self.category_entry = QLineEdit()
        layout.addWidget(self.category_entry)
        
        price_label = QLabel("Price:")
        layout.addWidget(price_label)
        self.price_entry = QLineEdit()
        layout.addWidget(self.price_entry)
        
        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_button_click)
        layout.addWidget(add_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_button_click)
        layout.addWidget(cancel_button)
        
        self.setLayout(layout)
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.cancel_button_click()
        if event.key() == Qt.Key_Return:
            self.add_button_click()
        super().keyPressEvent(event)
    
    def add_button_click(self):
        title = self.title_entry.text()
        description = self.description_entry.text()
        category = self.category_entry.text()
        price = self.price_entry.text()
        
        if not connection:
            QMessageBox.critical(self, 'Error', 'Failed to connect to the database.')
            return

        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Check the number of items the user has posted today
            response = connection.table('items').select('*').eq('creator', self.creator).eq('date', current_date).execute()
            
            if len(response.data) >= 2:
                QMessageBox.critical(self, 'Error', 'You can only post 2 items per day.')
                return
            
            if not title or not description or not category or not price:
                QMessageBox.critical(self, 'Error', 'All fields are required.')
                return
            
            # Insert the new item
            response = connection.table('items').insert({
                'creator': self.creator,
                'date': current_date, # Add the current date
                'title': title,
                'description': description,
                'category': category,
                'price': price
            }).execute()
            
            if response:
                QMessageBox.information(self, 'Success', 'Item added successfully.')
                self.close()
            else:
                QMessageBox.critical(self, 'Error', 'Failed to add item.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
            
    def cancel_button_click(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddItem("*TEST USER*")
    window.show()
    sys.exit(app.exec_())