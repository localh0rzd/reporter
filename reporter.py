#!/usr/bin/python3

from datetime import date, datetime, time, timedelta, timezone
from functools import reduce
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
from itertools import groupby
from operator import itemgetter
from functools import reduce
import requests
import argparse
import os
import json
import logging
import re

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', default='kapow.xml', help='File to process')
parser.add_argument('--project', help='Which project to use')
parser.add_argument('-u', '--username',  help='Timicx username', default=os.environ.get("TIMICX_USERNAME"))
parser.add_argument('--password',  help='Timicx password', default=os.environ.get("TIMICX_PASSWORD"))
parser.add_argument('-m', '--month',  help='Month to create report for (yyyy-mm)')
parser.add_argument('-l', '--list-projects',  help='List available project with their respective ids',  action='store_true')
parser.add_argument('-t', '--list-sessions',  help='List unbilled sessions for project', action='store_true')
parser.add_argument('-a', '--add-sessions',  help='Add unbilled sessions for project', action='store_true')
parser.add_argument('-w', '--write-report',  help='Write CSV report for set month', action='store_true')
args = parser.parse_args()

def parse_xml(file):
    et = ET.parse(file)
    data = {}
    for x in et.findall("project"):
        project = x.get('name')
        # if args.project and args.project not in project:
        #     break
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
                "date": session_date,
                "billed": True if y.get('billed') is '1' else False
            })
    return data

