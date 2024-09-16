# LiberCache
<!-- put in a picture or logo -->

## Introduction
`LiberCache` is a Flask-based web application that allows users to manage their personal libraries. Users can track books they've read, their progress in currently reading books, add books to their wishlist, and explore new books. The app uses an SQLite database to store book and user data, and provides features such as book logging, progress tracking, and file uploads for book cover images.

#### Video Demo: 
[CS50 Final Project: Libercache](https://youtu.be/eyr7jGwgNNk)

## Table of Contents
- [Introduction](#introduction)
- [Video Demo](#video-demo-httpsyoutubeeyr7jgwgnnk)
- [Features](#features)
- [Setup & Installation](#setup-&-installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Acknowledgements](#acknowledgements)

## Features
- **User Authentication:** Sign up, log in, and manage user sessions.
- **Book Tracking:** Add books to your library and track your reading progress.
- **Wishlist Management:** Add books to your wishlist.
- **File Uploads:** Upload cover images for books.
- **Book Statistics:** View reading progress and genre statistics.
- **Search Functionality:** Search for books by title or author.

## Setup & Installation
Below are the steps required to get this working on a Windows Subsystem for Linux:

### Prerequisites
- Python 3.x
- SQLite3
- Flask
- CS50 python module
- Virtual environment (recommended)

### Clone the repo
```bash
git clone <repository-url>
cd libercache
```
### Installing SQLite3
To install SQLite3 run the following command in your WSL Terminal in VSCode
```bash
sudo apt install sqlite3
```
### Installing Flask
```bash
pip3 install flask
pip3 install flask_session
```
### Installing the CS50 python module
```bash
pip install cs50
```
### Running the app
Run the following command from the project directory to get started
```bash
flask run
```
The app will be available at `http://127.0.0.1:5000`

## Usage
### Homepage
- Once logged in, you can view your library and wishlist. You can also see recommendations and popular books.

### Library
- View all books in your personal library with details like title, author, publication year, rating, and progress.
- Add new books, update progress, and log ratings.

### Add Book
- Use the "Add Book" form to enter the book's details, including uploading an optional cover image.

### Explore
- Browse through a curated collection of books or use the search functionality to find specific books.

### Wishlist
- Add books you plan to read to your wishlist and remove them as needed.

### Stats
- Monitor your reading progress, completed books, and progress toward a predefined goal.

## Dependencies

- [Flask](https://flask.palletsprojects.com/)
- [Flask-Session](https://pythonhosted.org/Flask-Session/)
- [Werkzeug](https://werkzeug.palletsprojects.com/)
- [CS50 Library](https://cs50.readthedocs.io/) (for database interaction)

## Configuration

- **Session Management**: Flask session is configured to use the filesystem with a secret key (`app.config['SECRET_KEY']`).
- **Database**: The app uses an SQLite database (`libercache.db`), with the `CS50` library handling SQL operations.
- **File Uploads**: Book cover images are uploaded to the `static/files` directory. Only image files with `.png`, `.jpg`, and `.jpeg` extensions are allowed.

## Project Structure
```
libercache/
├── app.py               # Main Flask application
├── libercache.db        # SQLite database
├── requirements.txt     # List of dependencies
├── static/
│   └── files/           # Folder for uploaded images
├── templates/
│   ├── index.html       # Landing page
│   ├── home.html        # Dashboard for logged-in users
│   ├── library.html     # User's personal library
│   └── ...              # Other HTML templates
└── README.md            # Project documentation
```

## Acknowledgements
This project was inspired by and built upon the knowledge gained from [CS50: Introduction to Computer Science](https://cs50.harvard.edu) by David J. Malan.
Some other helpful resources I used include:

- [Create 3D UI interactions for websites with Spline](https://youtu.be/7vMRRT6nhKI?si=prOHMZDrmC6Z46Tv) by Flux Academy.
- [Bootstrap 5 Crash Course | Website Build & Deploy](https://youtu.be/4sosXZsdy-s?si=Xc8JzWI4IY4L54yO) by Traversy Media.

