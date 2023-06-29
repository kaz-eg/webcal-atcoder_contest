from icalendar import Calendar, Event
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
        dict["dtstart"] = begin
        dict["dtend"] = end
    elif hit_count % 2 == 1:
        dict["summary"] = element.text
        dict["url"] = "https://atcoder.jp" + element.get('href')
        contests.append(dict)
        dict = {}
    hit_count = hit_count + 1

# カレンダーの生成
cal = Calendar()
cal['prodid'] = 'Kaz - AtCoder Contest Calendar'
cal['version'] = '2.0'
cal['method'] = 'PUBLISH'
cal['calscale'] = 'GREGORIAN'
cal['x-wr-calname'] = 'AtCoder Contest Calendar'
cal['x-wr-caldesc'] = 'Kazが自動配信するAtCoder Contest Calendar'
cal['x-wr-timezone'] = 'Asia/Tokyo'

# イベントの生成
for contest in contests:
    event = Event()
    event['summary'] = contest["summary"]
    event['dtstart'] = contest["dtstart"]
    event['dtend'] = contest["dtend"]
    event['url'] = contest["url"]
    cal.add_component(event)

with open('atcoder_contest_schedule.ics', 'wb') as f:
    f.write(cal.to_ical())