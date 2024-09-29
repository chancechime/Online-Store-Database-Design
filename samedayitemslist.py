import datetime
from database import get_connection
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)

# Ensure that the connection is created before the application starts
connection = get_connection()

class SameDayItems(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Users Who Posted at Least Two Items on the Same Day with Different Categories')
        self.setGeometry(100, 100, 800, 400)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        
        main_layout = QVBoxLayout()
        
        top_bar_layout = QHBoxLayout()
        
        self.category_1_entry = QLineEdit(self)
        self.category_1_entry.setPlaceholderText('Category 1...')
        top_bar_layout.addWidget(self.category_1_entry)
        
        self.category_2_entry = QLineEdit(self)
        self.category_2_entry.setPlaceholderText('Category 2...')
        top_bar_layout.addWidget(self.category_2_entry)
        
        main_layout.addLayout(top_bar_layout)
        
        self.table = QTableWidget(self)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['Username'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        main_layout.addWidget(self.table)
        
        bottom_bar_layout = QHBoxLayout()
        
        self.search_button = QPushButton('Search', self)
        self.reset_button = QPushButton('Reset Search', self)
        self.refresh_button = QPushButton('Refresh', self)
        self.quit_button = QPushButton('Quit', self)
        
        bottom_bar_layout.addWidget(self.search_button)
        bottom_bar_layout.addWidget(self.reset_button)
        bottom_bar_layout.addWidget(self.refresh_button)
        bottom_bar_layout.addWidget(self.quit_button)
        
        main_layout.addLayout(bottom_bar_layout)
        
        self.setLayout(main_layout)
        
        self.search_button.clicked.connect(self.search_users)
        self.reset_button.clicked.connect(self.reset_search)
        self.refresh_button.clicked.connect(self.refresh_table)
        self.quit_button.clicked.connect(self.closeEvent)
        
        self.load_data(category_1='', category_2='')
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.closeEvent()
        if event.key() == Qt.Key_Return:
            self.search_users()
        super().keyPressEvent(event)
        
    def load_data(self, category_1=None, category_2=None):
        startday = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        endday = datetime.datetime.combine(datetime.datetime.now(), datetime.time.max)
        
        print ("1. \"" + category_1 + "\"   2.  \"" + category_2 + "\"")
        
        try:
            if category_1 is not None and category_2 is not None:
                category_1 = category_1.strip()
                category_2 = category_2.strip()
                response = connection.table('items').select('creator').eq('category', category_1).eq('category', category_2).gte('date', startday.isoformat()).lte('date', endday.isoformat()).execute()
            elif category_1 == "" and category_2 == "":
                response = connection.table('items').select('creator').gte('date', startday.isoformat()).lte('date', endday.isoformat()).execute()
            
            if response is None:
                self.show()
                QMessageBox.critical(self, 'Error', 'Database query failed. Please try again.')
                return
            
            data = response.data if response and response.data else []
            if not data:
                self.show()
                QMessageBox.information(self, 'No Results', 'No users found for the given categories.')
                return
            
            self.table.setRowCount(0)
            self.table.setRowCount(len(data))
            
            for row, user in enumerate(data):
                if 'creator' in user:
                    username = user['creator']
                    username_item = QTableWidgetItem(username)
                    self.table.setItem(row, 0, username_item)
                else:
                    QMessageBox.critical(self, 'Error', 'Unexpected data format received from the database.')
                    return
                
            # Delete repeat usernames if same category
            for i in range(self.table.rowCount() - 1, -1, -1):
                for j in range(i - 1, -1, -1):
                    if self.table.item(i, 0) and self.table.item(j, 0) and self.table.item(i, 0).text() == self.table.item(j, 0).text():
                        if self.table.item(i, 1) and self.table.item(j, 1) and self.table.item(i, 1).text() == self.table.item(j, 1).text():
                            self.table.removeRow(i)
                            break
                
            self.table.update()
            QApplication.processEvents()
        
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to fetch data from the database: {e}')
            return
    
    def search_users(self):
        if self.category_1_entry.text() != '' and self.category_2_entry.text() != '':
            category_1 = self.category_1_entry.text().strip()
            category_2 = self.category_2_entry.text().strip()
        else:
            QMessageBox.critical(self, 'Error', 'Please fill in the two categories.')
            return
        
        self.load_data(category_1=category_1, category_2=category_2)
        
    def reset_search(self):
        self.category_1_entry.clear()
        self.category_2_entry.clear()
        self.load_data()
        
    def refresh_table(self):
        self.load_data()
        
    def closeEvent(self, event=None):
        self.close()