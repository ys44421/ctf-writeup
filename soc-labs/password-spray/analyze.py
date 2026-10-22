"""Offline reference analysis of the synthetic fixture. Does not execute Splunk SPL."""
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

def epoch(value):
    return int(datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp())

def iso(value):
    return datetime.fromtimestamp(value,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def analyze(rows, min_failures=12, min_users=6):
    events=[]
    for row in rows:
        event=dict(row)
        event['EventCode']=int(event['EventCode'])
        event['LogonType']=int(event['LogonType'])
        event['EventRecordID']=int(event['EventRecordID'])
        event['epoch']=epoch(event['TimeCreated'])
        if event['EventCode'] in (4624,4625) and event['LogonType']==3:
            events.append(event)
    events.sort(key=lambda r:(r['epoch'],r['EventRecordID']))
    groups=defaultdict(list)
    for e in events:
        if e['EventCode']==4625:
            key=(e['epoch']//300*300,e['SourceIp'],e['Computer'],e['TargetDomainName'])
            groups[key].append(e)
    alerts=[]; flagged=set()
    for key, failures in sorted(groups.items()):
        accounts=sorted({r['TargetUserName'] for r in failures})
        if len(failures)>=min_failures and len(accounts)>=min_users:
            flagged.add(key)
            alerts.append(dict(bucket_start_utc=iso(key[0]),source_ip=key[1],computer=key[2],domain=key[3],failed_attempts=len(failures),affected_accounts=len(accounts),targeted_accounts=accounts,first_failure_utc=failures[0]['TimeCreated'],last_failure_utc=failures[-1]['TimeCreated'],failure_record_ids=[r['EventRecordID'] for r in failures]))
    prior={}; successes=[]
    for e in events:
        key=(e['SourceIp'],e['Computer'],e['TargetDomainName'],e['TargetUserName'])
        if e['EventCode']==4625:
            prior[key]=e
        elif key in prior:
            previous=prior[key]
            delta=e['epoch']-previous['epoch']
            campaign=(previous['epoch']//300*300,*key[:3])
            if 0<delta<=600 and campaign in flagged:
                successes.append(dict(source_ip=key[0],computer=key[1],domain=key[2],user=key[3],success_time_utc=e['TimeCreated'],success_record_id=e['EventRecordID'],previous_failure_record_id=previous['EventRecordID'],seconds_since_previous_failure=delta))
    return dict(total_input_events=len(rows),events_analyzed=len(events),alert_count=len(alerts),alerts=alerts,correlated_successes=successes)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('csv_path',nargs='?',default=str(Path(__file__).parent/'data/synthetic_windows_auth.csv'))
    args=parser.parse_args()
    with open(args.csv_path,newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
    print(json.dumps(analyze(rows),indent=2))
