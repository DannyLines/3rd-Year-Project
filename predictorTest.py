import csv
import time
import pickle
import sqlite3
import datetime
import requests
import threading
import traceback
import numpy as np
import pandas as pd
import streamTweets
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from flask import Flask, render_template, request, jsonify

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
    "cardiff": 17,
    "southampton": 18,
    "fulham": 19,
    "huddersfield": 20,
    "Aston Villa": 21,
    "Wigan": 22,
    "Blackburn": 23,
    "Bolton": 24,
    "Sunderland": 25,
    "Portsmouth": 26,
    "Stoke": 27,
    "Hull": 28,
    "Birmingham": 29,
    "West Brom": 30,
    "Blackpool": 31,
    "QPR": 32,
    "Norwich": 33,
    "Swansea": 34,
    "reading": 35,
    "Middlesbrough": 36

}
try:
    connection = sqlite3.connect("commentary.db")
    cursor = connection.cursor()

except:
    print("COULD NOT CONNECT TO DATABASE")


def parseTableName(input):
    parsedInput = input.replace("-", "_")
    return parsedInput

tempTableName = "FulhamChelsea3_2_2019"
tableName = parseTableName(tempTableName) + "Predictions"



def preprocess(df, label):
    new_df = df.copy()
    new_df[label+'_home_acc'] = (new_df[label+'_home_target'] / new_df[label+'_home_attempts'])
    new_df[label+'_home_acc'] = new_df[label+'_home_acc'].replace([np.inf, -np.inf], np.nan)
    new_df[label+'_home_acc'] = new_df[label+'_home_acc'].fillna(0)

    # new_df = new_df.drop(['home_form_points', 'home_form_GF', 'home_form_GA', 'home_form_GD', 'away_form_points', 'away_form_GF','away_form_GA', 'away_form_GD'],axis=1)

    new_df[label+'_away_acc'] = (new_df[label+'_away_target'] / new_df[label+'_away_attempts'])
    new_df[label+'_away_acc'] = new_df[label+'_away_acc'].replace([np.inf, -np.inf], np.nan)
    new_df[label+'_away_acc'] = new_df[label+'_away_acc'] = new_df[label+'_away_acc'].fillna(0)

    return new_df

current_match_time = 15
filename = 'MSH_PredictionModel.sav'
model = pickle.load(open(filename, 'rb'))

# Get the stats from table for time period
stats_table_name = parseTableName(tempTableName) + "stats"
form_table_name = "formTable"

# HomeTeam - DONE, Awayteam - DONE, MFH_result - DONE, home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD,
# away_points, MFH_home_sentiment, MFH_away_sentiment, MFH_home_goals - DONE, MFH_away_goals - DONE, MFH_home_pos - DONE,
# MFH_away_pos - DONE, MFH_home_attempts - DONE, MFH_away_attempts - DONE, MFH_home_target - DONE, MFH_away_target - DONE

MSH_home_pos = 0
MSH_away_pos = 0

MSH_result = 0

MSH_home_shots = 0
MSH_away_shots = 0

MSH_home_target = 0
MSH_away_target = 0

MSH_home_goals = 0
MSH_away_goals = 0

cursor.execute("select * from " + stats_table_name + " ORDER BY ID DESC")
rows = cursor.fetchall()
stat_counter = 0.0
current_time = 0
for row in rows:
    if (stat_counter == 0.0):
        current_time = time
    # SCHEMA
    # INTEGER PRIMARY KEY, matchState TEXT, homeScore INTEGER, awayScore INTEGER, time TEXT, homePossession TEXT,
    # awayPossession TEXT, homeGoalAttempts INTEGER, awayGoalAttempts INTEGER, homePasses INTEGER, awayPasses INTEGER, homeShotsTarget INTEGER, awayShotsTarget INTEGER)
    MSH_home_goals += row[2]
    MSH_away_goals += row[3]

    MSH_home_pos += int(row[5][:2])
    MSH_away_pos += int(row[6][:2])

    MSH_home_shots += int(row[7])
    MSH_away_shots += int(row[8])

    MSH_home_target += int(row[11])
    MSH_away_target += int(row[12])

    stat_counter += 1.0

MSH_home_goals = MSH_home_goals / stat_counter
MSH_away_goals = MSH_away_goals / stat_counter

MSH_home_pos = MSH_home_pos / stat_counter
MSH_away_pos = MSH_away_pos / stat_counter

