import csv

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
print(os.getenv("DATABASE_URL"))
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

books = csv.reader(open("./books.csv"))
insc=0
for isbn,title,author,year in books:
    if isbn == 'isbn':
        continue
    db.execute("INSERT INTO books (isbn,title,author,year_publish) values (:isbn,:title,:author,:year) ",
               {'isbn':isbn,'title':title, 'author':author, 'year':int(year)})
    insc += 1
    if insc % 100 == 0:
        print('%d no of records inserted' %insc)

print('records inserted %d' %insc)
db.commit()
