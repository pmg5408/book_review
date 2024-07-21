# Book Review Website

## Overview
This project is a book review website developed using Python, JavaScript, Flask, PostgreSQL, SQL, REST APIs, and JSON. It allows users to search for books, post and view reviews and ratings. The site integrates its own proprietary database with the Google Books API to provide a collection of over 10,000 books and 20,000 reviews. Additionally, the website has its own API endpoints that allow users to get the reviews and ratings directly from the database, a feature not provided by the Google Books API.

## Features
- **Book Search**: Users can search for books by title, author, or ISBN.
- **Review Posting**: Users can post reviews and ratings for books.
- **Review Viewing**: Users can view reviews and ratings posted by other users.
- **API Access**: Users can query the website’s own API to receive a JSON object containing book details and reviews from the database and the Google Books API.

## Demo
Here are some GIFs showcasing the functionality of the website:


## Technologies Used
- **Python**
- **JavaScript**
- **Flask**: Used as the web framework.
- **PostgreSQL**: Used for relational database management.
- **SQL**: Used for database queries through SQLAlchemy.
- **REST APIs**: Used to fetch data from the Google Books API and provide API endpoints for the website.
- **JSON**: Used for data interchange.

## Usage
- **Homepage**: Users are greeted with a registration page.
- **Registration**: Users can register by providing a username and password.
- **Login**: Registered users can log in using their credentials.
- **Search Page**: After logging in, users can search for books by title, author, or ISBN.
- **Review Page**: Users can view details about a book and post their reviews and ratings.

## API Endpoints
- **Search by Book Name**: /api/bookName/<string:bookName>
- **Search by Book Author**: /api/ISBN/<string:Author>
- **Search by Book ISBN**: /api/ISBN/<string:ISBN>

## Example
To search for books by an author named "John Doe", you can use the following endpoint:
```
GET /api/author/John Doe
```
The response will be a JSON object containing the book details and reviews.

