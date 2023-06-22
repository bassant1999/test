from ast import literal_eval
from book_heaven.models import *
import csv
import json
path = "E:\\graduation project\\data\\new_data.csv"
with open(path , encoding="utf8") as f:
    csvreader = csv.reader(f)
    header = []
    header = next(csvreader)
    print(header)
    i = 0
    for row in csvreader:
        r0 = int(row[2])
        r1 = row[3]
        r2 = row[4]
        r4 = None
        if row[5]:
          r4 = int(float(row[5]))
        r5 = None
        if row[6]:
          r5 = int(float(row[6]))
        r3 = None
        if row[16]:
          r3 = json.loads(row[16].replace("\'", "\""))
          r3_ = None
          for i in r3.keys():
              if 'image/jpeg' in i or 'image/gif' in i or 'image/png' in i:
                  r3_ = i
          if(r3_):
              r3 = r3[r3_]
          else:
              r3 = None
        r6 = None
        if row[8]:
          r6 = int(float(row[8]))
        r7 = row[9]
        r8 = row[14]
        r9 = row[16]
        free =   free_books(
            Gutenberg_id = r0,
            title = r1,
            Authors = r2,
            authoryearofbirth = r4,
            authoryearofdeath = r5,
            subjects = r7,
            Image_url = r3,
            Download_count = r6,
            copy_right = r8,
            formats = r9
            )
        free.save()