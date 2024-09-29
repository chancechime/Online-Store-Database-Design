import sys
from samedayitemslist import SameDayItems
from gooditemslist import GoodItems
from database import get_connection
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from securecoding import AppDelegate, NSApplication

# Ensure that the connection is created before the application starts
connection = get_connection()

class DisplayPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.samedayitems_window = None
        self.gooditemslist_window = None
        
    def initUI(self):
        self.setWindowTitle("Display Page")
        self.setGeometry(100, 100, 400, 350)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        
        layout = QVBoxLayout()
        
        self.expensive_items_button = QPushButton("List the most expensive items in each category")
        self.expensive_items_button.clicked.connect(self.list_expensive_items)
        layout.addWidget(self.expensive_items_button)
        
        self.same_day_items_button = QPushButton("List the users who posted at least two items on the same day")
        self.same_day_items_button.clicked.connect(self.list_same_day_items)
        layout.addWidget(self.same_day_items_button)
        
        self.good_items_button = QPushButton("List all the items posted by user X with all 'Excellent' or 'Good' comments")
        self.good_items_button.clicked.connect(self.list_good_items)
        layout.addWidget(self.good_items_button)
        
        self.most_items_button = QPushButton("List the users who posted the most number of items on 7/4/2024")
        self.most_items_button.clicked.connect(self.list_most_items)
        layout.addWidget(self.most_items_button)
        
        self.poor_reviews_button = QPushButton("List all the users who posted some reviews, but each of them is 'poor'")
        self.poor_reviews_button.clicked.connect(self.list_poor_reviews)
        layout.addWidget(self.poor_reviews_button)
        
        self.good_reviews_button = QPushButton("List those users such that each item they posted so far never received any 'poor' reviews")
        self.good_reviews_button.clicked.connect(self.list_good_reviews)
        layout.addWidget(self.good_reviews_button)
        
        # Add space between buttons and close button
        layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.closeWindow)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.closeWindow()
        super().keyPressEvent(event)
        
    def list_expensive_items(self): # Show a table of the most expensive items in each category
        # Gathers the most expensive items in each category
        # The table will have 3 columns: item, category, and price
        # If one category for item, then the item will be displayed in the table
        # If multiple categories for the item, then be sure to split the item ", " and display the item in the table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Item", "Category", "Price"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        def keyPressEvent(self, event: QKeyEvent):
            if event.key() == Qt.Key_Escape:
                self.closeWindow()
            super().keyPressEvent(event)
        
        try:
            response = connection.table('items').select('*').execute()
            items = response.data
            if not items:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No items found"))
            else:
                # Create a dictionary to store the most expensive item in each category
                most_expensive_items = {}
                
                for item in items:
                    category = item.get('category')
                    price = item.get('price')
                    
                    # If the category is already in the dictionary, compare the prices
                    if category in most_expensive_items:
                        current_price = most_expensive_items[category].get('price')
                        if price > current_price:
                            most_expensive_items[category] = item
                    else:
                        most_expensive_items[category] = item
                
                # Set the number of rows in the table based on the number of categories
                self.table.setRowCount(len(most_expensive_items))
                
                # Populate the table with the most expensive items in each category
                for i, (category, item) in enumerate(most_expensive_items.items()):
                    title = item.get('title')
                    price = item.get('price')
                    
                    # If there are multiple categories for the item, split them and display in the table
                    categories = category.split(", ")
                    category_text = ", ".join(categories)
                    
                    self.table.setItem(i, 0, QTableWidgetItem(title))
                    self.table.setItem(i, 1, QTableWidgetItem(category_text))
                    self.table.setItem(i, 2, QTableWidgetItem(str(price)))
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Failed to fetch items: {e}"))
            
        self.table.setWindowTitle("Most Expensive Items in Each Category")
        self.table.setGeometry(200, 200, 600, 400)
        self.table.move(QApplication.desktop().screen().rect().center() - self.table.rect().center())
        self.table.show()
    
    def list_same_day_items(self): # Show a table of users who posted category X and Y on the same day
        if self.samedayitems_window is None or not self.samedayitems_window.isVisible():
            self.samedayitems_window = SameDayItems()
            self.samedayitems_window.show()
          
    def list_good_items(self): # Show a table of items posted by user X with all 'Excellent' or 'Good' comments
        if self.gooditemslist_window is None or not self.gooditemslist_window.isVisible():
            self.gooditemslist_window = GoodItems()
            self.gooditemslist_window.show()
    
    def list_most_items(self): # Show a table of users who posted the most number of items on 7/4/2024
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Username", "Number of Items"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        def keyPressEvent(self, event: QKeyEvent):
            if event.key() == Qt.Key_Escape:
                self.closeWindow()
            super().keyPressEvent(event)
        
        try:
            response = connection.table('items').select('*').execute()
            items = response.data
            if not items:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No items found"))
            else:
                user_items = {}
                for item in items:
                    username = item.get('creator')
                    date = item.get('date')
                    if date == '2024-08-04':
                        if username in user_items:
                            user_items[username] += 1
                        else:
                            user_items[username] = 1
                
                # Find the maximum number of items posted
                max_items = max(user_items.values())
                
                # Find the users who posted the maximum number of items
                top_users = [user for user, count in user_items.items() if count == max_items]
                
                self.table.setRowCount(len(top_users))
                for i, user in enumerate(top_users):
                    self.table.setItem(i, 0, QTableWidgetItem(user))
                    self.table.setItem(i, 1, QTableWidgetItem(str(max_items)))
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Failed to fetch items: {e}"))
        
        self.table.setWindowTitle("Users Who Posted the Most Number of Items on 7/4/2024")
        self.table.setGeometry(200, 200, 600, 400)
        self.table.move(QApplication.desktop().screen().rect().center() - self.table.rect().center())
        self.table.show()

    def list_poor_reviews(self): # Show a table of users who posted some reviews, but each of them is 'poor'
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Username"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        def keyPressEvent(self, event: QKeyEvent):
            if event.key() == Qt.Key_Escape:
                self.closeWindow()
            super().keyPressEvent(event)
        
        try:
            response = connection.table('reviews').select('*').execute()
            reviews = response.data
            if not reviews:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No reviews found"))
            else:
                usernames = set()
                for review in reviews:
                    username = review.get('username')
                    rating = review.get('rating')
                    if rating == 'poor':
                        usernames.add(username)
                
                self.table.setRowCount(len(usernames))
                for i, username in enumerate(usernames):
                    self.table.setItem(i, 0, QTableWidgetItem(username))
        except Exception as e:  
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Failed to fetch reviews: {e}"))
            
        self.table.setWindowTitle("Users Who Posted Some Reviews, But Each of Them is 'Poor'")
        self.table.setGeometry(200, 200, 300, 200)
        self.table.move(QApplication.desktop().screen().rect().center() - self.table.rect().center())
        self.table.show()
    
    def list_good_reviews(self): # Show a table of users such that each item they posted so far never received any 'poor' reviews (no poor reviews or no reviews at all)
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Username"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        def keyPressEvent(self, event: QKeyEvent):
            if event.key() == Qt.Key_Escape:
                self.closeWindow()
            super().keyPressEvent(event)
        
        try:
            response = connection.table('reviews').select('*').execute()
            reviews = response.data
            if not reviews:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No reviews found"))
            else:
                usernames = set()
                for review in reviews:
                    username = review.get('username')
                    rating = review.get('rating')
                    if rating != 'poor':
                        usernames.add(username)
                
                self.table.setRowCount(len(usernames))
                for i, username in enumerate(usernames):
                    self.table.setItem(i, 0, QTableWidgetItem(username))
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Failed to fetch reviews: {e}"))
            
        self.table.setWindowTitle("Users Who Posted Some Reviews, But Each of Them is 'Poor'")
        self.table.setGeometry(200, 200, 300, 200)
        self.table.move(QApplication.desktop().screen().rect().center() - self.table.rect().center())
        self.table.show()
    
    def closeWindow(self):
        self.close()
    
if __name__ == '__main__':
    NSApplication.sharedApplication().setDelegate_(AppDelegate()) # To remove Secure Coding Warning
    app = QApplication(sys.argv)
    display_page = DisplayPage()
    display_page.show()
    sys.exit(app.exec_())