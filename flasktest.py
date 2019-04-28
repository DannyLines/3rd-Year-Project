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
from sklearn.metrics import log_loss
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from selenium.webdriver.common.by import By
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import PolynomialFeatures
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

app = Flask(__name__)
matchTimeText = "-1"
@app.route("/")
def index():
    return render_template('main.html')

def parseTableName(input):
    parsedInput = input.replace("-", "_")
    return parsedInput

@app.route("/getSentimentGraph", methods=['POST', 'GET'])
def sentimentGraph():
    data = request.get_data()
    splitData = data.decode().replace("\"", "").split("__")
    print("CHECK 0")
    homeTeam = splitData[0]
    awayTeam = splitData[1]
    date_var = splitData[2]
    print("CHECK 1")
    tempTableName = homeTeam + awayTeam + date_var
    tweets_table_name = parseTableName(tempTableName) +"Tweets"

    print("CHECK 2")
    try:
        sentiment_connection = sqlite3.connect("commentary.db")
        sentiment_cursor = sentiment_connection.cursor()
    except:
        print("COULD NOT CONNECT TO DATABASE")
    print("Sentiment Graph")
    init_val = -100
    home_sentiment = [init_val] * 120
    home_count = [0] * 120
    away_sentiment = [init_val] * 120
    away_count = [0] * 120
    try:
        print("SENTIMENT GRAPH   - " + tweets_table_name)
        sentiment_cursor.execute("select * from " + tweets_table_name + " ORDER BY ID ASC")
        #TESTING ONLY ^
        #sentiment_cursor.execute("select * from " + tweets_table_name + " ORDER BY ID ASC")
        rows = sentiment_cursor.fetchall()
        for row in rows:
            if(row[3] == "finished"):
                break
            else:
                current_time = row[3].split(":")
                current_time = current_time[0]
                #print("CURRENT GRAPH TIME - " + str(current_time))
                try:
                    current_time = current_time[:2]
                except:
                    pass
                try:
                    current_time = int(current_time)
                except Exception as e:
                    print(e)
                    print("Error casting current time to int - sentimentGraph")
                    pass

                if(current_time == -1):
                    current_time = 0
                #print(row)
                if(row[1].lower() == homeTeam.lower().replace('-', ' ').strip()):
                    if(home_sentiment[current_time] == init_val):
                        home_sentiment[current_time] = 0

                    #print(row[2])
                    home_sentiment[current_time] += row[2]
                    home_count[current_time] += 1

                elif(row[1].lower() == awayTeam.lower().replace('-', ' ').strip()):
                    if (away_sentiment[current_time] == init_val):
                        away_sentiment[current_time] = 0
                    away_sentiment[current_time] += row[2]
                    away_count[current_time] += 1

        for index, entry in enumerate(home_sentiment):
            try:
                home_sentiment[index] = entry / home_count[index]
            except Exception as e:
                print("Home - sentiment graph division exception")
                print(e)
                home_sentiment[index] = init_val

        for index, entry in enumerate(away_sentiment):
            try:
                away_sentiment[index] = entry / home_count[index]
            except Exception as e:
                print("Away - sentiment graph division exception")
                print(e)
                away_sentiment[index] = init_val

        print(home_sentiment)
        print(away_sentiment)

        result = [home_sentiment, away_sentiment]
        return jsonify(result)
        print("sentiment end")
    except Exception as e:
        print(e)
        print("Exception raised sentiment graph!")
    return jsonify(0)

@app.route("/getPureSentimentPredictions", methods=['POST', 'GET'])
def sentimentPredictions():
    try:
        try:
            connection = sqlite3.connect("commentary.db")
            cursor = connection.cursor()

        except:
            print("COULD NOT CONNECT TO DATABASE")

        data = request.get_data()
        splitData = data.decode().replace("\"", "").split("__")
        homeTeam = splitData[0]
        awayTeam = splitData[1]
        print("SPLIT DATA" + str(splitData[2]))
        tempTableName = homeTeam + awayTeam + splitData[2]
        tableName = parseTableName(tempTableName) + "Predictions"

        cursor.execute("select * from " + tableName + " ORDER BY ID DESC")
        rows = cursor.fetchall()
        home_team_prob = 0
        draw_prob = 0
        away_team_prob = 0
        print("GET MODEL PREDICTIONS ROWS")
        for row in rows:
            print(row)
            if(row[5] == 0):
                home_team_prob = row[1]
                draw_prob = row[2]
                away_team_prob = row[3]
                break

        return_result = str(home_team_prob) + "___" + str(draw_prob) + "___" + str(away_team_prob)
        print("returninggg")
        return jsonify(return_result)
    except:
        print("get model predictions error")

@app.route("/getModelPredictions", methods=['POST', 'GET'])
def modelPredictions():
    try:
        try:
            connection = sqlite3.connect("commentary.db")
            cursor = connection.cursor()

        except:
            print("COULD NOT CONNECT TO DATABASE")

        data = request.get_data()
        splitData = data.decode().replace("\"", "").split("__")
        homeTeam = splitData[0]
        awayTeam = splitData[1]
        print("SPLIT DATA" + str(splitData[2]))
        tempTableName = homeTeam + awayTeam + splitData[2]
        tableName = parseTableName(tempTableName) + "Predictions"

        cursor.execute("select * from " + tableName + " ORDER BY ID DESC")
        rows = cursor.fetchall()
        home_team_prob = 0
        draw_prob = 0
        away_team_prob = 0
        print("GET MODEL PREDICTIONS ROWS")
        for row in rows:
            print(row)
            if(row[5] == 1):
                home_team_prob = row[1]
                draw_prob = row[2]
                away_team_prob = row[3]
                break

        return_result = str(home_team_prob) + "___" + str(draw_prob) + "___" + str(away_team_prob)
        print("returninggg")
        return jsonify(return_result)
    except:
        print("get model predictions error")

