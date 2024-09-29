from database import get_connection
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)

# Ensure that the connection is created before the application starts
connection =  get_connection()

class GoodItems(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Items Posted by User X with All 'Excellent' or 'Good' Comments")
        self.setGeometry(100, 100, 600, 400)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        
        main_layout = QVBoxLayout()
        
        top_bar_layout = QHBoxLayout()
        
        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText('Username...')
        top_bar_layout.addWidget(self.username_entry)
        
        main_layout.addLayout(top_bar_layout)
        
        self.table = QTableWidget(self)
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['Items'])
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
        
        self.search_button.clicked.connect(self.search_user)
        self.reset_button.clicked.connect(self.reset_search)
        self.refresh_button.clicked.connect(self.refresh_table)
        self.quit_button.clicked.connect(self.closeEvent)
        
      #  self.load_data()
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return:
            self.search_user()
        if event.key() == Qt.Key_Escape:
            self.closeEvent()
        super().keyPressEvent(event)
        
    '''List all the items posted by user X, such that all the comments are "Excellent" or "Good" for
        these items (in other words, these items must have comments, but these items don't have any
        other kinds of comments, such as "bad" or "fair" comments). User X is arbitrary and will be
        determined by the instructor.'''
    def load_data(self, username=None):
        try:
            reviews = []
            print("username: ", username)  # Debug Check 1

            if username is not None and username.strip() != '':
                username = username.strip()
                itemresponse = connection.table('items').select('id').eq('creator', username).execute()
                items = itemresponse.data
                print("items: ", items)  # Debug Check 2

                # Ensure items are not empty before continuing
                if not items:
                    QMessageBox.information(self, 'Info', 'No items found for this user.')
                    return

                idlist = [item.get('id') for item in items]
                print("idlist: ", idlist)  # Debug Check 3

                if not idlist:
                    QMessageBox.information(self, 'Info', 'No item IDs found for this user.')
                    return

                # Fetch Excellent reviews
                for _id in idlist:
                    response = connection.table('reviews').select().eq('id', _id).eq('rating', 'excellent').execute()
                    reviews.extend(response.data)
                    print("excellent_reviews_response: ", response.data)  # Debug Check 4

                # Fetch Good reviews
                for _id in idlist:
                    response = connection.table('reviews').select().eq('id', _id).eq('rating', 'good').execute()
                    reviews.extend(response.data)
                    print("good_reviews_response: ", response.data)  # Debug Check 5

            elif username is None or username.strip() == '':
                # Fetch Excellent reviews without filtering by username
                excellent_reviews_response = connection.table('reviews').select().eq('rating', 'excellent').execute()
                reviews.extend(excellent_reviews_response.data)
                print("excellent_reviews_response: ", excellent_reviews_response.data)  # Debug Check 6

                # Fetch Good reviews without filtering by username
                good_reviews_response = connection.table('reviews').select().eq('rating', 'good').execute()
                reviews.extend(good_reviews_response.data)
                print("good_reviews_response: ", good_reviews_response.data)  # Debug Check 7

            if not reviews:
                QMessageBox.information(self, 'Info', 'No reviews found matching the criteria.')
                return

            self.table.setRowCount(0)
            self.table.setRowCount(len(reviews))

            for row, review in enumerate(reviews):
                if 'item_id' in review:
                    item = review['item_id']
                    _item = QTableWidgetItem(str(item))  # Ensure the ID is converted to string for display
                    self.table.setItem(row, 0, _item)
                else:
                    QMessageBox.critical(self, 'Error', 'Unexpected data format received from the database.')
                    return

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to fetch data from the database: {e}')
            return

    def search_user(self):
        if self.username_entry.text() != '':
            username = self.username_entry.text().strip()
        else:
            QMessageBox.critical(self, 'Error', 'Please enter a username to search for.')
            return
        
        self.load_data(username=username)
    
    def reset_search(self):
        self.username_entry.clear()
        self.load_data()
        
    def refresh_table(self):
        self.load_data()
        
    def closeEvent(self, event=None):
        self.close()