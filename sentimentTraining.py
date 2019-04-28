import sqlite3
import traceback
import pandas as pd
try:
    sentiment_connection = sqlite3.connect("commentary.db")
    cursor = sentiment_connection.cursor()
except:
    print("COULD NOT CONNECT TO DATABASE")

name_to_number = {
    "liverpool": 5,
    "man city": 2,
    "tottenham": 3,
    "chelsea": 1,
    "arsenal": 4,
    "man utd": 6,
    "leicester": 7,
    "west ham": 8,
    "watford": 9,
    "wolves": 10,
    "everton": 11,
    "bournemouth": 12,
    "brighton": 13,
    "crystal palace": 14,
    "newcastle": 15,
    "burnley": 16,
    "cardiff city": 17,
    "southampton": 18,
    "fulham": 19,
    "huddersfield": 20,
    "aston villa": 21,
    "wigan": 22,
    "blackburn": 23,
    "bolton": 24,
    "sunderland": 25,
    "portsmouth": 26,
    "stoke": 27,
    "hull": 28,
    "birmingham": 29,
    "west brom": 30,
    "blackpool": 31,
    "qpr": 32,
    "norwich": 33,
    "swansea": 34,
    "reading": 35,
    "middlesbrough": 36

}

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
home_team = "Fulham"
away_team = "Chelsea"
cursor.execute("SELECT * FROM FulhamChelsea3_2_2019stats")
rows = cursor.fetchall()

#homescore, awayscore, homepossession, awaypossession, homeattempts, awayattempts, homeOntarget, awayOnTarget
mid_first_data = [0, 0, 0, 0, 0, 0, 0, 0]
half_data = [0, 0, 0, 0, 0, 0, 0, 0]
second_half_data = [0, 0, 0, 0, 0, 0, 0, 0]

half_time_check = 0
mid_first_count = 0
half_count = 0
second_half_count = 0
for row in rows:
    split_data = row[4].split(" ")
    print(row)
    try:
        time = int(split_data[3][:2])
        if time < 30:
            mid_first_data[0] += int(row[2])
            mid_first_data[1] += int(row[3])
            mid_first_data[2] += int(row[5][:2])
            mid_first_data[3] += int(row[6][:2])
            mid_first_data[4] += int(row[7])
            mid_first_data[5] += int(row[8])
            mid_first_data[6] += int(row[11])
            mid_first_data[7] += int(row[12])
            mid_first_count += 1
        elif time < 60 and time > 30:
            half_data[0] += int(row[2])
            half_data[1] += int(row[3])
            half_data[2] += int(row[5][:2])
            half_data[3] += int(row[6][:2])
            half_data[4] += int(row[7])
            half_data[5] += int(row[8])
            half_data[6] += int(row[11])
            half_data[7] += int(row[12])
            half_count += 1
        elif time > 60:
            second_half_data[0] += int(row[2])
            second_half_data[1] += int(row[3])
            second_half_data[2] += int(row[5][:2])
            second_half_data[3] += int(row[6][:2])
            second_half_data[4] += int(row[7])
            second_half_data[5] += int(row[8])
            second_half_data[6] += int(row[11])
            second_half_data[7] += int(row[12])
            second_half_count += 1
    except Exception as e:
        print(e)
        if row[4] == 'Half Time' and half_time_check == 0:
            half_data[0] += row[2]
            half_data[1] += row[3]
            half_data[2] += int(row[5][:2])
            half_data[3] += int(row[6][:2])
            half_data[4] += row[7]
            half_data[5] += row[8]
            half_data[4] += row[11]
            half_data[4] += row[12]
            half_count += 1
            half_time_check = 1

average_first_half = [x / mid_first_count for x in mid_first_data]
#average_first_half = [0, 0, 20, 80, 0, 5, 0, 0]
average_half = [x / half_count for x in half_data]
#average_second_half = [x / second_half_count for x in second_half_data]
average_second_half = [1, 2, 36, 64, 12, 20, 5, 7]
prep_home_team = home_team.lower().replace("_", " ")
prep_away_team = away_team.lower().replace("_", " ")

home_num = name_to_number[prep_home_team]
away_num = name_to_number[prep_away_team]

#homescore, awayscore, homepossession, awaypossession, homeattempts, awayattempts, homeOntarget, awayOnTarget

form_table_name = "formTable"

cursor.execute("select * from " + form_table_name + " ORDER BY ID DESC")
rows = cursor.fetchall()
#(id INTEGER PRIMARY KEY, name TEXT, points INTEGER, GF INTEGER, GA INTEGER, GD INTEGER, date TEXT
home_GF = 0
home_GA = 0
home_GD = 0
home_points = 0

