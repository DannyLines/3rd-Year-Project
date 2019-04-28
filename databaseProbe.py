import sqlite3
sentiment_connection = sqlite3.connect("commentary.db")
cursor = sentiment_connection.cursor()


cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='Man_CityChelsea13_1_2019Tweets'")
result = cursor.fetchall()
for row in result:
    print(result)

# cursor.execute("DROP table if exists 'SouthamptonTottenham9_2_2019Predictions'")
# cursor.execute("DROP table if exists 'SouthamptonTottenham9_2_2019tweets'")
# cursor.execute("DROP table if exists 'SouthamptonTottenham9_2_2019MatchTime'")
# cursor.execute("DROP table if exists 'SouthamptonTottenham9_2_2019'")
cursor.execute("DROP table if exists 'LiverpoolBurnley10_2_2019Predictions'")


cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
#for row in result:
    #print(result)


