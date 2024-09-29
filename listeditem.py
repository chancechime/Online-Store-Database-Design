from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from review import ReviewWindow
from database import get_connection

connection = get_connection()

class ListedItem(QWidget):
    def __init__(self, _id, creator, date, title, description, category, price, username):
        super().__init__()
        self.id = _id
        self.creator = creator
        self.date = date
        self.title = title
        self.description = description
        self.category = category
        self.price = price
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.creator_label = QLabel(f"Creator: {self.creator}")
        self.date_label = QLabel(f"Date: {self.date}")
        self.title_label = QLabel(f"Title: {self.title}")
        self.description_label = QLabel(f"Description: {self.description}")
        self.price_label = QLabel(f"Price: {self.price}")

        layout.addWidget(self.creator_label)
        layout.addWidget(self.date_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)
        layout.addWidget(self.price_label)

        self.review_button = QPushButton("Review", self)
        self.review_button.clicked.connect(self.open_review_window)
        layout.addWidget(self.review_button)

        self.reviews_label = QLabel(self)
        layout.addWidget(self.reviews_label)

        self.setLayout(layout)
        self.load_reviews()

    def load_reviews(self):
        try:
            response = connection.table('reviews').select('*').eq('id', self.id).execute()
            reviews = response.data
            if not reviews:
                self.reviews_label.setText("No one has reviewed yet")
            else:
                review_texts = []
                for review in reviews:
                    rating = review.get('rating')
                    color = self.get_rating_color(rating)
                    review_text = f"\t{review.get('username')} rated this item as {rating.capitalize()} and said: \"{review.get('description')}\""
                    review_texts.append(review_text)
                self.reviews_label.setText(f"Reviews: {str(len(reviews))}\n" + "\n".join(review_texts).center(30))
        except ValueError:
            self.reviews_label.setText("No one has reviewed yet")
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to fetch reviews: {e}')

    def get_rating_color(self, rating):
        color_map = {
            "Excellent": "purple",
            "Good": "green",
            "Fair": "yellow",
            "Poor": "red"
        }
        return color_map.get(rating, "")

    def open_review_window(self):
        self.review_window = ReviewWindow(item_id=self.id, item_creator=self.creator, username=self.username, on_review_submitted=self.load_reviews)
        self.review_window.show()