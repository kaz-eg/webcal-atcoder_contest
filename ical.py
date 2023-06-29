from icalendar import Calendar, Event, Timezone, TimezoneStandard
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
with open('atcoder_contest.ics', 'wb') as f:
    f.write(cal.to_ical())