def get_projects():
    request = requests.get('https://fruuts.timicx.net/ws/2.0/projects.json', auth=(args.username, args.password))
    body = request.json()
    #body = json.loads('[{"id":1,"name":"alle Projekte","billable":true,"description":"","active":true,"parent":null,"position":0,"children":[7,14,12,13,181,15,27,49,52,73,80,74,56,144,149,152,160,170,174,175,184,189,199,200,190,202,203,204,205,206,207,208,209,191,192,193,194,197,185,186,176,60,64,65,57,66,110,113,121],"estimatedTime":null,"estimatedCompletionDate":null},{"id":12,"name":"fruuts","billable":false,"description":"<br>","active":true,"parent":1,"position":2,"children":[16,17,18,19,21,22,122,132],"estimatedTime":null,"estimatedCompletionDate":"2015-12-31"},{"id":16,"name":"Urlaub","billable":false,"description":"<br>","active":true,"parent":12,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":17,"name":"Krankheit","billable":false,"description":"<br>","active":true,"parent":12,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":18,"name":"Einarbeitung","billable":false,"description":"<br>","active":true,"parent":12,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":19,"name":"Presales","billable":false,"description":"<br>","active":true,"parent":12,"position":3,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":21,"name":"Weiterbildung","billable":false,"description":"<br>","active":true,"parent":12,"position":4,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":22,"name":"Intern","billable":false,"description":"<br>","active":true,"parent":12,"position":5,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":23,"name":"VMS-KVWL","billable":true,"description":"<br>","active":false,"parent":49,"position":2,"children":[24,25,67,68],"estimatedTime":null,"estimatedCompletionDate":null},{"id":24,"name":"Entwicklung","billable":true,"description":"<br>","active":false,"parent":23,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":25,"name":"Wartung\/Betrieb","billable":true,"description":"<br>","active":true,"parent":23,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":27,"name":"IPS Projects GmbH","billable":true,"description":"<br>","active":true,"parent":1,"position":6,"children":[31,28],"estimatedTime":null,"estimatedCompletionDate":null},{"id":28,"name":"frips","billable":true,"description":"<br>","active":true,"parent":27,"position":1,"children":[29,30,119,124],"estimatedTime":null,"estimatedCompletionDate":null},{"id":29,"name":"Entwicklung","billable":true,"description":"<br>","active":true,"parent":28,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":30,"name":"Wartung\/Betrieb\/Support","billable":true,"description":"<br>","active":true,"parent":28,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":31,"name":"Website IPSWAYS.COM","billable":true,"description":"<br>","active":true,"parent":27,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":32,"name":"VMS-ERGO","billable":true,"description":"<br>","active":true,"parent":49,"position":1,"children":[71,72,85,96,102,107,108,139],"estimatedTime":null,"estimatedCompletionDate":null},{"id":42,"name":"VMS-Mobilcom","billable":true,"description":"","active":false,"parent":49,"position":0,"children":[43,44,45],"estimatedTime":null,"estimatedCompletionDate":null},{"id":43,"name":"Entwicklung","billable":true,"description":"","active":true,"parent":42,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":44,"name":"Wartung\/Betrieb","billable":true,"description":"","active":true,"parent":42,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":45,"name":"Projektmanagement","billable":true,"description":"","active":true,"parent":42,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":46,"name":"VMS intern","billable":false,"description":"","active":true,"parent":49,"position":3,"children":[47,50,61,101,109],"estimatedTime":null,"estimatedCompletionDate":null},{"id":47,"name":"Weiterentwicklung VMS allegemein","billable":false,"description":"alle Stunden, die keine kundenspezifische Entwicklungsarbeiten betreffen<br>","active":true,"parent":46,"position":0,"children":[125],"estimatedTime":null,"estimatedCompletionDate":null},{"id":49,"name":"VMS","billable":true,"description":"","active":true,"parent":1,"position":7,"children":[42,32,23,46,81,88,103,130],"estimatedTime":null,"estimatedCompletionDate":null},{"id":50,"name":"VMS-NG","billable":false,"description":"","active":false,"parent":46,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":60,"name":"LKA","billable":true,"description":"","active":true,"parent":1,"position":41,"children":[166,201],"estimatedTime":176,"estimatedCompletionDate":"2016-09-30"},{"id":61,"name":"APP","billable":false,"description":"","active":false,"parent":46,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":67,"name":"Support","billable":true,"description":"Supportleistungen au\u00dferhalb Wartung und Betrieb\u200b","active":true,"parent":23,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":68,"name":"Leistungserfassung, Ratecard, Onboarding","billable":true,"description":"<br>","active":true,"parent":23,"position":3,"children":[],"estimatedTime":188,"estimatedCompletionDate":null},{"id":71,"name":"Wartung\/Betrieb\/Bugfix","billable":false,"description":"<br>","active":true,"parent":32,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":72,"name":"Entwicklung allgemein","billable":true,"description":"","active":true,"parent":32,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":81,"name":"VMS-Car2Go","billable":true,"description":"","active":false,"parent":49,"position":4,"children":[82,83,84,86,99],"estimatedTime":null,"estimatedCompletionDate":null},{"id":82,"name":"Wartung\/Betrieb","billable":true,"description":"","active":true,"parent":81,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":83,"name":"Support","billable":true,"description":"","active":true,"parent":81,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":84,"name":"Setup","billable":true,"description":"","active":true,"parent":81,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":85,"name":"SAP-Anbindung","billable":true,"description":"","active":false,"parent":32,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":86,"name":"Car2Go Customizing","billable":true,"description":"","active":true,"parent":81,"position":3,"children":[],"estimatedTime":224,"estimatedCompletionDate":null},{"id":88,"name":"VMS-Signal-Iduna","billable":true,"description":"","active":true,"parent":49,"position":5,"children":[89,90,91,92,93,94,95,97,98,100,140,143,145,183,187],"estimatedTime":null,"estimatedCompletionDate":null},{"id":89,"name":"Setup","billable":true,"description":"","active":false,"parent":88,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":90,"name":"Wartung\/Betrieb\/Bugfix","billable":false,"description":"Deployen, etc. <br>","active":true,"parent":88,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":91,"name":"Support","billable":true,"description":"Konkrete Kundenfragen zum Produkt<br>","active":true,"parent":88,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":92,"name":"Entwicklung\/Customizing","billable":true,"description":"Alle Programmiert\u00e4tigkeiten bis 10 PT Aufwand<br>","active":true,"parent":88,"position":3,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":93,"name":"OCI-Schnittstelle","billable":true,"description":"<br>","active":false,"parent":88,"position":4,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":94,"name":"Lieferanten- und Ressourcenbewertung","billable":true,"description":"<br>","active":false,"parent":88,"position":5,"children":[],"estimatedTime":120,"estimatedCompletionDate":"2017-08-31"},{"id":95,"name":"Reisekosten","billable":true,"description":"<br>","active":false,"parent":88,"position":6,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":96,"name":"intern","billable":false,"description":"","active":true,"parent":32,"position":3,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":97,"name":"intern","billable":false,"description":"","active":true,"parent":88,"position":7,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":98,"name":"Kundenmeetings allgemein","billable":true,"description":"<br>","active":true,"parent":88,"position":8,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":99,"name":"Intern","billable":true,"description":"","active":true,"parent":81,"position":4,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":100,"name":"LDAP Anbindung","billable":true,"description":"","active":false,"parent":88,"position":9,"children":[],"estimatedTime":48,"estimatedCompletionDate":"2017-08-31"},{"id":101,"name":"VMS Neues Frontend","billable":false,"description":"","active":true,"parent":46,"position":3,"children":[163,178,165,172,173,180,171,164],"estimatedTime":null,"estimatedCompletionDate":null},{"id":102,"name":"Support","billable":true,"description":"","active":true,"parent":32,"position":4,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":103,"name":"VMS-HSBC","billable":true,"description":"","active":false,"parent":49,"position":6,"children":[104,105,106],"estimatedTime":null,"estimatedCompletionDate":null},{"id":104,"name":"Wartung\/Betrieb","billable":true,"description":"","active":true,"parent":103,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":105,"name":"Customizing","billable":true,"description":"","active":true,"parent":103,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":106,"name":"Intern","billable":true,"description":"","active":true,"parent":103,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":107,"name":"Leistungserfassung","billable":true,"description":"","active":false,"parent":32,"position":5,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":108,"name":"AN\u00dc","billable":true,"description":"","active":true,"parent":32,"position":6,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":109,"name":"VMS Testing","billable":false,"description":"","active":true,"parent":46,"position":4,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":119,"name":"Perm\/Contracting Anpassungen","billable":true,"description":"","active":true,"parent":28,"position":2,"children":[],"estimatedTime":128,"estimatedCompletionDate":null},{"id":122,"name":"Business Development","billable":false,"description":"","active":true,"parent":12,"position":6,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":124,"name":"DSGVO","billable":true,"description":"","active":false,"parent":28,"position":3,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":125,"name":"DSGVO","billable":false,"description":"","active":true,"parent":47,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":130,"name":"VMS-MunichRe","billable":true,"description":"","active":true,"parent":49,"position":7,"children":[131,138,146,147,148,158],"estimatedTime":null,"estimatedCompletionDate":null},{"id":131,"name":"Setup","billable":true,"description":"","active":true,"parent":130,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":132,"name":"Infrastruktur\/Betrieb","billable":false,"description":"","active":true,"parent":12,"position":7,"children":[133,134,135,136,137,142],"estimatedTime":null,"estimatedCompletionDate":null},{"id":133,"name":"debian9 VM Template","billable":false,"description":"","active":true,"parent":132,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":134,"name":"SVN-Git Umstellung","billable":false,"description":"","active":true,"parent":132,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":135,"name":"Jenkins","billable":false,"description":"","active":true,"parent":132,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":136,"name":"root1140","billable":false,"description":"","active":true,"parent":132,"position":3,"children":[141],"estimatedTime":null,"estimatedCompletionDate":null},{"id":137,"name":"fruuchtkorb","billable":false,"description":"","active":true,"parent":132,"position":4,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":138,"name":"Kundenmeetings allgemein","billable":true,"description":"","active":true,"parent":130,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":139,"name":"Itergo","billable":true,"description":"","active":false,"parent":32,"position":7,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":140,"name":"Remote-Stundensatz","billable":true,"description":"","active":false,"parent":88,"position":10,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":141,"name":"VM Umzug debian9","billable":false,"description":"","active":true,"parent":136,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":142,"name":"Zabbix","billable":false,"description":"","active":true,"parent":132,"position":5,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":143,"name":"Leistungserfassung","billable":true,"description":"","active":false,"parent":88,"position":11,"children":[],"estimatedTime":40,"estimatedCompletionDate":null},{"id":145,"name":"CR20190410","billable":true,"description":"","active":false,"parent":88,"position":12,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":146,"name":"Wartung\/Betrieb\/Bugfix","billable":true,"description":"<br>","active":true,"parent":130,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":147,"name":"Support","billable":true,"description":"","active":true,"parent":130,"position":3,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":148,"name":"Entwicklung allgemein","billable":true,"description":"","active":true,"parent":130,"position":4,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":158,"name":"Coupa Integration","billable":true,"description":"","active":true,"parent":130,"position":5,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":163,"name":"VMS AN-Rolle f\u00fcr Iduna","billable":false,"description":"","active":true,"parent":101,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":164,"name":"VMS Neues Frontend AG-Rolle","billable":false,"description":"","active":true,"parent":101,"position":7,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":165,"name":"VMS AG-Rolle","billable":false,"description":"","active":true,"parent":101,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":166,"name":"Neuentwicklung Upload Portal","billable":true,"description":"","active":true,"parent":60,"position":0,"children":[169,167,168],"estimatedTime":176,"estimatedCompletionDate":"2019-09-14"},{"id":167,"name":"Entwicklung","billable":true,"description":"","active":true,"parent":166,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":168,"name":"Test\/Abnahme","billable":true,"description":"","active":true,"parent":166,"position":2,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":169,"name":"Besprechung","billable":true,"description":"","active":true,"parent":166,"position":0,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":171,"name":"VMS-Eink\u00e4ufer-Rolle","billable":false,"description":"","active":true,"parent":101,"position":6,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":172,"name":"VMS AG-Rolle f\u00fcr Iduna","billable":false,"description":"","active":true,"parent":101,"position":3,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":173,"name":"VMS AG-Rolle f\u00fcr Ergo","billable":false,"description":"","active":true,"parent":101,"position":4,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":178,"name":"VMS AN-Rolle f\u00fcr ERGO","billable":false,"description":"VMS AN-Rolle f\u00fcr ERGO","active":true,"parent":101,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":180,"name":"VMS AG-Rolle f\u00fcr Munichre","billable":false,"description":"","active":true,"parent":101,"position":5,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":183,"name":"Buchen von Team","billable":true,"description":"","active":false,"parent":88,"position":13,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":187,"name":"Bearbeiten von Vertragsdetails","billable":true,"description":"","active":false,"parent":88,"position":14,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":194,"name":"greybee","billable":true,"description":"","active":true,"parent":1,"position":36,"children":[195,196],"estimatedTime":null,"estimatedCompletionDate":"2021-05-03"},{"id":196,"name":"Entwicklung","billable":true,"description":"","active":true,"parent":194,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":"2021-05-03"},{"id":201,"name":"Java-Upgrade","billable":true,"description":"","active":true,"parent":60,"position":1,"children":[],"estimatedTime":null,"estimatedCompletionDate":null},{"id":209,"name":"KVBW","billable":true,"description":"","active":true,"parent":1,"position":32,"children":[],"estimatedTime":null,"estimatedCompletionDate":null}]')
    seen = []
    if not body:
        print("RIP")
        return
    def traverse(proj, acc = []):
        seen.append(proj["id"])
        if not proj['active']:
            seen.extend(proj['children'])
            return acc
        cld = []
        acc.append({'id': proj['id'], 'name': proj['name']})
        for child_id in proj['children']:
            child = next((x for x in body if x["id"] == child_id), None)
            if not child:
                continue
            logging.debug(f'append {child["id"]}')
            cld.append(traverse(child, []))
        if len(cld):
            acc.append(cld)
        if len(acc) > 1:
            return acc
        else:
            return acc[0]
    rows = []
    for project in body[1:]:
        if project['id'] in seen:
            continue
        seen.append(project['id'])

        if not project['active']:
            seen += project['children']
            continue
        seen.append(project['id'])
        logging.debug(f'traverse project {project["id"]}')
        res = traverse(project, [])
        rows.append(res)
    
    def print_proj(proj, acc, depth=0):
        spc = ''
        for x in range(depth):
            spc += "   " 
        if not isinstance(proj, list):
            return f"\n{acc}{proj['id']}: {proj['name']}"
        for elem in proj:
            if isinstance(elem, list):
                acc += print_proj(elem, f"", depth+1)
            else:
                acc += f"\n{spc}{elem['id']}: {elem['name']}"
        return acc
    
    for row in rows:
        print(print_proj(row, ""))   