MSH_home_shots = MSH_home_shots / stat_counter
MSH_away_shots = MSH_away_shots / stat_counter

MSH_home_target = MSH_home_target / stat_counter
MSH_away_target = MSH_away_target / stat_counter

if (MSH_home_goals > MSH_away_goals):
    MSH_result = 0
elif (MSH_home_goals < MSH_away_goals):
    MSH_result = 2
else:
    MSH_result = 1

# LEFT TO GET
# home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD, away_points,
# MFH_home_sentiment, MFH_away_sentiment,

# Get sentiment for time period
tweet_table_name = tempTableName + "Tweets"
cursor.execute("select * from " + tweet_table_name + " ORDER BY ID DESC")
rows = cursor.fetchall()
home_polarity = 0.0
away_polarity = 0.0
home_tweet_counter = 0.0
away_tweet_counter = 0.0
# SCHEMA
# id INTEGER PRIMARYKEY, subjectTEXT, polarityREAL, matchTimeTEXT, trueTime TEXT
homeTeam = 'fulham'
awayTeam = 'chelsea'
for row in rows:
    if (row[1].lower() == homeTeam.lower().replace('-', ' ').strip()):
        home_polarity += row[2]
        home_tweet_counter += 1
    elif (row[1].lower() == awayTeam.lower().replace('-', ' ').strip()):
        away_polarity += row[2]
        away_tweet_counter += 1

home_polarity = home_polarity / home_tweet_counter
away_polarity = away_polarity / away_tweet_counter

# LEFT TO GET
# home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD, away_points,

# SCHEMA
# INTEGER PRIMARY KEY, name TEXT, points INTEGER, GF INTEGER, GA INTEGER, GD INTEGER, date TEXT, gameCount INTEGER)
# Get form
cursor.execute("select * from formTable ORDER BY ID DESC")
rows = cursor.fetchall()
home_points = 0
away_points = 0
home_GA = 0
away_GA = 0

home_GF = 0
away_GF = 0

home_GD = 0
away_GD = 0

home_games = 0
away_games = 0

for row in rows:
    team_name = row[1]

    if (team_name.lower() == homeTeam.lower()):
        home_points = row[2]
        home_GF = row[3]
        home_GA = row[4]
        home_GD = row[5]
        home_games = row[7]
        print("home match")
    elif (team_name.lower() == awayTeam.lower()):
        away_points = row[2]
        away_GF = row[3]
        away_GA = row[4]
        away_GD = row[5]
        away_games = row[7]
        print("away match")
home_points = float(home_points) / float(home_games)
home_GF = float(home_GF) / float(home_games)
home_GA = float(home_GA) / float(home_games)
home_GD = float(home_GD) / float(home_games)

away_points = float(away_points) / float(away_games)
away_GF = float(away_GF) / float(away_games)
away_GA = float(away_GA) / float(away_games)
away_GD = float(away_GD) / float(away_games)

home_team_parsed = homeTeam.lower().replace('-', ' ')
home_team_number = name_to_number[home_team_parsed]

away_team_parsed = awayTeam.lower().replace('-', ' ')
away_team_number = name_to_number[away_team_parsed]

dataframe = pd.DataFrame([[home_team_number, away_team_number, MSH_result, home_GF, home_GA, home_GD,
                           home_points, away_GF, away_GA, away_GD, away_points, home_polarity,
                           away_polarity, MSH_home_goals, MSH_away_goals, MSH_home_pos, MSH_away_pos,
                           MSH_home_shots, MSH_away_shots, MSH_home_target, MSH_away_target]])
# Preprocess data

dataframe.columns = ['HomeTeam', 'AwayTeam', 'MSH_result', 'home_GF', 'home_GA', 'home_GD',
                     'home_points',
                     'away_GF', 'away_GA', 'away_GD', 'away_points', 'MSH_home_sentiment',
                     'MSH_away_sentiment',
                     'MSH_home_goals', 'MSH_away_goals', 'MSH_home_pos', 'MSH_away_pos',
                     'MSH_home_attempts',
                     'MSH_away_attempts', 'MSH_home_target', 'MSH_away_target']

new_data = preprocess(dataframe, 'MSH')

result = model.predict_proba(new_data)
away_team_win_prob = result[0][0]
draw_prob = result[0][1]
home_team_win_prob = result[0][2]
print(away_team_win_prob)
print(draw_prob)
print(home_team_win_prob)
# id INTEGER PRIMARY KEY, homeWin TEXT, draw TEXT, awayWin TEXT, time TEXT