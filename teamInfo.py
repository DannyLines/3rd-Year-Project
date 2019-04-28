import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import csv

#Define filename
filename = "teamInfo.csv"

#Defining webpage
myurl = "https://www.premierleague.com/clubs"

#Downloading webpage content
uClient = uReq(myurl)

page_content = uClient.read()

uClient.close()

page_soup = soup(page_content, "html.parser")

containers = page_soup.findAll("a", {"class":"indexItem"})

with open(filename, mode="w+") as f:
    fileWriter = csv.writer(f)
    fileWriter.writerow(['TeamName', 'StadiumName'])
    for container in containers:
        clubName = container.find("h4", {"class":"clubName"}).text
        stadiumName = container.find("div", {"class":"stadiumName"}).text
        print(clubName)
        print(stadiumName)
        fileWriter.writerow([clubName, stadiumName])

f.close()