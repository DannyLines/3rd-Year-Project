import csv
import time
import datetime
from selenium import webdriver


now = datetime.datetime.now()
month = '%02d' % now.month
todaysDate = str(now.day) + "." + month
#todaysDate = "15.09"
myurl = "https://www.scoreboard.com/uk/football/england/premier-league/"
browser = webdriver.Chrome()
browser.get(myurl)
page = browser.page_source

pageLoad = False
scheduled = 0

rowIDs = []
times = []
homeTeams = []
awayTeams = []

while pageLoad != True:
    print("called")
    live = browser.find_elements_by_class_name("stage-live")
    finished = browser.find_elements_by_class_name("stage-finished")
    scheduled = browser.find_elements_by_class_name("stage-scheduled")
    #Possibly problems forseen, as it isn't necessarily true ther must be LIVE results or Scheduled (last week of games has no scheduled) or
    #finished (first week of season), so instead it is just a somewhat logically flawed assumption that there always is a game scheduled, or finished or live
    #Not sure how this would work inbetween seasons...
    if (len(live) == 0) & (len(scheduled) == 0) & (len(finished)==0):
        print("page not loaded yet!")
        time.sleep(0.5)
        continue

    for result in live+finished+scheduled:
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

        if(date.text[:-7] == todaysDate):
            rowIDs.append(rowID)
            times.append(date.text[7:])
            homeTeams.append(homeTeam.text)
            awayTeams.append(awayTeam.text)
            print(homeTeam.text + " VS " + awayTeam.text)
    pageLoad = True
browser.close()

with open("static/csv/gamesToday.csv", mode="w+") as file:
    fileWriter = csv.writer(file)
    fileWriter.writerow(['Time', 'HomeTeam', 'AwayTeam', 'URLID'])
    for time, homeTeam, awayTeam, URLID in zip(times, homeTeams, awayTeams, rowIDs):
        fileWriter.writerow([time, homeTeam, awayTeam, URLID])
file.close()