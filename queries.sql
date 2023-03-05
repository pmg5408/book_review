CREATE TABLE userInfo (
    id SERIAl PRIMARY KEY,
    username VARCHAR NOT NULL,
    passwords VARCHAR NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year VARCHAR NOT NULL
);