@app.route("/machineLearningModel", methods=['POST', 'GET'])
def model():
    print("MODEL CALLED")
    try:
        connection = sqlite3.connect("commentary.db")
        cursor = connection.cursor()

    except:
        print("COULD NOT CONNECT TO DATABASE")

    data = request.get_data()
    splitData = data.decode().replace("\"", "").split("__")
    homeTeam = splitData[0]
    awayTeam = splitData[1]
    print("SPLIT DATA" + str(splitData[2]))
    tempTableName = parseTableName(homeTeam + awayTeam + splitData[2])
    tableName = parseTableName(tempTableName) + "Predictions"

    pure_sentiment_model_id = 0
    intelligent_model_id = 1

    # Does table exist
    #   TESTING PURPOSES
    cursor.execute("DROP TABLE if exists " + tableName)
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + tableName + "';")
    result = cursor.fetchone()
    number_of_rows = result[0]

    if (number_of_rows == 0):
        create_table_string = "create table if not exists '" + tableName + "' (id INTEGER PRIMARY KEY, homeWin TEXT, draw TEXT, awayWin TEXT, time TEXT, modelID INTEGER)"
        cursor.execute(create_table_string)

        match_time_table_name = homeTeam.lower().replace("-", "_") + awayTeam.lower().replace("-", "_") + splitData[2] + "MatchTime"

        def machineModelMethod():
            current_match_time = 0
            while(True):
                time.sleep(5)
                # Need to know the current time
                cursor.execute("select * from " + tempTableName + "stats ORDER BY ID DESC")
                rows = cursor.fetchall()
                for row in rows:
                    current_match_time = row[4].split(":")
                    current_match_time = current_match_time[0]
                    try:
                        current_match_time = int(current_match_time)
                    except:
                        print("match time is not an integer")
                    break

                def preprocess(df, label):
                    new_df = df.copy()
                    new_df[label + '_home_acc'] = (new_df[label + '_home_target'] / new_df[label + '_home_attempts'])
                    new_df[label + '_home_acc'] = new_df[label + '_home_acc'].replace([np.inf, -np.inf], np.nan)
                    new_df[label + '_home_acc'] = new_df[label + '_home_acc'].fillna(0)

                    # new_df = new_df.drop(['home_form_points', 'home_form_GF', 'home_form_GA', 'home_form_GD', 'away_form_points', 'away_form_GF','away_form_GA', 'away_form_GD'],axis=1)

                    new_df[label + '_away_acc'] = (new_df[label + '_away_target'] / new_df[label + '_away_attempts'])
                    new_df[label + '_away_acc'] = new_df[label + '_away_acc'].replace([np.inf, -np.inf], np.nan)
                    new_df[label + '_away_acc'] = new_df[label + '_away_acc'] = new_df[label + '_away_acc'].fillna(0)

                    return new_df

                cursor.execute("select * from " + tempTableName + "stats ORDER BY ID DESC")
                rows = cursor.fetchall()
                for row in rows:
                    if(row[1] == 1):
                        streamTweets.current_match_time = -1
                        print("Match finished so terminating script")
                        return
                    break
                # Then evaluate which model to use

                home_team_win_prob = 0
                draw_prob = 0
                away_team_win_prob = 0
                try:
                    print("CURRENT MATCH TIME -- " + str(current_match_time))
                    if(current_match_time > 0 and current_match_time < 30):
                        filename = 'MFH_PredictionModel.sav'
                        model = pickle.load(open(filename, 'rb'))

                        pure_filename = 'MFH_PureSentiment_PredictionModel.sav'
                        pure_model = pickle.load(open(pure_filename, 'rb'))

                        # Get the stats from table for time period
                        stats_table_name = parseTableName(tempTableName) + "stats"
                        form_table_name = "formTable"

                        # HomeTeam - DONE, Awayteam - DONE, MFH_result - DONE, home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD,
                        # away_points, MFH_home_sentiment, MFH_away_sentiment, MFH_home_goals - DONE, MFH_away_goals - DONE, MFH_home_pos - DONE,
                        # MFH_away_pos - DONE, MFH_home_attempts - DONE, MFH_away_attempts - DONE, MFH_home_target - DONE, MFH_away_target - DONE

                        MFH_home_pos = 0
                        MFH_away_pos = 0

                        MFH_result = 0

                        MFH_home_shots = 0
                        MFH_away_shots = 0

                        MFH_home_target = 0
                        MFH_away_target = 0

                        MFH_home_goals = 0
                        MFH_away_goals = 0

                        cursor.execute("select * from " + stats_table_name + " ORDER BY ID DESC")
                        rows = cursor.fetchall()
                        stat_counter = 0.0
                        current_time = 0
                        for row in rows:
                            if(stat_counter == 0.0):
                                current_time = time
                            #SCHEMA
                            #INTEGER PRIMARY KEY, matchState TEXT, homeScore INTEGER, awayScore INTEGER, time TEXT, homePossession TEXT,
                            # awayPossession TEXT, homeGoalAttempts INTEGER, awayGoalAttempts INTEGER, homePasses INTEGER, awayPasses INTEGER, homeShotsTarget INTEGER, awayShotsTarget INTEGER)
                            time_entry = row[4].split(":")
                            time_entry = time_entry[0]
                            if(time_entry != 'finished'):
                                time_entry = int(time_entry)

                            print("TIME ENTRY - " + str(time_entry))
                            if(time_entry >= 30 and time_entry <= 60):
                                MFH_home_goals += row[2]
                                MFH_away_goals += row[3]

                                MFH_home_pos += int(row[5][:2])
                                MFH_away_pos += int(row[6][:2])

                                MFH_home_shots += int(row[7])
                                MFH_away_shots += int(row[8])

                                MFH_home_target += int(row[11])
                                MFH_away_target += int(row[12])

                                stat_counter += 1.0
                        try:
                            try:
                                MFH_home_goals = MFH_home_goals / stat_counter
                                MFH_away_goals = MFH_away_goals / stat_counter

                                MFH_home_pos = MFH_home_pos/ stat_counter
                                MFH_away_pos = MFH_away_pos / stat_counter

                                MFH_home_shots =  MFH_home_shots / stat_counter
                                MFH_away_shots = MFH_away_shots / stat_counter

                                MFH_home_target =  MFH_home_target / stat_counter
                                MFH_away_target = MFH_away_target / stat_counter
                            except:
                                pass

                            if(MFH_home_goals > MFH_away_goals):
                                MFH_result = 0
                            elif(MFH_home_goals < MFH_away_goals):
                                MFH_result = 2
                            else:
                                MFH_result = 1

                            # LEFT TO GET
                            # home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD, away_points,
                            # MFH_home_sentiment, MFH_away_sentiment,

                            # Get sentiment for time period
                            tweet_table_name = tempTableName+"Tweets"
                            cursor.execute("select * from " + tweet_table_name + " ORDER BY ID DESC")
                            rows = cursor.fetchall()
                            home_polarity = 0.0
                            away_polarity = 0.0
                            home_tweet_counter = 0.0
                            away_tweet_counter = 0.0
                            #SCHEMA
                            #id INTEGER PRIMARYKEY, subjectTEXT, polarityREAL, matchTimeTEXT, trueTime TEXT
                            for row in rows:
                                if(row[1].lower() == homeTeam.lower().replace('-', ' ').strip()):
                                    home_polarity += row[2]
                                    home_tweet_counter += 1
                                elif(row[1].lower() == awayTeam.lower().replace('-', ' ').strip()):
                                    away_polarity += row[2]
                                    away_tweet_counter += 1

                            try:
                                home_polarity = home_polarity / home_tweet_counter
                            except:
                                home_polarity = 0

                            try:
                                away_polarity = away_polarity / away_tweet_counter
                            except:
                                away_polarity = 0

                            pure_sentiment_df = pd.DataFrame([[home_polarity, away_polarity]])

                            result = pure_model.predict_proba(pure_sentiment_df)
                            away_team_win_prob = result[0][0]
                            draw_prob = result[0][1]
                            home_team_win_prob = result[0][2]

                            cursor.execute(
                                "INSERT INTO " + tableName + " (homeWin, draw, awayWin, time, modelID) VALUES(?,?,?,?,?)",
                                (home_team_win_prob, draw_prob, away_team_win_prob, current_match_time,
                                 pure_sentiment_model_id))
                            connection.commit()

                            # LEFT TO GET
                            # home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD, away_points,

                            #SCHEMA
                            #INTEGER PRIMARY KEY, name TEXT, points INTEGER, GF INTEGER, GA INTEGER, GD INTEGER, date TEXT, gameCount INTEGER)
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
                                if(team_name.lower() == homeTeam.lower()):
                                    home_points = row[2]
                                    home_GF = row[3]
                                    home_GA = row[4]
                                    home_GD = row[5]
                                    home_games = row[7]
                                    print("home match")
                                elif(team_name.lower() == awayTeam.lower()):
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


                            dataframe = pd.DataFrame([[home_team_number, away_team_number, MFH_result, home_GF, home_GA, home_GD,
                                                       home_points, away_GF, away_GA, away_GD, away_points, home_polarity,
                                                       away_polarity, MFH_home_goals, MFH_away_goals, MFH_home_pos, MFH_away_pos,
                                                       MFH_home_shots, MFH_away_shots, MFH_home_target, MFH_away_target]])
                            # Preprocess data

                            dataframe.columns = ['HomeTeam', 'AwayTeam', 'MFH_result', 'home_GF', 'home_GA', 'home_GD',
                                                 'home_points',
                                                 'away_GF', 'away_GA', 'away_GD', 'away_points', 'MFH_home_sentiment',
                                                 'MFH_away_sentiment',
                                                 'MFH_home_goals', 'MFH_away_goals', 'MFH_home_pos', 'MFH_away_pos',
                                                 'MFH_home_attempts',
                                                 'MFH_away_attempts', 'MFH_home_target', 'MFH_away_target']

                            new_data = preprocess(dataframe, 'MFH')

                            result = model.predict_proba(new_data)
                            away_team_win_prob = result[0][0]
                            draw_prob = result[0][1]
                            home_team_win_prob = result[0][2]

                            cursor.execute(
                                "INSERT INTO " + tableName + " (homeWin, draw, awayWin, time, modelID) VALUES(?,?,?,?,?)",
                                (home_team_win_prob, draw_prob, away_team_win_prob, current_match_time, intelligent_model_id))
                            connection.commit()
                            #id INTEGER PRIMARY KEY, homeWin TEXT, draw TEXT, awayWin TEXT, time TEXT

                            # Predict
                            # Store prediction
                            # continue
                        except Exception as e:
                            print("exception raised while trying to predict for halftime")
                            traceback.print_exc()
                    elif(current_match_time >= 30 and current_match_time < 60):
                        filename = 'H_PredictionModel.sav'
                        model = pickle.load(open(filename, 'rb'))

                        pure_filename = 'H_PureSentiment_PredictionModel.sav'
                        pure_model = pickle.load(open(pure_filename, 'rb'))

                        # Get the stats from table for time period
                        stats_table_name = parseTableName(tempTableName) + "stats"
                        form_table_name = "formTable"

                        # HomeTeam - DONE, Awayteam - DONE, MFH_result - DONE, home_GF, home_GA, home_GD, home_points, away_GF, away_GA, away_GD,
                        # away_points, MFH_home_sentiment, MFH_away_sentiment, MFH_home_goals - DONE, MFH_away_goals - DONE, MFH_home_pos - DONE,
                        # MFH_away_pos - DONE, MFH_home_attempts - DONE, MFH_away_attempts - DONE, MFH_home_target - DONE, MFH_away_target - DONE

                        H_home_pos = 0
                        H_away_pos = 0

                        H_result = 0

                        H_home_shots = 0
                        H_away_shots = 0

                        H_home_target = 0
                        H_away_target = 0

                        H_home_goals = 0
                        H_away_goals = 0

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
                            H_home_goals += row[2]
                            H_away_goals += row[3]

                            H_home_pos += int(row[5][:2])
                            H_away_pos += int(row[6][:2])

                            H_home_shots += int(row[7])
                            H_away_shots += int(row[8])

                            H_home_target += int(row[11])
                            H_away_target += int(row[12])

                            stat_counter += 1.0

                        try:
                            H_home_goals = H_home_goals / stat_counter
                            H_away_goals = H_away_goals / stat_counter

                            H_home_pos = H_home_pos / stat_counter
                            H_away_pos = H_away_pos / stat_counter

                            H_home_shots = H_home_shots / stat_counter
                            H_away_shots = H_away_shots / stat_counter

                            H_home_target = H_home_target / stat_counter
                            H_away_target = H_away_target / stat_counter
                        except:
                            pass

                        if (H_home_goals > H_away_goals):
                            H_result = 0
                        elif (H_home_goals < H_away_goals):
                            H_result = 2
                        else:
                            H_result = 1

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
                        for row in rows:
                            if (row[1].lower() == homeTeam.lower().replace('-', ' ').strip()):
                                home_polarity += row[2]
                                home_tweet_counter += 1
                            elif (row[1].lower() == awayTeam.lower().replace('-', ' ').strip()):
                                away_polarity += row[2]
                                away_tweet_counter += 1

                        try:
                            home_polarity = home_polarity / home_tweet_counter
                        except:
                            home_polarity = 0

                        try:
                            away_polarity = away_polarity / away_tweet_counter
                        except:
                            away_polarity = 0

                        pure_sentiment_df = pd.DataFrame([[home_polarity, away_polarity]])

                        result = pure_model.predict_proba(pure_sentiment_df)
                        away_team_win_prob = result[0][0]
                        draw_prob = result[0][1]
                        home_team_win_prob = result[0][2]

                        cursor.execute(
                            "INSERT INTO " + tableName + " (homeWin, draw, awayWin, time, modelID) VALUES(?,?,?,?,?)",
                            (home_team_win_prob, draw_prob, away_team_win_prob, current_match_time,
                             pure_sentiment_model_id))
                        connection.commit()

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

                        dataframe = pd.DataFrame([[home_team_number, away_team_number, H_result, home_GF, home_GA, home_GD,
                                                   home_points, away_GF, away_GA, away_GD, away_points, home_polarity,
                                                   away_polarity, H_home_goals, H_away_goals, H_home_pos, H_away_pos,
                                                   H_home_shots, H_away_shots, H_home_target, H_away_target]])
                        # Preprocess data

                        dataframe.columns = ['HomeTeam', 'AwayTeam', 'H_result', 'home_GF', 'home_GA', 'home_GD',
                                             'home_points',
                                             'away_GF', 'away_GA', 'away_GD', 'away_points', 'H_home_sentiment',
                                             'H_away_sentiment',
                                             'H_home_goals', 'H_away_goals', 'H_home_pos', 'H_away_pos',
                                             'H_home_attempts',
                                             'H_away_attempts', 'H_home_target', 'H_away_target']

                        new_data = preprocess(dataframe, 'H')

                        result = model.predict_proba(new_data)
                        away_team_win_prob = result[0][0]
                        draw_prob = result[0][1]
                        home_team_win_prob = result[0][2]


                        cursor.execute(
                            "INSERT INTO " + tableName + " (homeWin, draw, awayWin, time, modelID) VALUES(?,?,?,?,?)",
                            (home_team_win_prob, draw_prob, away_team_win_prob, current_match_time, intelligent_model_id))
                        connection.commit()
                        # id INTEGER PRIMARY KEY, homeWin TEXT, draw TEXT, awayWin TEXT, time TEXT
                    else:
                        print("LOADING SECOND HALF MODEL")
                        filename = 'MSH_PredictionModel.sav'
                        model = pickle.load(open(filename, 'rb'))

                        pure_filename = 'MSH_PureSentiment_PredictionModel.sav'
                        pure_model = pickle.load(open(pure_filename, 'rb'))

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

                        try:
                            MSH_home_goals = MSH_home_goals / stat_counter
                            MSH_away_goals = MSH_away_goals / stat_counter

                            MSH_home_pos = MSH_home_pos / stat_counter
                            MSH_away_pos = MSH_away_pos / stat_counter

                            MSH_home_shots = MSH_home_shots / stat_counter
                            MSH_away_shots = MSH_away_shots / stat_counter

                            MSH_home_target = MSH_home_target / stat_counter
                            MSH_away_target = MSH_away_target / stat_counter
                        except:
                            pass

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
                        for row in rows:
                            if (row[1].lower() == homeTeam.lower().replace('-', ' ').strip()):
                                home_polarity += row[2]
                                home_tweet_counter += 1
                            elif (row[1].lower() == awayTeam.lower().replace('-', ' ').strip()):
                                away_polarity += row[2]
                                away_tweet_counter += 1

                        try:
                            home_polarity = home_polarity / home_tweet_counter
                        except:
                            home_polarity = 0

                        try:
                            away_polarity = away_polarity / away_tweet_counter
                        except:
                            away_polarity = 0

                        pure_sentiment_df = pd.DataFrame([[home_polarity, away_polarity]])

                        result = pure_model.predict_proba(pure_sentiment_df)
                        away_team_win_prob = result[0][0]
                        draw_prob = result[0][1]
                        home_team_win_prob = result[0][2]

                        cursor.execute(
                            "INSERT INTO " + tableName + " (homeWin, draw, awayWin, time, modelID) VALUES(?,?,?,?,?)",
                            (home_team_win_prob, draw_prob, away_team_win_prob, current_match_time,
                             pure_sentiment_model_id))
                        connection.commit()

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

                        print("MODEL PREDICTIONS HERE:")
                        print(away_team_win_prob)
                        print(draw_prob)
                        print(home_team_win_prob)
                        away_team_win_prob = result[0][0]
                        draw_prob = result[0][1]
                        home_team_win_prob = result[0][2]

                        cursor.execute(
                            "INSERT INTO " + tableName + " (homeWin, draw, awayWin, time, modelID) VALUES(?,?,?,?,?)",
                            (home_team_win_prob, draw_prob, away_team_win_prob, current_match_time, intelligent_model_id))
                        connection.commit()
                        # id INTEGER PRIMARY KEY, homeWin TEXT, draw TEXT, awayWin TEXT, time TEXT
                except:
                    print("error on conditionals determining which model to use!")
                    print(current_match_time)
                    if(current_match_time == 'finished'):
                        print("LOADING SECOND HALF MODEL")
                        filename = 'MSH_PredictionModel.sav'
                        model = pickle.load(open(filename, 'rb'))

                        pure_filename = 'MSH_PureSentiment_PredictionModel.sav'
                        pure_model = pickle.load(open(pure_filename, 'rb'))

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

                        try:
                            MSH_home_goals = MSH_home_goals / stat_counter
                            MSH_away_goals = MSH_away_goals / stat_counter

                            MSH_home_pos = MSH_home_pos / stat_counter
                            MSH_away_pos = MSH_away_pos / stat_counter

                            MSH_home_shots = MSH_home_shots / stat_counter
                            MSH_away_shots = MSH_away_shots / stat_counter

                            MSH_home_target = MSH_home_target / stat_counter
                            MSH_away_target = MSH_away_target / stat_counter
                        except:
                            pass

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
                        for row in rows:
                            if (row[1].lower() == homeTeam.lower().replace('-', ' ').strip()):
                                home_polarity += row[2]
                                home_tweet_counter += 1
                            elif (row[1].lower() == awayTeam.lower().replace('-', ' ').strip()):
                                away_polarity += row[2]
                                away_tweet_counter += 1

                        try:
                            home_polarity = home_polarity / home_tweet_counter
                        except:
                            home_polarity = 0

                        try:
                            away_polarity = away_polarity / away_tweet_counter
                        except:
                            away_polarity = 0

                        pure_sentiment_df = pd.DataFrame([[home_polarity, away_polarity]])

                        result = pure_model.predict_proba(pure_sentiment_df)
                        away_team_win_prob = result[0][0]
                        draw_prob = result[0][1]
                        home_team_win_prob = result[0][2]

                        cursor.execute(
                            "INSERT INTO " + tableName + " (homeWin, draw, awayWin, time, modelID) VALUES(?,?,?,?,?)",
                            (home_team_win_prob, draw_prob, away_team_win_prob, current_match_time,
                             pure_sentiment_model_id))
                        connection.commit()

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

                        dataframe = pd.DataFrame(
                            [[home_team_number, away_team_number, MSH_result, home_GF, home_GA, home_GD,
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

                        #new_data.to_csv("test.csv", header=True, index=False)

                        result = model.predict_proba(new_data)

                        print("MODEL PREDICTIONS HERE:")
                        away_team_win_prob = result[0][0]
                        draw_prob = result[0][1]
                        home_team_win_prob = result[0][2]
                        print(away_team_win_prob)
                        print(draw_prob)
                        print(home_team_win_prob)

                        cursor.execute(
                            "INSERT INTO " + tableName + " (homeWin, draw, awayWin, time, modelID) VALUES(?,?,?,?,?)",
                            (home_team_win_prob, draw_prob, away_team_win_prob, current_match_time, intelligent_model_id))
                        connection.commit()
                        return
                        # id INTEGER PRIMARY KEY, homeWin TEXT, draw TEXT, awayWin TEXT, time TEXT

                    traceback.print_exc()
                    time.sleep(15)
                print("sleeping...")
                time.sleep(15)
        try:
            machineModelMethod()
        except:
            attempts = 0
            max_attempts = 10
            print("machine learning model exception!")
            traceback.print_exc()
            time.sleep(15)
            while attempts < max_attempts:
                try:
                    machineModelMethod()
                except:
                    attempts += 1
                    time.sleep(15)
        # Load the corresponding model
        # Predict
        # enter prediction into table
        # If updatedTrain is false
            # Then train 3 models on latest training data to form new model
            # save this as latest model, repeat entire thing until match is finished

    return jsonify("Done")

@app.route("/getPredictions", methods=['POST', 'GET'])
def predictions():
    print("Getting predictions")
    try:
        matches_connection = sqlite3.connect("commentary.db")
        matches_cursor = matches_connection.cursor()
    except:
        print("COULD NOT CONNECT TO DATABASE")

    data = request.get_data()
    splitData = data.decode().replace("\"", "").split("__")
    homeTeam = splitData[0]
    awayTeam = splitData[1]
    date_var = splitData[2]
    filename = 'predictionModel.sav'
    model = pickle.load(open(filename, 'rb'))

    tempTableName = homeTeam + awayTeam + splitData[2]
    stats_table_name = parseTableName(tempTableName) + "stats"
    form_table_name = "formTable"

    matches_cursor.execute("select * from " + stats_table_name + " ORDER BY ID DESC")
    rows = matches_cursor.fetchall()

    home_possession = 0
    away_possession = 0

    home_attempts = 0
    away_attempts = 0

    home_attempts_on_target = 0
    away_attempts_on_target = 0

    home_score = 0
    away_score = 0

    HTGF = 0
    ATGF = 0

    HTGA = 0
    ATGA = 0

    HTGD = 0
    ATGD = 0

    home_points = 0
    away_points = 0

    time = 0
    print("UNIQUE IDENTIFIER")
    if(rows):
        for row in rows:
            print(row)
            home_score = row[2]
            away_score = row[3]
            time = row[4]
            home_possession = row[5][:-1]
            away_possession = row[6][:-1]
            home_attempts = row[7]
            away_attempts = row[8]

            home_attempts_on_target = row[11]
            away_attempts_on_target = row[12]
            break
        print(home_possession)
    else:
        print("ROWS ARE EMPTY")

    matches_cursor.execute("select * from " + form_table_name)
    form_rows = matches_cursor.fetchall()
    print(homeTeam)
    for row in form_rows:
        team_name = row[1]
        points = row[2]
        GF = row[3]
        GA = row[4]
        GD = row[5]
        if(team_name.lower() == homeTeam.lower()):
            HTGF = GF
            HTGA = GA
            HTGD = GD
            home_points = points

        elif(team_name.lower() == awayTeam.lower()):
            ATGF = GF
            ATGA = GA
            ATGD = GD
            away_points = points
    home_team_parsed = homeTeam.lower().replace('-', ' ')
    home_team_number = name_to_number[home_team_parsed]

    away_team_parsed = awayTeam.lower().replace('-', ' ')
    away_team_number = name_to_number[away_team_parsed]

    # Paramaters needed to feed into model
    # HomeTeam - number
    # AwayTeam - number
    # HTHG - excluded for now
    # HTAG - excluded for now
    # HTGD - excluded for now
    # HTR - excluded for now
    # HS
    # AS
    # HST
    # AST
    point_dif = home_points - away_points
    GF_dif = HTGF - ATGF
    GA_dif = HTGA - ATGA
    GD_dif = HTGD - ATGD

    try:
        HT_acc = float(home_attempts_on_target) / float(home_attempts)
    except ZeroDivisionError as e:
        print("divide by zero caught")
        HT_acc = 0
    try:
        AT_acc = float(away_attempts_on_target) /float(away_attempts)
    except ZeroDivisionError as e:
        print("divide by zero caught")
        AT_acc = 0

    formatted_data = {
        'home_team': [home_team_number],
        'away_team': [away_team_number],
        'home_attemtps': [home_attempts],
        'away_attempts': [away_attempts],
        'home_attempts_on_target': [home_attempts_on_target],
        'away_attempts_on_target': [away_attempts_on_target],
        'point_dif': [point_dif],
        'GF_dif': [GF_dif],
        'GA_dif': [GA_dif],
        'GD_dif': [GD_dif],
        'home_acc': [HT_acc],
        'away_acc': [AT_acc]
    }

    formatted_data = pd.DataFrame(formatted_data)
    print(formatted_data)
    result = model.predict_proba(formatted_data)
    away_team_win_prob = result[0][0]
    draw_prob = result[0][1]
    home_team_win_prob = result[0][2]

    print(model.classes_)
    return_result = str(home_team_win_prob) + "___" + str(draw_prob) + "___" + str(away_team_win_prob)
    print(return_result)
    return jsonify(return_result)

@app.route("/getMatchesToday", methods=['POST', 'GET'])
def gamesToday():
    print("Called")
    table_name = "MatchesToday"
    try:
        matches_connection = sqlite3.connect("commentary.db")
        matches_cursor = matches_connection.cursor()
    except:
        print("COULD NOT CONNECT TO DATABASE")

    matches_cursor.execute("select distinct time, home_team, away_team, url_id, date from " + table_name)
    rows = matches_cursor.fetchall()
    print("Before")
    result_matrix = []
    count = 0

    for row in rows:
        print(row)
        time_val = row[0]
        home_team = row[1]
        away_team = row[2]
        url_id = row[3]
        date = row[4]
        row_entry = time_val + "___"+home_team+"___"+away_team+"___"+url_id+"___"+date
        result_matrix.append(row_entry)
        count += 1
    return jsonify(result_matrix)

@app.route("/getTeamForm", methods=['POST', 'GET'])
def getFormData():
    try:
        now = datetime.datetime.now()
        month = '%02d' % now.month
        day = '%02d' % now.day
        todaysDate = day + "." + month
        myurl = "https://www.transfermarkt.com/premier-league/formtabelle/wettbewerb/GB1"

        try:
            form_connection = sqlite3.connect("commentary.db")
            form_cursor = form_connection.cursor()
        except:
            print("COULD NOT CONNECT TO DATABASE")

        table_name = 'formTable'

        #form_cursor.execute("DROP TABLE if exists " + table_name)

        create_table_string = "create table if not exists '" + table_name + "' (id INTEGER PRIMARY KEY, name TEXT, points INTEGER, GF INTEGER, GA INTEGER, GD INTEGER, date TEXT, gameCount INTEGER)"
        form_cursor.execute(create_table_string)
        form_connection.commit()

        empty = True

        try:
            form_cursor.execute("SELECT count(*) FROM " + table_name +"")
            result = list(form_cursor)
            empty = False
        except Exception as e:
            print(e)
            print("Table empty!")
            pass

        for entry in result:
            number_of_rows = entry[0]

        form_cursor.execute("select * from " + table_name)
        rows = form_cursor.fetchall()
        dates_match = False

        for row in rows:
            try:
                print(row[6])
                print(todaysDate)
                if (row[6] == todaysDate):
                    print("dates match")
                    dates_match = True
            except Exception as e:
                print(e)
            break
        pageLoad = False
        if (number_of_rows == 0) or (not dates_match):
            print("FORM NEEDS UPDATING")
            form_cursor.execute('DELETE from ' + table_name)
            form_connection.commit()
            browser = webdriver.Chrome()
            browser.get(myurl)
            while pageLoad != True:
                time.sleep(1.5)
                main_table = browser.find_element_by_class_name("responsive-table")
                table_body = main_table.find_elements_by_tag_name('tbody')
                rows = table_body[0].find_elements_by_tag_name('tr')
                for row in rows:
                    entries = row.find_elements_by_tag_name('td')
                    team_name = entries[2].text.lower().strip().replace(' ', '-')
                    if(team_name == 'spurs'):
                        team_name = 'tottenham'
                    GFGA = entries[7].text.lower().strip()
                    GFGA_split = GFGA.split(":")
                    GF = GFGA_split[0].strip()
                    GA = GFGA_split[1].strip()
                    GD = entries[8].text.lower().strip()
                    points = entries[9].text.lower().strip()
                    game_number = entries[10]
                    win_games = game_number.find_elements_by_class_name("form_greenblock")
                    loss_games = game_number.find_elements_by_class_name("form_redblock")
                    draw_games = game_number.find_elements_by_class_name("form_greyblock")
                    game_count = 0
                    for entry in win_games:
                        game_count += 1
                    for entry in loss_games:
                        game_count += 1
                    for entry in draw_games:
                        game_count += 1

                    print(game_count)

                    #print("Team - " + str(team_name) + " -- GFGA - " + str(GFGA) + " -- Points - " + str(points))
                    form_cursor.execute(
                        "INSERT INTO " + table_name + " (name, points, GF, GA, GD, date, gameCount) VALUES(?,?,?,?,?,?,?)",
                        (team_name, points, GF, GA, GD, todaysDate, game_count))
                    form_connection.commit()
                pageLoad = True
        form_cursor.execute("select * from " + table_name)
        rows = form_cursor.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        browser.close()
        print(e)
    return jsonify("test passed")

@app.route("/scrapeMatchesToday", methods=['POST', 'GET'])
def matchesToday():
    try:
        now = datetime.datetime.now()
        month = '%02d' % now.month
        day = '%02d' % now.day
        todaysDate = day + "." + month
        myurl = "https://www.scoreboard.com/uk/football/england/premier-league/"


        pageLoad = False
        scheduled = 0

        rowIDs = []
        times = []
        homeTeams = []
        awayTeams = []
        table_name = "MatchesToday"

        try:
            fixture_connection = sqlite3.connect("commentary.db")
            fixture_cursor = fixture_connection.cursor()
        except:
            print("COULD NOT CONNECT TO DATABASE")

        #fixture_cursor.execute("DROP TABLE " + table_name)
        #fixture_cursor.execute("DROP TABLE if exists " + table_name)

        create_table_string = "create table if not exists '" + table_name + "' (id INTEGER PRIMARY KEY, time TEXT, home_team TEXT, away_team TEXT, url_id TEXT, date TEXT)"
        fixture_cursor.execute(create_table_string)
        fixture_connection.commit()
        result = []
        try:
            fixture_cursor.execute("SELECT count(*) FROM " + table_name +"")
            result = list(fixture_cursor)
            empty = False
        except Exception as e:
            print(e)
            print("Table empty!")
            pass

        for entry in result:
            number_of_rows = entry[0]

        fixture_cursor.execute("select * from " + table_name)
        rows = fixture_cursor.fetchall()
        dates_match = False

        for row in rows:
            try:
                print(row[5])
                print(todaysDate)
                if(row[5] == todaysDate):
                    print("dates match")
                    dates_match = True
            except Exception as e:
                print(e)
            break

        # TO DO - MAKE TABLE EMPTY ITSELF WHEN DATES DONT MATCH, LEFT IN FOR TESTING AT THE MOMENT
        # if(not dates_match):
        #     print("dates fail to match")
        #     # DELETE FROM
        if (number_of_rows == 0) or (not dates_match):
            browser = webdriver.Chrome()
            browser.get(myurl)
            print("NEED TO UPDATE MATCHES")
            while pageLoad != True:
                print("called")
                time.sleep(1.5)
                live = browser.find_elements_by_class_name("stage-live")
                finished = browser.find_elements_by_class_name("stage-finished")
                scheduled = browser.find_elements_by_class_name("stage-scheduled")
                # Possibly problems forseen, as it isn't necessarily true ther must be LIVE results or Scheduled (last week of games has no scheduled) or
                # finished (first week of season), so instead it is just a somewhat logically flawed assumption that there always is a game scheduled, or finished or live
                # Not sure how this would work inbetween seasons...


                for result in live + finished + scheduled:
                    rowID = result.get_attribute("id")[4:]
                    date = result.find_element_by_class_name("time")
                    homeTeam = result.find_element_by_class_name("team-home")
                    awayTeam = result.find_element_by_class_name("team-away")
                    homeTeamText = homeTeam.text
                    awayTeamText = awayTeam.text
                    try:
                        homeTeamText = homeTeam.find_element_by_class_name("padl")
                        homeTeamText = homeTeamText.text[:-1]
                    except:
                        pass

                    try:
                        awayTeamText = awayTeam.find_element_by_class_name("racard")
                        awayTeamText = awayTeam.text[:-1]
                    except:
                        pass
                    if (date.text[:-7] == todaysDate):
                        rowIDs.append(rowID)
                        date_val = date.text[7:]
                        date_val = date_val.strip()
                        home_team_val = homeTeam.text.strip()
                        away_team_val = awayTeam.text.strip()

                        times.append(date_val)
                        homeTeams.append(home_team_val)
                        awayTeams.append(away_team_val)
                        print(home_team_val + " VS " + away_team_val)
                pageLoad = True
            browser.close()

            for time_val, homeTeam, awayTeam, URLID in zip(times, homeTeams, awayTeams, rowIDs):
                fixture_cursor.execute(
                    "INSERT INTO " + table_name + " (time, home_team, away_team, url_id, date) VALUES(?,?,?,?,?)",
                    (time_val, homeTeam, awayTeam, URLID, todaysDate))
                fixture_connection.commit()

            fixture_cursor.execute("select * from " + table_name)
            rows = fixture_cursor.fetchall()
            print("FIXTURE TABLE ENTRIES")
            for row in rows:
                print(row)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return jsonify("CLEAN")

#STOP CALL WHEN MATCH FINISHED
#RETURN SPECIFIC MESSAGE WHEN MATCH NOT STARTED YET
#ONLY ADD NEW COMMENTARY, NEED TO CHECK IF UPDATE IS NEW
@app.route("/teamSelected", methods=['POST', 'GET'])
def new():
    try:
        try:
            connection = sqlite3.connect("commentary.db")
            cursor = connection.cursor()

        except:
            print("COULD NOT CONNECT TO DATABASE")

        def convertToInt(time_input):
            time_input.strip()
            time_input = time_input.replace('\'', '')
            print(time_input)
            if('+' in time_input):
                time_parts = time_input.split("+")
                true_time = int(time_parts[0]) + int(time_parts[1])
                if true_time > 45:
                    half = 1
                if true_time > 90:
                    half = 2
            else:
                true_time = int(time_input)
                half = 0
            return [true_time, half]

        data = request.get_data()
        splitData = data.decode().replace("\"", "").split("__")
        homeTeam = splitData[0]
        awayTeam = splitData[1]
        print("SPLIT DATA" +str(splitData[2]))
        tempTableName = homeTeam + awayTeam + splitData[2]
        tableName = parseTableName(tempTableName)

        #print("Dropping table " + tableName)
        now = datetime.datetime.now()
        year = now.year
        nextYear = year + 1
        URLID = 0


        #cursor.execute("DROP TABLE if exists "+tableName)
        #cursor.execute("DROP TABLE if exists " + tableName+"stats")
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + tableName + "';")
        result = cursor.fetchone()
        number_of_rows = result[0]

        #cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + tableName + "stats';")

        print("RIGHT_HERE " + str(number_of_rows))
        #CHANGE THIS to == 0
        # ONLY EVER != 0 FOR TESTING PURPOSES
        if(number_of_rows == 0):
            #CREATE TABLE
            create_table_string = "create table if not exists '"+ tableName + "' (id INTEGER PRIMARY KEY, commentary TEXT, time TEXT)"
            cursor.execute(create_table_string)

            print("TABLE " + str(tableName) + "stats HAS BEEN CREATED")
            create_table_string = "create table if not exists '" + tableName + "stats' (id INTEGER PRIMARY KEY, matchState TEXT, homeScore INTEGER, awayScore INTEGER, time TEXT, homePossession TEXT, awayPossession TEXT, homeGoalAttempts INTEGER, awayGoalAttempts INTEGER, homePasses INTEGER, awayPasses INTEGER, homeShotsTarget INTEGER, awayShotsTarget INTEGER)"
            cursor.execute(create_table_string)

            def scrapeInfo():
                homeTeamSearch = homeTeam.replace("-", " ")
                awayTeamSearch = awayTeam.replace("-", " ")

                match_table_name = "MatchesToday"
                cursor.execute("select * from " + match_table_name)
                rows = cursor.fetchall()

                for row in rows:
                    print(row)

                print("before start")
                for row in rows:
                    print(row[2] + "__" + homeTeamSearch)
                    print(row[3] + "__" + awayTeamSearch)
                    if (str(row[2]) == homeTeamSearch) & (str(row[3]) == awayTeamSearch):
                        print("MATCH")
                        URLID = str(row[4])
                        break
                print("after")
                print(URLID)

                try:
                    #myurl = "https://www.scoreboard.com/uk/match/levante-alaves-2018-2019/GKbBmhbD/#live-commentary;0"
                    myurl = "https://www.scoreboard.com/uk/match/"+str(homeTeam)+"-"+str(awayTeam)+"-"+str(year)+"-"+str(nextYear)+"/"+str(URLID)+"/#live-commentary;0"
                    browser = webdriver.Chrome()
                    browser.get(myurl)

                    myurl2 = "https://www.scoreboard.com/uk/match/" + str(homeTeam) + "-" + str(awayTeam) + "-" + str(year) + "-" + str(nextYear) + "/" + str(URLID) + "/#match-summary|match-statistics;0|lineups;1"
                    browser2 = webdriver.Chrome()
                    browser2.get(myurl2)

                except:
                    print("Live commentary not available")

                pageLoad = False
                times = 0
                commentary = 0

                times = []
                commentaryUpdates = []
                awayTeams = []

                checkNumber = True

                def parseUpdate(input):
                    check = 0
                    if (input.strip() != ""):
                        input = input.replace("\n", '')
                    return input

                def isNumber(input):
                    parsed = input.strip()[:-1]
                    number = 0
                    try:
                        number = int(parsed)
                        return True
                    except:
                        pass

                    try:
                        if "+" in parsed:
                            splitResult = parsed.split("+")
                            for numResult in splitResult:
                                number += int(numResult)
                        else:
                            return false
                    except:
                        return False
                    return True
                matchAlive = True

                #print("before scrape")

                def scrapeData():
                    print("SCRAPE DATA CALLED")
                    matchState = ""
                    homeScore = ""
                    awayScore = ""
                    matchTimeText = ""
                    homePossessionText = ""
                    awayPossessionText = ""
                    homeGoalAttemptText = ""
                    awayGoalAttemptText = ""
                    homePassText = ""
                    awayPassText = " "

                    pageLoad = False
                    checkNumber = True

                    try:
                        league_table_url = "https://www.premierleague.com/matchweek/3284/table"
                        league_table_page = requests.get(league_table_url)
                        soup = BeautifulSoup(league_table_page.content, 'html.parser')
                        soup.findAll("div", {"class": "standingEntriesContainer"})
                    except:
                        pass

                    print("BEFORE WHILE")
                    while pageLoad != True:
                        print("in while")
                        matchTime = browser2.find_elements_by_class_name("mstat")
                        stats = browser2.find_elements_by_id("tab-statistics-0-statistic")
                        scoreboard = browser2.find_elements_by_class_name("scoreboard")
                        updates = browser.find_elements_by_css_selector(".phrase.fl ")
                        #Start of removal...

                        # End of removal...

                        if len(scoreboard) == 0:
                            print("page not loaded yet!")
                            time.sleep(0.5)
                            continue

                        homeScore = scoreboard[0].text
                        awayScore = scoreboard[1].text
                        matchTimeText = matchTime[0].text

                        # START - Need to remove this if removal placed back
                        match_time_table_name = homeTeam.lower().replace("-", "_") + awayTeam.lower().replace("-", "_") + splitData[2] + "MatchTime"
                        try:
                            create_table_string = "create table if not exists '" + match_time_table_name + "' (id INTEGER PRIMARY KEY, time TEXT)"
                            cursor.execute(create_table_string)
                            connection.commit()
                        except Exception as e:
                            print("table creation exception!")
                            print(e)

                        try:
                            matchTime = browser2.find_element_by_id("atomclock")
                            matchTimeText = matchTime.text.split(":")
                            matchTimeText = matchTimeText[0]
                        except:
                            traceback.print_exc()
                            print("Failure to access atomclock class for time")
                            matchTimeText = matchTime[0].text
                            if (matchTimeText.lower() == 'half time'):
                                print("here")
                                matchTimeText = '45'
                            elif (matchTimeText.lower() == 'finished'):
                                matchTimeText = 'finished'
                                matchState = 1
                            else:
                                matchTimeText = '-1'
                        cursor.execute("DELETE FROM " + match_time_table_name)
                        cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='" + match_time_table_name + "'")
                        cursor.execute("INSERT INTO " + match_time_table_name + " (time) VALUES(?)", (matchTimeText,))
                        connection.commit()
                        print(matchTimeText)

                        # END of removal if removed content reinserted

                        if (homeScore == "-") & (awayScore == "-"):
                            matchState = -1
                            print("MATCH NOT STARTED YET")
                            time.sleep(45)
                            continue
                        else:
                            if len(stats) == 0:
                                print("stats area not loaded yet!")
                                time.sleep(0.5)
                                continue
                            else:
                                matchState = 0
                                if matchTimeText.lower() == "finished":
                                    matchState = 1
                                oddRows = stats[0].find_elements_by_class_name("odd")
                                evenRows = stats[0].find_elements_by_class_name("even")

                                for row in oddRows + evenRows:
                                    if ("ball possession" in row.text.lower()):
                                        homePossessionElement = row.find_element_by_class_name("fl")
                                        awayPossessionElement = row.find_element_by_class_name("fr")
                                        homePossessionText = homePossessionElement.text
                                        awayPossessionText = awayPossessionElement.text
                                    elif ("goal attempts" in row.text.lower()):
                                        homeGoalAttemptElements = row.find_element_by_class_name("fl")
                                        awayGoalAttemptElements = row.find_element_by_class_name("fr")
                                        homeGoalAttemptText = homeGoalAttemptElements.text
                                        awayGoalAttemptText = awayGoalAttemptElements.text
                                    elif ("shots on goal" in row.text.lower()):
                                        homeShotsOnTargetElements = row.find_element_by_class_name("fl")
                                        awayShotsOnTargetElements = row.find_element_by_class_name("fr")
                                        homeShotsOnTargetText = homeShotsOnTargetElements.text
                                        awayShotsOnTargetText = awayShotsOnTargetElements.text
                                    elif ("total passes" in row.text.lower()):
                                        homePassElements = row.find_element_by_class_name("fl")
                                        awayPassElements = row.find_element_by_class_name("fr")
                                        homePassText = homePassElements.text
                                        awayPassText = awayPassElements.text

                        if (len(updates) == 0):
                            #print("page not loaded yet!")
                            time.sleep(0.5)
                            continue

                        for commentaryResult in updates:
                            #print(commentaryResult.text)
                            value = parseUpdate(commentaryResult.text)
                            if ((checkNumber) & (isNumber(value))):
                                times.append(value)
                                checkNumber = False
                            elif not checkNumber:
                                commentaryUpdates.append(value)
                                checkNumber = True
                            else:
                                pass

                        pageLoad = True
                    maxUpdate = 5
                    updateNumber = 0

                    print("inserting to stats table..")
                    #matchState TEXT, homeScore INTEGER, awayScore INTEGER, time TEXT,
                    #homePossession TEXT, awayPossession TEXT, homeGoalAttempts INTEGER, awayGoalAttempts INTEGER, homePasses INTEGER, awayPasses INTEGER)


                    cursor.execute("INSERT INTO " + tableName + "stats (matchState, homeScore, awayScore, time, homePossession, awayPossession, homeGoalAttempts, awayGoalAttempts, homePasses, awayPasses, homeShotsTarget, awayShotsTarget) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (matchState, homeScore, awayScore, matchTimeText, homePossessionText, awayPossessionText, homeGoalAttemptText, awayGoalAttemptText, homePassText, awayPassText, homeShotsOnTargetText, awayShotsOnTargetText))
                    print("I N S E R T E D")
                    #cursor.execute("select * from " + tableName+"stats")
                    #rows = cursor.fetchall()
                    # for row2 in rows:
                       # print(row2)

                    newCommentaryUpdates = []
                    newTimeUpdates = []
                    commentaryUpdatesLength = len(commentaryUpdates) - 1
                    matchNumber = 0
                    break_out = False
                    cursor.execute("select * from " + tableName + " order by id desc limit " + str(maxUpdate))
                    rows = cursor.fetchall()
                    no_match = True
                    try:
                        if (len(rows) == 0):
                            arrayIndex = len(commentaryUpdates) -1
                            while(arrayIndex >= 0):
                                cursor.execute("INSERT INTO " + tableName + "(commentary, time) VALUES(?,?)",(commentaryUpdates[arrayIndex], times[arrayIndex]))
                                arrayIndex -= 1
                        else:
                            for row in rows:
                                if break_out:
                                    break
                                print("looking through row")
                                while no_match:
                                    print(row[1] + "_______" + commentaryUpdates[matchNumber])
                                    print("HERE")
                                    latest_time = row[2]
                                    print("before compare time retrieved")
                                    compare_time = times[matchNumber]
                                    latest_time = convertToInt(latest_time)
                                    compare_time = convertToInt(compare_time)
                                    print("compare time 0")
                                    print(compare_time[0])
                                    print("compare time 1")
                                    print(compare_time[1])
                                    print("latets time 0")
                                    print(latest_time[0])
                                    print("latest time 1")
                                    print(latest_time[1])
                                    #Need to add OR if times[matchNumber] < row[whatever time is]
                                    print("before if statetement")
                                    if commentaryUpdates[matchNumber] == row[1]:
                                        print("breaking out!")
                                        break_out = True
                                        no_match = False
                                        break
                                    elif(compare_time[0] < latest_time[0]) and (compare_time[1] == latest_time[1]):
                                        print("breaking out!")
                                        break_out = True
                                        no_match = False
                                        break
                                    else:
                                        print("in else statement")
                                        newCommentaryUpdates = [commentaryUpdates[matchNumber]] + newCommentaryUpdates
                                        print("commentary updates assigned")
                                        newTimeUpdates = [times[matchNumber]] + newTimeUpdates
                                        print("time updates assigned")
                                        matchNumber += 1
                                        print(newCommentaryUpdates)
                                        print(newTimeUpdates)
                                print("breaking out of rows")
                                break
                            print("new commentary updates")
                            print(newCommentaryUpdates)
                            print(newTimeUpdates)

                            insert_index = 0
                            max_insert_length = len(newCommentaryUpdates)

                            while insert_index < max_insert_length:
                                cursor.execute("INSERT INTO " + tableName + "(commentary, time) VALUES(?,?)", (newCommentaryUpdates[insert_index], newTimeUpdates[insert_index]))
                                insert_index += 1

                        with open("static/csv/lastUpdate.csv", mode="w+") as file:
                            fileWriter = csv.writer(file)
                            fileWriter.writerow([times[0], commentaryUpdates[0]])
                        file.close()

                        commentaryUpdates.clear()
                        times.clear()
                        connection.commit()
                    except Exception as e:
                        print("Error inserting new commentary updates!")
                        traceback.print_exc()
                        print(e)

                    if(matchState == 1):
                        streamTweets.current_match_time = -1
                        browser.close()
                        browser2.close()
                        print("Match finished so terminating script")
                        return


                    time.sleep(10)
                    scrapeData()
                try:
                    print("now calling to scrape page")
                    scrapeData()
                except Exception as e:
                    attempts = 0
                    max_attempts = 10
                    print("Exception raised while scraping")

                    print(e)
                    time.sleep(15)
                    print("calling scrape data again!")
                    while attempts < max_attempts:
                        try:
                            scrapeData()
                        except:
                            attempts += 1
                            time.sleep(15)
            try:
                print("calling scraping..")
                twitter_thread = threading.Thread(target=streamTweets.main, args=(homeTeam, awayTeam, tableName, splitData[2]))
                twitter_thread.start()
                print("twitter called")
                scrapeInfo()
            except Exception as e:
                print("error opening page - " + e)
                time.sleep(15)
                twitter_thread = threading.Thread(target=streamTweets.main, args=(homeTeam, awayTeam, tableName, splitData[2]))
                twitter_thread.start()
                traceback.print_exc()
                attempts = 0
                max_attempts = 10
                time.sleep(1)
                while attempts < max_attempts:
                    try:
                        print("TRYING TO HANDLE EXCEPTION SCRAPEINFO")
                        scrapeInfo()
                    except:
                        traceback.print_exc()
                        attempts += 1
                        time.sleep(1)

    except Exception as e:
        print(e)
        return jsonify("ERROR")

    return jsonify("CLEAN")

                #check if match finished
                #scrape
            #CREATE FUNCTION
                #scrape data
                #check if match finished
                    #if finished - terminate
                    #else continue
                #update table with updates

@app.route("/requestStats", methods=['POST', 'GET'])
def getUpdate():
    print("GET UPDATE CALLED")
    data = request.get_data()
    splitData = data.decode().replace("\"", "").split("__")
    homeTeam = splitData[0]
    awayTeam = splitData[1]
    tempTableName = homeTeam + awayTeam + splitData[2]+"Tweets"
    tweetTableName = parseTableName(tempTableName)

    Team_abbreviations = {
        homeTeam: [],
        awayTeam: []
    }

    try:
        connection = sqlite3.connect("commentary.db")
        cursor = connection.cursor()

    except:
        print("COULD NOT CONNECT TO DATABASE")

    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + tweetTableName + "';")
    result = cursor.fetchone()
    number_of_rows = result[0]
    if (number_of_rows == 0):
        return jsonify("ERROR")
    else:
        cursor.execute("select * from " + tweetTableName + " order by id desc")
        rows = cursor.fetchall()
        subject = 0
        home_polarity = 0
        away_polarity = 0
        home_counter = 0
        away_counter = 0
        home_avg = 0
        away_avg = 0
        home_positive = 0
        home_negative = 0
        home_neutral = 0
        away_positive = 0
        away_negative = 0
        away_neutral = 0
        time = 0
        print("IN ELSE STATEMENT")
        homeTeam = homeTeam.lower().replace("-", " ")
        awayTeam = awayTeam.lower().replace("-", " ")
        for row in rows:
            subject = row[1]
            print(str(subject) + "-" + str(homeTeam) + "-" + str(awayTeam))
            if subject == homeTeam:
                print("HOME POLARITY " + str(home_polarity))
                time = row[4]
                print(row[3])
                home_polarity += row[2]
                home_counter += 1
                if row[2] > 0:
                    home_positive += 1
                elif row[2] < 0:
                    home_negative += 1
                else:
                    home_neutral += 1
            elif subject == awayTeam:
                away_polarity += row[2]
                away_counter += 1
                if row[2] > 0:
                    away_positive += 1
                elif row[2] < 0:
                    away_negative += 1
                else:
                    away_neutral += 1
        try:
            home_avg = float(float(home_polarity) / float(home_counter))
        except:
            home_avg = 0
        try:
            away_avg = float(float(away_polarity) / float(away_counter))
        except:
            away_avg = 0
        home_array = [home_avg, home_positive, home_negative]
        away_array = [away_avg, away_positive, away_negative]
        return jsonify(str(time) + "___" + str(home_avg) + "___" + str(home_positive) + "___" +str(home_negative) + "___" + str(home_neutral) + "___" + str(away_avg) + "___" + str(away_positive) + "___" + str(away_negative) + "___" + str(away_neutral))


@app.route("/requestCommentary", methods=['POST', 'GET'])
def getCommentary():
    try:
        try:
            connection = sqlite3.connect("commentary.db")
            cursor = connection.cursor()

        except:
            print("COULD NOT CONNECT TO DATABASE")

        data = request.get_data()
        splitData = data.decode().replace("\"", "").split("__")
        homeTeam = splitData[0]
        awayTeam = splitData[1]
        tempTableName = homeTeam + awayTeam + splitData[2]
        tableName = parseTableName(tempTableName)
        maxUpdate = 5

        cursor.execute("select * from " + tableName + " order by id desc limit " + str(maxUpdate))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            commentaryUpdate = row[1]
            timeUpdate = row[2]
            result.append(timeUpdate + "___" + commentaryUpdate)
        return jsonify(result)

    except Exception as e:
        print(e)
        return jsonify("ERROR")


@app.route("/quickStats", methods=['POST', 'GET'])
def stats():
    print("Now in the stats section")
    try:
        try:
            connection = sqlite3.connect("commentary.db")
            cursor = connection.cursor()

        except:
            print("COULD NOT CONNECT TO DATABASE")


        data = request.get_data()
        splitData = data.decode().replace("\"", "").split("__")
        homeTeam = splitData[0]
        awayTeam = splitData[1]

        tempTableName = homeTeam + awayTeam + splitData[2] +"stats"
        tableName = parseTableName(tempTableName)

        print("HERE RETRIEVEING STATS")
        cursor.execute("SELECT * FROM " + tableName)
        rows = cursor.fetchall()
        print(tableName)
        for row in rows:
           print(row)

        cursor.execute("SELECT * FROM " + tableName + " ORDER BY id DESC LIMIT 1")
        rows = cursor.fetchall()
        result = []


        for row in rows:
            matchState = row[1]
            homeScore = row[2]
            awayScore = row[3]
            matchTimeText = row[4]
            homePossessionText = row[5]
            awayPossessionText = row[6]
            homeGoalAttemptText = row[7]
            awayGoalAttemptText = row[8]
            homePassText = row[9]
            awayPassText = row[10]

            result = {"matchState": matchState, "homeScore": homeScore, "awayScore": awayScore, "time": matchTimeText,
                    "homePossession": homePossessionText, "awayPossession": awayPossessionText,
                    "homeGoalAttempts": homeGoalAttemptText, "awayGoalAttempts": awayGoalAttemptText,
                    "homePasses": homePassText, "awayPasses": awayPassText}
        return jsonify(result)

    except Exception as e:
        print(e)
        print("H E R R O R")
        return jsonify("ERROR")

@app.route("/tinyDelayRequest", methods=['POST', 'GET'])
def tinyDelay():
    print("T I N Y  D E L A Y ")
    time.sleep(1)
    return jsonify("done")

@app.route("/delayRequest", methods=['POST', 'GET'])
def delay():
    time.sleep(10)
    return jsonify("done")

@app.route("/largeDelayRequest", methods=['POST', 'GET'])
def largeDelay():
    time.sleep(25)
    return jsonify("done")


if __name__ == "__main__":
    app.run(debug=True)

