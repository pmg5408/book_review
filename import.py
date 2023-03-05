import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

#engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine('postgresql://localhost:5433/pratham')

db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute(text("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)"),
                        {"isbn":isbn, "title":title, "author":author, "year":year})
    db.commit()

if __name__ == "__main__":
    main()