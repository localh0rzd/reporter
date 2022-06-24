#!/usr/bin/python3

from datetime import date, datetime, time, timedelta
from functools import reduce
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
from itertools import groupby
from operator import itemgetter
from functools import reduce
import requests
import argparse
import os
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', default='kapow.xml', help='File to process')
parser.add_argument('--project', help='Which project to use')
parser.add_argument('-u', '--username',  help='Timicx username', default=os.environ.get("TIMICX_USERNAME"))
parser.add_argument('--password',  help='Timicx password', default=os.environ.get("TIMICX_PASSWORD"))
parser.add_argument('-m', '--month',  help='Month to create report for (yyyy-mm)')
parser.add_argument('-l', '--list-projects',  help='List available project with their respective ids',  action='store_true')
args = parser.parse_args()

def parse_xml():
    et = ET.parse("kapow.xml")
    data = {}
    for x in et.findall("project"):
        project = x.get('name')
        if args.project and args.project not in project:
            break
        data[project] = {}
        for y in x.findall('session'):
            session_date = y.get('date')
            if args.month and args.month not in session_date:
                break
            if session_date not in data[project]:
                data[project][session_date] = []
            data[project][session_date].append({
                "start": datetime.strptime(y.get("start"), "%H:%M:%S").replace(second=0),
                "stop": datetime.strptime(y.get("stop"), "%H:%M:%S").replace(second=0),
                "note": y.get("note"),
                "date": session_date
            })

#print(data)
# for date in data["kvbw"]:
#     print(round_day(data["kvbw"][date]))

def get_projects():
    request = requests.get('https://fruuts.timicx.net/ws/2.0/projects.json')

def round_day(day):
    rounded_day = day.copy()
    day_sum = reduce(lambda acc, curr: acc + (curr["stop"] - curr["start"]).total_seconds() / 60, rounded_day, 0)
    mdl = int(day_sum % 15)
    sessions = []
    if mdl is not 0:
        print(mdl)
        rounded_day[-1]["stop"] = rounded_day[-1]["stop"] + timedelta(minutes=15 - mdl)
        print(f'{15 - mdl} added')
        day_sum += 15 - mdl
    
    for session in rounded_day:
        print(f"{datetime.strftime(session['start'], '%H:%M')} - {datetime.strftime(session['stop'], '%H:%M')}: {session['note']} ({session['stop'] - session['start']})")
    day_sum_date = datetime.fromtimestamp(0).replace(second=0, minute=0, hour=0) + timedelta(minutes = day_sum)
    print(day_sum, f"{day_sum_date.hour}:{day_sum_date.minute}")
    print(rounded_day)
    result = {
        "day_sum": f"{day_sum_date.hour:02d}:{day_sum_date.minute:02d}",
        "day_begin": rounded_day[0]["start"],
        "day_end": rounded_day[-1]["stop"],
        "day_summary": ", ".join(reduce(lambda r, x: r + [x] if x not in r else r, list(map(lambda y: y["note"], rounded_day)), [])),
        "sessions": list(map(lambda x: {"start": datetime.strftime(x['start'], '%H:%M'), "stop": datetime.strftime(x['stop'], '%H:%M'), "note": x["note"]}, rounded_day))
    }
    return result

if __name__ == "__main__":
    print(args)
    if args.list_projects:
        if not args.username or not args.password:
            print("Username or password missing")
            exit(1)
        get_projects()
    