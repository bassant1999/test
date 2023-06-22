#  path: E:\djaingo\data\goodbooks-10k\books.csv
# link: https://www.goodreads.com/book/show/2767052

from book_heaven.models import *
import csv

path = "E:\\djaingo\\data\\goodbooks-10k\\books.csv"
with open(path , encoding="utf8") as f:
    csvreader = csv.reader(f)
    header = []
    header = next(csvreader)
    i = 0
    for row in csvreader: 
        Publication_year = row[8]
        if(Publication_year == ""):
            Publication_year = None
        else:
            Publication_year = int(float(Publication_year))
        paid=  paid_books(
            Goodread_id = int(row[1]),
            title = row[10],
            original_title = row[9],
            Authors = row[7],
            link = "https://www.goodreads.com/book/show/" + str(row[1]),
            Publication_year = Publication_year,
            Average_rating = float(row[12]),
            Rating_count = int(row[13]),
            Image_url = row[21],
            small_image_url = row[22]
            )
        paid.save()
        

# 