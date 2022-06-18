#!/usr/bin/python3

from datetime import date, datetime, time, timedelta
from functools import reduce
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
from itertools import groupby
from operator import itemgetter
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', default='kapow.xml', help='File to process')
parser.add_argument('-p', '--project', help='Which project to use')
parser.add_argument('-m', '--month',  help='Month to create report for (yyyy-mm)')
args = parser.parse_args()
print(args)
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
            "note": y.get("note")
        })

#print(data)

def round_day(day):
    rounded_day = day.copy()
    day_sum = reduce(lambda acc, curr: acc + (curr["stop"] - curr["start"]).total_seconds() / 60, rounded_day, 0)
    mdl = day_sum % 15
    if mdl is not 0:
        rounded_day[-1]["stop"] = rounded_day[-1]["stop"] + timedelta(minutes=15 - mdl)
        print(f'{15 - mdl} added')
        day_sum += 15 - mdl
    
    for session in rounded_day:
        print(f"{datetime.strftime(session['start'], '%H:%M')} - {datetime.strftime(session['stop'], '%H:%M')}: {session['note']}")
    day_sum_date = datetime.fromtimestamp(0).replace(second=0, minute=0, hour=0) + timedelta(minutes = day_sum)
    print(day_sum, f"{day_sum_date.hour}:{day_sum_date.minute}", rounded_day)

# def sum_daily_hours(rounded_day):
#     pass

round_day(data["kvbw"][list(data["kvbw"].keys())[0]])

