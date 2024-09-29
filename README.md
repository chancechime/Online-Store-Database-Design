# Online Store Project README
===========================

## Project Overview
----------------

This project is an online store application built using Python, PyQt5, and Supabase. It features user authentication, secure password storage, and database management for product listings.

Group Members and Contributions
-------------------------------

**Chance Chime: Project Lead**

-   Database design (schema for online store)
-   User interface development (PyQt5)
-   Database integration (Supabase)

Features
--------

-   User registration and login
-   Add items with title, description, category, and price
-   Display item details and user reviews
-   Sort items in the table

Installation
------------

### Prerequisites:

-   Python 3


### Steps:

**Clone the Repository:**

`git clone https://github.com/ChanceChime/comp440.git`

# Download and Install Python 3

## Step 1: Download Python 3

1. Visit the [official Python website](https://www.python.org/downloads/).
2. Click the "Download Python 3.x.x" button. The exact version may vary.

## Step 2: Install Python 3

### Windows

1. Run the downloaded executable installer.
2. Make sure to check the box that says "Add Python to PATH".
3. Click "Install Now".

### macOS

1. Open the downloaded `.pkg` file.
2. Follow the installation steps.

### Linux

1. Open a terminal.
2. Run the following command:
   ```bash
   sudo apt-get update
   sudo apt-get install python3
   ```

**Install Dependencies:**


bash

Copy code

`pip install PyQt5 bcrypt supabase python-dotenv`

**Run the Application:**

Run in folder

`python main.py`

Usage
-----

- **Register**: Create a new user account.
- **Login**: Use your credentials to access the application.
- **Home Page**:
    -   View listed items, search, add new items, display, and manage items.
- **Display Page**:
   - Lists most expensive item in each category
   - List the users who posted at least two items that were posted on the same day, one has a category of X, and another has a category of Y
   - List all the items posted by user X, such that all the comments are "Excellent" or "Good" for these items
   - List the users who posted the most number of items on 7/4/2024; if there is a tie, list all the users who have a tie
   - Display all the users who posted some reviews, but each of them is "poor"
    - Display those users such that each item they posted so far never received any "poor" reviews 