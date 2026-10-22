import copy
import csv
import unittest
from pathlib import Path
from analyze import analyze
ROOT=Path(__file__).resolve().parents[1]

class CorrelationTests(unittest.TestCase):
    def setUp(self):
        with (ROOT/'data/synthetic_windows_auth.csv').open(newline='') as f:
            self.rows=list(csv.DictReader(f))
    def test_known_campaign_and_controls(self):
        result=analyze(self.rows)
        self.assertEqual(result['alert_count'],1)
        self.assertEqual(result['alerts'][0]['failed_attempts'],16)
        self.assertEqual(result['alerts'][0]['affected_accounts'],8)
        self.assertEqual([r['user'] for r in result['correlated_successes']],['alice'])
        self.assertEqual(result['correlated_successes'][0]['seconds_since_previous_failure'],80)
    def test_benign_controls_do_not_trigger(self):
        rows=[r for r in self.rows if r['SourceIp']!='10.20.30.45']
        self.assertEqual(analyze(rows)['alerts'],[])
        self.assertEqual(analyze(rows)['correlated_successes'],[])
    def test_success_before_failures_is_not_correlated(self):
        rows=copy.deepcopy(self.rows)
        for row in rows:
            if row['SourceIp']=='10.20.30.45' and row['EventCode']=='4624': row['TimeCreated']='2026-10-20T06:00:00Z'
        self.assertEqual(analyze(rows)['correlated_successes'],[])
    def test_other_user_host_domain_or_source_is_not_correlated(self):
        for field,value in [('TargetUserName','other'),('Computer','OTHER-HOST'),('TargetDomainName','OTHER'),('SourceIp','10.20.30.46')]:
            with self.subTest(field=field):
                rows=copy.deepcopy(self.rows)
                for row in rows:
                    if row['SourceIp']=='10.20.30.45' and row['EventCode']=='4624': row[field]=value
                self.assertEqual(analyze(rows)['correlated_successes'],[])
    def test_success_outside_ten_minutes_is_not_correlated(self):
        rows=copy.deepcopy(self.rows)
        for row in rows:
            if row['SourceIp']=='10.20.30.45' and row['EventCode']=='4624': row['TimeCreated']='2026-10-20T06:20:00Z'
        self.assertEqual(analyze(rows)['correlated_successes'],[])
    def test_many_failures_on_one_account_are_not_a_spray_alert(self):
        rows=copy.deepcopy(self.rows)
        for row in rows:
            if row['SourceIp']=='10.20.30.45': row['TargetUserName']='alice'
        self.assertEqual(analyze(rows)['alerts'],[])

if __name__=='__main__': unittest.main()
