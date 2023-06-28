from ics import Calendar, Event
import requests
import arrow
from bs4 import BeautifulSoup

## Web Scraping
url = "https://atcoder.jp/home"
html = requests.get(url)
soup = BeautifulSoup(html.content, "html.parser")
upcoming = soup.find(id='contest-table-upcoming')
contests = []
dict = {}
hit_count = 0
for element in upcoming.find_all("a"):    # すべてのliタグを検索して表示
    if hit_count % 2 == 0:
        begin = arrow.get(element.text)
        end = begin.shift(minutes=+100)
        dict["begin"] = begin
        dict["end"] = end
    elif hit_count % 2 == 1:
        dict["name"] = element.text
        dict["url"] = "https://atcoder.jp" + element.get('href')
        contests.append(dict)
        dict = {}
    hit_count = hit_count + 1

# カレンダーの生成
cal = Calendar()
cal.creator = 'Kaz' # 作成者

# イベントの生成
for contest in contests:
    event = Event()
    event.name = contest["name"]
    event.begin = contest["begin"]
    event.end = contest["end"]
    event.url = contest["url"]
    cal.events.add(event)

with open('my.ics', 'w', encoding='utf-8') as f:
    f.write(str(cal))