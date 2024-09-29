import sys
import random
from database import get_connection
from additem import AddItem
from listeditem import ListedItem
from displaypage import DisplayPage
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from securecoding import AppDelegate, NSApplication

# Ensure get_connection is correctly imported and returns a valid Supabase client
connection = get_connection()

class HomePage(QWidget):
    def __init__(self, firstName, lastName, username):
        super().__init__()
        self.firstName = firstName
        self.lastName = lastName
        self.username = username
        self.initUI()
        self.additem_window = None
        self.display_window = None
        self.sort_order = [Qt.AscendingOrder] * 6  # Keep track of sort order for each column

    def initUI(self):
        self.setWindowTitle('Home Page')
        self.setGeometry(100, 100, 1000, 600)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        
        main_layout = QVBoxLayout()

        top_bar_layout = QHBoxLayout()
        
        self.search_entry = QLineEdit(self)
        self.search_entry.setPlaceholderText("Search Category...")
        top_bar_layout.addWidget(self.search_entry)
        
        welcoming = [
            "Hello", "Good day", "Greetings", "Salutations", "Welcome", "Hi", "Hey", "What's up", "Howdy", "Yo",
            "Hi there", "Hey there", "Hello, friend!", "Hiya", "Hi", "Hey", "How’s it going", "How are you",
            "Hiya", "Hey, sunshine"
        ]
        self.greeting_label = QLabel(f"{random.choice(welcoming)}, {self.firstName}!", self)
        top_bar_layout.addWidget(self.greeting_label)
        
        self.change_info_button = QPushButton(self)
        self.change_info_button.setIcon(QIcon("media/loginuser.png"))
        self.change_info_button.setIconSize(QSize(20, 20))
        self.change_info_button.setStyleSheet("QPushButton { border-radius: 35px; border: 3px solid white; background-color: grey;}")
        self.change_info_button.setFixedSize(35, 35)  # Width and height must be the same
        top_bar_layout.addWidget(self.change_info_button)

        
        main_layout.addLayout(top_bar_layout)
        
        self.product_table = QTableWidget(self)
        self.product_table.setColumnCount(7)
        self.product_table.setHorizontalHeaderLabels(["Creator", "Date", "Title", "Description", "Category", "Price", "ID"])
        self.product_table.setColumnHidden(6, True)
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.product_table.cellDoubleClicked.connect(self.view_item)    
        self.product_table.horizontalHeader().sectionClicked.connect(self.sort_table)

        self.load_data()

        main_layout.addWidget(self.product_table)

        bottom_bar_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Item", self)
        self.display_button = QPushButton("Display Item", self)
        self.delete_button = QPushButton("Delete", self)
        self.search_button = QPushButton("Search", self)
        self.reset_button = QPushButton("Reset Search", self)
        self.refresh_button = QPushButton("Refresh", self)
        self.quit_button = QPushButton("Quit", self)
        
        bottom_bar_layout.addWidget(self.add_button)
        bottom_bar_layout.addWidget(self.display_button)
        bottom_bar_layout.addWidget(self.delete_button)
        bottom_bar_layout.addWidget(self.search_button)
        bottom_bar_layout.addWidget(self.reset_button)
        bottom_bar_layout.addWidget(self.refresh_button)
        bottom_bar_layout.addWidget(self.quit_button)

        main_layout.addLayout(bottom_bar_layout)
        
        self.setLayout(main_layout)
        
        self.change_info_button.clicked.connect(self.change_info)
        self.add_button.clicked.connect(self.add_item)
        self.display_button.clicked.connect(self.display_item)
        self.delete_button.clicked.connect(self.delete_item)
        self.search_button.clicked.connect(self.search_items)
        self.reset_button.clicked.connect(self.reset_search)
        self.refresh_button.clicked.connect(self.refresh_items)
        self.quit_button.clicked.connect(self.logout)
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.logout()
        super().keyPressEvent(event)

    def load_data(self, category=None):
        try:
            if category:
                categories = category.split(', ')
                response = connection.table('items').select('id, creator, date, title, description, category, price').in_('category', categories).execute()
            else:
                response = connection.table('items').select('id, creator, date, title, description, category, price').execute()
            
            data = response.data
            
            if not data:
                QMessageBox.information(self, 'Info', 'No data found in the database.')
                return

            self.product_table.setRowCount(0)
            self.product_table.setRowCount(len(data))

            for row, item in enumerate(data):
                self.product_table.setItem(row, 0, QTableWidgetItem(item.get('creator', '')))
                self.product_table.setItem(row, 1, QTableWidgetItem(str(item.get('date', ''))))
                self.product_table.setItem(row, 2, QTableWidgetItem(item.get('title', '')))
                self.product_table.setItem(row, 3, QTableWidgetItem(item.get('description', '')))
                self.product_table.setItem(row, 4, QTableWidgetItem(item.get('category', '')))
                self.product_table.setItem(row, 5, QTableWidgetItem("$" + "{:.2f}".format(item.get('price', 0))))
                self.product_table.setItem(row, 6, QTableWidgetItem(str(item.get('id', ''))))

            self.product_table.update()
            QApplication.processEvents()
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to fetch data from the database: {e}')
    
    def sort_table(self, column):
        # Toggle the sort order
        current_order = self.sort_order[column]
        new_order = Qt.DescendingOrder if current_order == Qt.AscendingOrder else Qt.AscendingOrder
        self.sort_order[column] = new_order

        # Retrieve all data from the table
        items = []
        for row in range(self.product_table.rowCount()):
            item_data = []
            for col in range(self.product_table.columnCount()):
                item = self.product_table.item(row, col)
                item_data.append(item.text() if item else '')
            items.append(item_data)
        
        # Determine the key for sorting
        def sort_key(item):
            if column == 5:  # Price column
                try:
                    return float(item[column].replace('$', '').replace(',', ''))
                except ValueError:
                    return 0
            return item[column]

        # Sort the data
        items.sort(key=sort_key, reverse=(new_order == Qt.DescendingOrder))
        
        # Clear and repopulate the table
        self.product_table.setRowCount(0)
        self.product_table.setRowCount(len(items))
        for row, item_data in enumerate(items):
            for col, text in enumerate(item_data):
                self.product_table.setItem(row, col, QTableWidgetItem(text))
        
        self.product_table.update()

    def change_info(self):
        QMessageBox.information(self, 'Info', 'Change info functionality is not implemented yet.')
    
    def add_item(self):
        if self.additem_window is None or not self.additem_window.isVisible():
            self.additem_window = AddItem(creator=self.username)
            self.additem_window.show()
    
    def display_item(self):
        if self.display_window is None or not self.display_window.isVisible():
            self.display_window = DisplayPage()
            self.display_window.show()

    def delete_item(self):
        # QMessageBox.information(self, 'Info', 'Delete item functionality is not implemented yet.')
        # Checks if the user has selected a row and prompts the user to confirm deletion
        # If the user confirms and user is creator, the item is deleted from the database
        ## deletes the item from the database (from items database) and reviews associated with the item (from reviews database)
        # If the user confirms and user is not creator, the user is informed
        # If the user does not confirm, then window is closed
        try:
            selected_row = self.product_table.currentRow()
            if selected_row == -1:
                QMessageBox.information(self, 'Info', 'Please select an item to delete.')
                return

            title = self.product_table.item(selected_row, 2).text()
            item_id = int(self.product_table.item(selected_row, 6).text())
            creator = self.product_table.item(selected_row, 0).text()

            confirm = QMessageBox.question(self, 'Delete Item', f'Delete item {title} by {creator}?', QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                if self.username == creator:
                    response = connection.table('items').delete().eq('id', item_id).execute()
                    if response.error:
                        QMessageBox.critical(self, 'Error', f'Failed to delete item: {response.error}')
                    else:
                        QMessageBox.information(self, 'Info', f'Item {item_id} by {creator} deleted successfully.')
                        self.load_data()
                else:
                    QMessageBox.information(self, 'Info', 'You are not the creator of this item.')
            else:
                self.close()
        except ValueError as e:
            QMessageBox.critical(self, 'Error', f'Invalid item ID: {e}')
        except AttributeError as e:
            QMessageBox.critical(self, 'Error', f'Failed to retrieve item details: {e}')

    def search_items(self):
        category = self.search_entry.text().strip()
        self.load_data(category=category)

    def reset_search(self):
        self.search_entry.clear()
        self.load_data()

    def refresh_items(self):
        self.load_data()

    def logout(self):
        self.close()

    def view_item(self, row, column):
        try:
            creator = self.product_table.item(row, 0).text()
            date = self.product_table.item(row, 1).text()
            title = self.product_table.item(row, 2).text()
            description = self.product_table.item(row, 3).text()
            category = self.product_table.item(row, 4).text()
            price = self.product_table.item(row, 5).text()
            item_id = int(self.product_table.item(row, 6).text())  # Accessing hidden column 6 for 'id'
            print(f"Viewing item {item_id} by {creator}", title, description, category, price)

            self.listeditem_window = ListedItem(item_id, creator, date, title, description, category, price, self.username)
            self.listeditem_window.show()
        except AttributeError as e:
            QMessageBox.critical(self, 'Error', f'Failed to retrieve item details: {e}')
        except ValueError as e:
            QMessageBox.critical(self, 'Error', f'Invalid item ID: {e}')

if __name__ == '__main__':
    NSApplication.sharedApplication().setDelegate_(AppDelegate()) # To remove Secure Coding Warning
    app = QApplication(sys.argv)
    window = HomePage("Debug", "Mode", "debugger")
    window.show()
    sys.exit(app.exec_())