def round_day(day):
    rounded_day = day.copy()
    day_sum = reduce(lambda acc, curr: acc + (curr["stop"] - curr["start"]).total_seconds() / 60, rounded_day, 0)
    mdl = int(day_sum % 15)
    sessions = []
    if mdl is not 0:
        logging.debug(mdl)
        rounded_day[-1]["stop"] = rounded_day[-1]["stop"] + timedelta(minutes=15 - mdl)
        logging.debug(f'{15 - mdl} added')
        day_sum += 15 - mdl
    
    for session in rounded_day:
        logging.debug(f"{datetime.strftime(session['start'], '%H:%M')} - {datetime.strftime(session['stop'], '%H:%M')}: {session['note']} ({session['stop'] - session['start']})")
    day_sum_date = datetime.fromtimestamp(0).replace(second=0, minute=0, hour=0) + timedelta(minutes = day_sum)
    logging.debug(day_sum, f"{day_sum_date.hour}:{day_sum_date.minute}")
    logging.debug(rounded_day)
    def map_sessions(session):
        delta = session['stop'] - session['start']
        delta_date = datetime.fromtimestamp(0).replace(second=0, minute=0, hour=0) + delta
        return {
            "start": datetime.strftime(session['start'], '%H:%M'),
            "stop": datetime.strftime(session['stop'], '%H:%M'),
            "note": session["note"],
            "duration": f"{delta_date.hour:02d}:{delta_date.minute:02d}"
        }
    result = {
        "day_sum": f"{day_sum_date.hour:02d}:{day_sum_date.minute:02d}",
        "day_sum_seconds": day_sum_date.hour * 3600 + day_sum_date.minute * 60,
        "day_begin": rounded_day[0]["start"],
        "day_end": rounded_day[-1]["stop"],
        "day_summary": ", ".join(reduce(lambda r, x: r + [x] if x not in r else r, list(map(lambda y: y["note"], rounded_day)), [])),
        "sessions": list(map(map_sessions, rounded_day))
    }
    return result

