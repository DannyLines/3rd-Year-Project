import csv
import datetime
import json
import requests
import time

from selenium import webdriver
from bs4 import BeautifulSoup as soup

myurl = "https://www.scoreboard.com/uk/match/manchester-utd-wolves-2018-2019/tnt4xEeo/#match-summary|match-statistics;0|lineups;1"
headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
browser = webdriver.Chrome()
browser.get(myurl)

pageLoad = False

matchState = 0; #   -1 = not started   ---   0 = live   ---   1 = finished
scoreboard = []
matchTime = []
stats = []

homeScore = ""
awayScore = ""
matchTimeText = ""

homePossessionText = ""
awayPossessionText = ""
while pageLoad != True:
    matchTime = browser.find_elements_by_class_name("mstat")
    stats = browser.find_elements_by_id("tab-statistics-0-statistic")
    scoreboard = browser.find_elements_by_class_name("scoreboard")

    if len(scoreboard) == 0:
        print("page not loaded yet!")
        time.sleep(0.5)
        continue

    homeScore = scoreboard[0].text
    awayScore = scoreboard[1].text
    matchTimeText = matchTime[0].text

    if (homeScore == "-") & (awayScore == "-"):
        matchState = -1
        data = {"matchState": matchState}
    else:
        if len(stats) == 0:
            print("stats area not loaded yet!")
            time.sleep(0.5)
            continue
        else:
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
                elif ("total passes" in row.text.lower()):
                    homePassElements = row.find_element_by_class_name("fl")
                    awayPassElements = row.find_element_by_class_name("fr")
                    homePassText = homePassElements.text
                    awayPassText = awayPassElements.text

    print(homePossessionText)
    print(awayPossessionText)
    print(homeGoalAttemptText)
    print(awayGoalAttemptText)
    print(homePassText)
    print(awayPassText)

    data = {"matchState": matchState, "homeScore": homeScore, "awayScore": awayScore, "time":matchTimeText, "homePossession": homePossessionText, "awayPossession": awayPossessionText, "homeGoalAttempts": homeGoalAttemptText, "awayGoalAttempts": awayGoalAttemptText, "homePasses": homePassText, "awayPasses": awayPassText}
    pageLoad = True
browser.close()
