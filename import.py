import csv


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql:///books")

db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for i, t, a, y in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:ibsn, :title, :author, :year)", {"ibsn": i, "title":t, "author": a, "year": y})
    db.commit()

if __name__=="__main__":
    main()

