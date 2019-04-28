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

myurl2 = "https://www.scoreboard.com/uk/match/shanghai-sipg-kawasaki-2019/jNKNL1U5/#match-summary|match-statistics;0|lineups;1"
browser2 = webdriver.Chrome()
browser2.get(myurl2)
matchTime = browser2.find_elements_by_class_name("mstat")

try:
    connection = sqlite3.connect("commentary.db")
    cursor = connection.cursor()

except:
    print("COULD NOT CONNECT TO DATABASE")
match_time_table_name = "test_test"

create_table_string = "create table if not exists '" + match_time_table_name + "' (id INTEGER PRIMARY KEY, time TEXT)"
cursor.execute(create_table_string)
connection.commit()

while(True):
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



    connection.commit()
    time.sleep(5)
browser2.close()