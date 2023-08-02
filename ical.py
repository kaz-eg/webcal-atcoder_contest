from icalendar import Calendar, Event, Timezone, TimezoneStandard
import requests
import arrow
from bs4 import BeautifulSoup

def scraping(url, classOrId="class", className="", idName="", contests=[]):

    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    table = None
    if classOrId == "class":
        table = soup.find(class_=className)
    elif classOrId == "id":
        table = soup.find(id=idName)
    else:
        return
    dict = {}
    hit_count = 0

    contestsLength = len(contests)

    for element in table.find_all("a"):    # すべてのaタグを検索
        if hit_count % 2 == 0:
            begin = arrow.get(element.text)
            dict["dtstart"] = begin
        elif hit_count % 2 == 1:
            dict["summary"] = element.text
            dict["url"] = "https://atcoder.jp" + element.get('href')
            contests.append(dict)
            dict = {}
        hit_count = hit_count + 1

    hit_count = 0

    for element in table.find_all("td"):    # すべてのtdタグを検索
        if hit_count % 4 == 2:
            time = element.text.split(':')
            dict = contests[(int)(hit_count/4) + (contestsLength)]
            contests[(int)(hit_count/4) + (contestsLength)]["dtend"] = dict["dtstart"].shift(hours=+int(time[0]), minutes=+int(time[1]))

        if hit_count % 4 == 3:
            contests[(int)(hit_count/4) + (contestsLength)]["description"] = "Rated対象 : " + element.text

        hit_count = hit_count + 1


## Web Scraping
base_url = "https://atcoder.jp"
contests = []

### Scheduled Contest
scraping(url=base_url + "/contests/?lang=ja", classOrId="id", idName="contest-table-upcoming", contests=contests)

### Archived Contest
html = requests.get(base_url + "/contests/archive?lang=ja")
soup = BeautifulSoup(html.content, "html.parser")
ul = soup.find(class_="pagination-sm")
maxPage = 1
for element in ul.find_all("li"):
    maxPage = int(element.text)

for page in range(1, (maxPage + 1), 1):
    scraping(url=base_url + "/contests/archive?lang=ja&page=" + str(page), classOrId="class", className="table-responsive", contests=contests)

## generate calendar
cal = Calendar()
cal['prodid'] = 'Kaz - AtCoder Contest Calendar'
cal['version'] = '2.0'
cal['method'] = 'PUBLISH'
cal['calscale'] = 'GREGORIAN'
cal['x-wr-calname'] = 'AtCoder Contest'
cal['x-wr-caldesc'] = 'Kazが自動配信するAtCoder Contest Calendar'
cal['x-wr-timezone'] = 'Asia/Tokyo'

## generate events
for contest in contests:
    event = Event()
    event['uid'] = "kaz-atcodercontestschedule-" + contest["dtstart"].format('YYYYMMDD')
    event['summary'] = contest["summary"]
    event['dtstart'] = contest["dtstart"].to('UTC').format('YYYYMMDDTHHmmss') + 'Z'
    event['dtend'] = contest["dtend"].to('UTC').format('YYYYMMDDTHHmmss') + 'Z'
    event['description'] = contest["description"]
    event['url'] = contest["url"]
    cal.add_component(event)

## set timezone
tzs = TimezoneStandard()
tzs['dtstart'] = '19700101T000000'
tzs['tzoffsetto'] = '+0900'
tzs['tzoffsetfrom'] = '+0900'
tz = Timezone()
tz['TZID'] = 'Asia/Tokyo'
tz.add_component(tzs)
cal.add_component(tz)

## write on file.
with open('/tmp/atcoder_contest.ics', 'wb') as f:
    f.write(cal.to_ical())