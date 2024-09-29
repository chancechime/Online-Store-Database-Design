from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QMessageBox
import datetime
from database import get_connection

connection = get_connection()

class ReviewWindow(QWidget):
    def __init__(self, item_id, item_creator, username, on_review_submitted):
        super().__init__()
        self.item_id = item_id
        self.item_creator = item_creator
        self.username = username
        self.on_review_submitted = on_review_submitted
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Write a Review")
        self.setGeometry(300, 300, 400, 300)
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        self.rating_label = QLabel("Rating:")
        self.rating_dropdown = QComboBox(self)
        self.rating_dropdown.addItems(["Excellent", "Good", "Fair", "Poor"])
        
        self.description_label = QLabel("Description:")
        self.description_text = QTextEdit(self)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_review)

        layout.addWidget(self.rating_label)
        layout.addWidget(self.rating_dropdown)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_text)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit_review(self):
        rating = self.rating_dropdown.currentText().strip()
        description = self.description_text.toPlainText()
        date = datetime.datetime.now().isoformat()  # Adjust date format as needed
        username = self.username
        _id = self.item_id

        # Validate rating against allowed values
        allowed_ratings = ["Excellent", "Good", "Fair", "Poor"]
        rating = rating.capitalize()  # Normalize the input
        if rating not in allowed_ratings:
            QMessageBox.critical(self, 'Error', f'Invalid rating value: {rating}')
            return

        if self.item_creator == username:
            QMessageBox.warning(self, 'Warning', 'You cannot review your own item.')
            return

        try:
            # Check if the user has already reviewed this item
            existing_reviews_response = connection.table('reviews').select('*').eq('username', username).eq('id', _id).execute()
            if existing_reviews_response.data:
                QMessageBox.warning(self, 'Warning', 'You have already reviewed this item.')
                return

            # Check if the user has reached the daily review limit of 3 reviews
            startday = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
            endday = datetime.datetime.combine(datetime.datetime.now(), datetime.time.max)
            daily_reviews_response = connection.table('reviews').select('*').eq('username', username).gte('date', startday.isoformat()).lte('date', endday.isoformat()).execute()
            if len(daily_reviews_response.data) >= 3:
                QMessageBox.warning(self, 'Warning', 'You can only give at most 3 reviews a day.')
                return

            # Insert the review data
            data = {
                "id": _id,
                "username": username,
                "description": description,
                "rating": rating.lower(),
                "date": date
            }

            response = connection.table('reviews').insert(data).execute()
            if response:  
                QMessageBox.information(self, 'Success', 'Review submitted successfully.')
                self.close()
                if self.on_review_submitted:
                    self.on_review_submitted()  # Refresh reviews in the parent widget
            else:
                raise Exception(f"Failed to submit review: {response.data}")

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to submit review: {e}')