away_GF = 0
away_GA = 0
away_GD = 0
away_points = 0
for row in rows:
    if(row[1].lower().replace("-", " ") == prep_home_team):
        home_points = row[2]
        home_GF = row[3]
        home_GA = row[4]
        home_GD = row[5]
    elif(row[1].lower().replace("-", " ") == prep_away_team):
        away_points = row[2]
        away_GF = row[3]
        away_GA = row[4]
        away_GD = row[5]

tweetTable = "FulhamChelsea3_2_2019Tweets"
cursor.execute("select * from " + tweetTable + " ORDER BY ID")
rows = cursor.fetchall()
MFH_sentiment = 0
H_sentiment = 0
MSH_sentiment = 0
home_tweet_array = []
away_tweet_array = []

for row in rows:
    if(row[1].lower().strip().replace("-", " ") == prep_home_team):
        home_tweet_array.append([row[2], row[3]])

    elif(row[1].lower().strip().replace("-", " ") == prep_away_team):
        away_tweet_array.append([row[2], row[3]])

home_length = len(home_tweet_array)
away_length = len(away_tweet_array)

MFH_home_sentiment_array = home_tweet_array[:int(home_length/3)]
MFH_away_sentiment_array = away_tweet_array[:int(away_length/3)]
MFH_home_sentiment = 0
MFH_away_sentiment = 0
H_home_sentiment = 0
H_away_sentiment = 0
MSH_home_sentiment = 0
MSH_away_sentiment = 0

H_home_sentiment_array = home_tweet_array[int(home_length/3):int(2*(home_length/3))]
H_away_sentiment_array = away_tweet_array[int(home_length/3):int(2*(home_length/3))]
H_sentiment = 0

MSH_home_sentiment_array = home_tweet_array[int(2*(home_length/3)):]
MSH_away_sentiment_array = away_tweet_array[int(2*(home_length/3)):]
MFH_sentiment = 0

for home_entry, away_entry in zip(MFH_home_sentiment_array, MFH_away_sentiment_array):
    MFH_home_sentiment += home_entry[0]
    MFH_away_sentiment += away_entry[0]

for home_entry, away_entry in zip(H_home_sentiment_array, H_away_sentiment_array):
    H_home_sentiment += home_entry[0]
    H_away_sentiment += away_entry[0]

for home_entry, away_entry in zip(MSH_home_sentiment_array, MSH_away_sentiment_array):
    MSH_home_sentiment += home_entry[0]
    MSH_away_sentiment += away_entry[0]
MFH_home_sentiment = MFH_home_sentiment / len(MFH_home_sentiment_array)
MFH_away_sentiment = MFH_away_sentiment/len(MFH_away_sentiment_array)

H_home_sentiment = H_home_sentiment / len(H_home_sentiment_array)
H_away_sentiment = H_away_sentiment/len(H_away_sentiment_array)

MSH_home_sentiment = MSH_home_sentiment / len(MSH_home_sentiment_array)
MSH_away_sentiment = MSH_away_sentiment/len(MSH_away_sentiment_array)

sentiment_info = [MFH_home_sentiment, MFH_away_sentiment, H_home_sentiment, H_away_sentiment, MSH_home_sentiment, MSH_away_sentiment]
team_info = [home_num, away_num, home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD, away_points]

output_array = [team_info + sentiment_info +  average_first_half + average_half + average_second_half]
column_names = ['HomeTeam', 'AwayTeam', 'home_GF', 'home_GA', 'home_GD', 'home_points',
                'away_GF', 'away_GA', 'away_GD', 'away_points',
                'MFH_home_sentiment', 'MFH_away_sentiment', 'H_home_sentiment', 'H_away_sentiment', 'MSH_home_sentiment',
                'MSH_away_sentiment',
                'MFH_home_goals', 'MFH_away_goals', 'MFH_home_pos', 'MFH_away_pos', 'MFH_home_attempts',
                'MFH_away_attempts', 'MFH_home_target', 'MFH_away_target',
                'H_home_goals', 'H_away_goals', 'H_home_pos', 'H_away_pos', 'H_home_attempts',
                'H_away_attempts', 'H_home_target', 'H_away_target',
                'MSH_home_goals', 'MSH_away_goals', 'MSH_home_pos', 'MSH_away_pos', 'MSH_home_attempts',
                'MSH_away_attempts', 'MSH_home_target', 'MSH_away_target',
                ]
output_dataframe = pd.DataFrame(output_array, columns=column_names)
print(output_dataframe)
#output_dataframe.to_csv("training_data.csv", header=True, index=False)
with open('training_data.csv', 'a') as f:
    output_dataframe.to_csv(f, header=False, index=False)
#print(output_array)

#name TEXT, points INTEGER, GF INTEGER, GA INTEGER, GD INTEGER, date TEXT