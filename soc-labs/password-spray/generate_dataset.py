"""Create fictional normalized Windows authentication events; no live login attempts."""
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
BASE = datetime(2026, 10, 20, 6, 0, tzinfo=timezone.utc)
FIELDS = ['TimeCreated','EventRecordID','EventCode','Computer','TargetDomainName','TargetUserName','SourceIp','LogonType','AuthenticationPackageName','Status','SubStatus','Synthetic']

def build():
    rows = []
    def add(seconds, code, user, ip):
        rows.append(dict(TimeCreated=(BASE+timedelta(seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ'), EventRecordID='', EventCode=code, Computer='FS-LAB-01', TargetDomainName='LAB', TargetUserName=user, SourceIp=ip, LogonType=3, AuthenticationPackageName='NTLM', Status='0xC000006D' if code==4625 else '', SubStatus='0xC000006A' if code==4625 else '', Synthetic='true'))
    # Control A: fictional user mistypes twice, then succeeds.
    for t in (5,20): add(t,4625,'nora','10.20.30.60')
    add(35,4624,'nora','10.20.30.60')
    # Attack fixture: two rounds against eight users from one fictional source.
    users=['alice','ben','carla','dan','emma','faisal','grace','hugo']
    for i,user in enumerate(users*2): add(60+i*5,4625,user,'10.20.30.45')
    add(180,4624,'alice','10.20.30.45')
    # Control B: repeated failures for one fictional service account.
    for t in (185,190,195): add(t,4625,'svc_backup','10.20.30.99')
    rows.sort(key=lambda r:r['TimeCreated'])
    for i,row in enumerate(rows,10001): row['EventRecordID']=i
    return rows

if __name__=='__main__':
    path=Path(__file__).parent/'data/synthetic_windows_auth.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(build())
    print(f'Wrote 23 synthetic events to {path.name}')
