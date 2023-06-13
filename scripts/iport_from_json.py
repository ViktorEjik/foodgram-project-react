import json
import sqlite3
from pathlib import Path

connection = sqlite3.connect('../backend/foodgram_api/db.sqlite3')
cursor = connection.cursor()


traffic = json.load(open('../data/ingredients.json'))
columns = ['name','measurement_unit']
i = 1
for row in traffic:
    keys= tuple((row[c] for c in columns))
    keys = i, keys[0], keys[1]
    print(keys)
    cursor.execute('insert into recipes_ingredient values(?,?,?)',keys)
    i+=1
    print(f'{row["name"]} data inserted Succefully')

connection.commit()
connection.close()