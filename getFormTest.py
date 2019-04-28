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

    create_table_string = "create table if not exists '" + table_name + "' (id INTEGER PRIMARY KEY, name TEXT, points INTEGER, GF INTEGER, GA INTEGER, GD INTEGER, date TEXT)"
    form_cursor.execute(create_table_string)
    form_connection.commit()

    empty = True

    try:
        form_cursor.execute("SELECT count(*) FROM " + table_name + "")
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

    print("FORM NEEDS UPDATING")
    form_cursor.execute('DELETE from ' + table_name)
    form_connection.commit()
    browser = webdriver.Chrome()
    browser.get(myurl)
    pageLoad = False
    while pageLoad != True:
        time.sleep(1.5)
        main_table = browser.find_element_by_class_name("responsive-table")
        table_body = main_table.find_elements_by_tag_name('tbody')
        rows = table_body[0].find_elements_by_tag_name('tr')
        for row in rows:
            entries = row.find_elements_by_tag_name('td')
            team_name = entries[2].text.lower().strip().replace(' ', '-')
            if (team_name == 'spurs'):
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

            # print("Team - " + str(team_name) + " -- GFGA - " + str(GFGA) + " -- Points - " + str(points))
        pageLoad = True
    form_cursor.execute("select * from " + table_name)
    rows = form_cursor.fetchall()
    for row in rows:
        print(row)
except Exception as e:
    print(e)

form_cursor.execute("drop table formTable")

form_cursor.execute("select * from " + table_name)
    rows = form_cursor.fetchall()
    for row in rows:
        print(row)