def add_project_times(project_id, date, rounded_day):
    payload = {
        "date": f"{date} 00:00:00",
        "project": project_id,
        "task": 1,
        "duration": rounded_day['day_sum_seconds'],
        "comment": rounded_day['day_summary'],
        "billable": True
    }
    request = requests.post('https://fruuts.timicx.net/ws/2.0/project_time.json', auth=(args.username, args.password), json=payload)
    print(request)
    print(request.json())
    #{"date":"2022-06-27 00:00:00","project":29,"task":1,"duration":60,"comment":"test","begin":null,"end":null,"billable":true}

def get_project_times(project_id):
    request = requests.get(f'https://fruuts.timicx.net/ws/2.0/project_time.json?project={project_id}', auth=(args.username, args.password))
    return request.json()

def extract_id(project):
    res = re.search("(\d+)$", project)
    if not res:
        raise Exception("Trailing ID missing")
    return re.search("(\d+)$", project).group(1)

if __name__ == "__main__":
    if args.write_report:
        if not args.month:
            print("Month missing")
            exit(1)
        data = parse_xml(args.file)
        if not args.project or not data[args.project]:
            print(f"Project not found")
            exit(1)
        with open(f"{args.month}_{args.project}.csv", "w") as f:
            f.write('date;start;stop;note;duration;month_sum\n')
            month_sum_date = datetime.fromtimestamp(0, tz=timezone.utc).replace(second=0, minute=0, hour=0)
            print(month_sum_date.timestamp())
            for date in data[args.project]:
                day = list(filter(lambda x: not x['billed'], data[args.project][date]))
                if len(day):
                    rounded_day = round_day(day)
                    #print(date, rounded_day['day_sum'], rounded_day['day_summary'])
                    for session in rounded_day['sessions']:
                        f.write(f"{date};{session['start']};{session['stop']};{session['note']};{session['duration']};\n")
                        month_sum_date += timedelta(hours=int(session['duration'][:2]), minutes=int(session['duration'][3:]))
                        #print(f"{session['start']} - {session['stop']}: {session['note']} ({session['duration']})")
            total_seconds = int(month_sum_date.timestamp())
            f.write(f";;;;;{int(total_seconds/3600):02d}:{int(total_seconds/60 %60):02d}")
            f.close()
            exit(0)
        
    if args.list_projects:
        if not args.username or not args.password:
            print("Username or password missing")
            exit(1)
        get_projects()
    if args.add_sessions:
        data = parse_xml(args.file)
        if not args.project or not data[args.project]:
            print(f"Project not found")
            exit(1)
        project_id = extract_id(args.project)
        print(list(map(lambda y: y["date"][:10], get_project_times(project_id))))
        booked_dates = list(reduce(lambda r, x: r + [x] if x not in r else r, list(map(lambda y: y["date"][:10], get_project_times(project_id))), []))
        for date in data[args.project]:
            unbilled_dates = list(filter(lambda x: not x['billed'], data[args.project][date]))
            unbilled_dates = list(reduce(lambda r, x: r + [x] if x not in r else r, list(map(lambda y: y["date"][:10], unbilled_dates)), list(map(lambda z: z[:10], booked_dates))))
            unbooked_dates = list(set(unbilled_dates) - set(booked_dates))
            for unbilled_date in unbooked_dates:
                print(unbilled_date)
                if unbilled_date not in data[args.project]:
                    continue
                rounded_day = round_day(data[args.project][unbilled_date])
                print(rounded_day)
                add_project_times(209, date, rounded_day)
    if args.list_sessions:
        data = parse_xml(args.file)
        if not args.project or not data[args.project]:
            print(f"Project not found")
            exit(1)
        for date in data[args.project]:
            unbilled_day = list(filter(lambda x: not x['billed'], data[args.project][date]))
            if len(unbilled_day):
                rounded_day = round_day(unbilled_day)
                print(date, rounded_day['day_sum'], rounded_day['day_summary'])
                for session in rounded_day['sessions']:
                    print(f"{session['start']} - {session['stop']}: {session['note']} ({session['duration']})")

    