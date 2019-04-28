from bs4 import BeautifulSoup
import requests

def main():
    url = 'http://www.footballsquads.co.uk/eng/2018-2019/engprem.htm'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    main = soup.find(id="main")
    team_entries = main.find_all('h5')
    url = url[:-4]

    exclude_values = ['Name','name', '']

    for entry in team_entries:
        team_name = entry.text
        link = entry.find('a', href=True)
        link_text = link['href'][7:]
        team_url = url + link_text

        team_page = requests.get(team_url).content
        page_soup = BeautifulSoup(team_page, 'html.parser')
        main = page_soup.find(id='main')
        table_rows = main.find_all('tr')
        name_array = []
        for row in table_rows:
            row_entries = row.find_all('td')
            try:
                name = row_entries[1].text
                name = name.replace(u'\xa0', u' ')
                if name in exclude_values:
                    continue
                split_name = name.split(" ")
                name_array.append(name)
                try:
                    name_array.append(split_name[1])
                except:
                    continue
            except Exception as e:
                print(e)
                break
        print(name_array)
        #for name in name_array:
            #print(name)
main()
