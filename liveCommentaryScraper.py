import csv
import time
import datetime
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.by import By


now = datetime.datetime.now()
month = '%02d' % now.month
todaysDate = str(now.day) + "." + month
todaysDate = "15.09"
myurl = "https://www.scoreboard.com/uk/match/aek-larnaca-zurich-2018-2019/4UKlWzAF/#live-commentary;0"
try:
    browser = webdriver.Chrome()
    browser.get(myurl)
    page = browser.page_source
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
    if(input.strip() != ""):
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


while pageLoad != True:
    #timeUpdates = browser.find_elements_by_css_selector(".time-box.time-box-sec")
    updates = browser.find_elements_by_css_selector(".phrase.fl ")

    if (len(updates) == 0):
        print("page not loaded yet!")
        time.sleep(0.5)
        continue

    for commentaryResult in updates:
        value = parseUpdate(commentaryResult.text)
        if ((checkNumber) & (isNumber(value))):
            times.append(value)
            checkNumber = False
        elif not checkNumber:
            commentaryUpdates.append(value)
            checkNumber = True

    pageLoad = True
browser.close()
maxUpdate = 5
updateNumber = 0

with open("lastUpdate.csv", mode="r") as readFile:
    csv_reader = csv.reader(readFile, delimiter=",")
    firstRow = next(csv_reader)
    try:
        if(firstRow[0] == times[0]) & (firstRow[1] == commentaryUpdates[0]):
            print("nothing to change")
    except:
        with open("gameUpdates.csv", mode="w+") as file:
            fileWriter = csv.writer(file)
            fileWriter.writerow(['Time', 'Comment'])
            while updateNumber < maxUpdate:
                fileWriter.writerow([times[updateNumber], commentaryUpdates[updateNumber]])
                updateNumber += 1
        file.close()

        with open("lastUpdate.csv", mode="w+") as file:
            fileWriter = csv.writer(file)
            fileWriter.writerow([times[0], commentaryUpdates[0]])
        file.close()