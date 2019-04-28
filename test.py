import numpy as np
import pandas as pd
import sqlite3
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold

try:
    connection = sqlite3.connect("commentary.db")
    cursor = connection.cursor()

except:
    print("COULD NOT CONNECT TO DATABASE")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())


cursor.execute("select * from formtable ORDER BY ID DESC")
rows = cursor.fetchall()
print(rows)
for row in rows:
    print(row)
