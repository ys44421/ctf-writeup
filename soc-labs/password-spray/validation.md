# Validation notes

## Executed during preparation

The following commands ran successfully with Python 3 in the preparation environment:

```bash
python3 generate_dataset.py
python3 analyze.py > expected_findings.json
python3 -m unittest discover -s tests -v
```

The generator creates 23 deterministic synthetic rows. The saved analyzer result contains one campaign from `10.20.30.45` to `FS-LAB-01`, 16 failures across eight LAB users, and alice's successful logon at `06:03:00Z`, 80 seconds after her last failure. The successful event is record 10020 and the preceding account-specific failure is record 10012.

All six automated checks passed:

1. The known candidate campaign is detected, with the expected account count and correlated success.
2. The two benign control scenarios alone do not generate a campaign.
3. A success before the failures is not correlated.
4. A different user, destination host, domain or source is not correlated (four subcases).
5. A success more than ten minutes after a prior failure is not correlated.
6. Many failures for one account do not trigger this multi-account rule.

These tests check the offline Python reference implementation. They do not execute or validate Splunk's parser, search engine, timestamp settings, field extraction or `streamstats` behavior.

## Expected SPL results and manual correlation

**SPL engine validation is pending.** Run the steps in the lab README before reporting that Splunk searches were tested.

Query 1 should produce one candidate campaign row. Query 2 intentionally performs broader failure-to-success correlation and should produce:

| User | Source | Successful event | Prior failure | Seconds elapsed | Candidate campaign member |
|---|---|---|---|---|---|
| nora | 10.20.30.60 | 10003 | 10002 | 15 | No |
| alice | 10.20.30.45 | 10020 | 10012 | 80 | Yes |

Only after matching query 2 to query 1 by source, destination, domain and the preceding failure interval should the analyst associate a success with a candidate spray. Python performs that extra campaign-membership check; query 2 alone does not. A failure-success sequence is a triage lead, not an automatic compromise verdict.

## Limitations

- Fixed five-minute buckets can split an attack across boundaries. Thresholds are illustrative; there is no baseline tuning or production evaluation.
- Correlation uses source, host, domain, user and time. It does not establish the human operator's identity. NAT, shared systems and reused accounts complicate attribution.
- The fixture uses UTC and NTLM network-logon examples. Real collection requires source-specific field mapping, telemetry completeness checks and authentication coverage.
- No EVTX files, real SIEM screenshots, EDR evidence or production actions are included.
- No performance, alert precision or detection-coverage claim is made from this small dataset.

## Portfolio owner execution record

After running the lab personally, add your date, environment, Splunk version, actual results, screenshots and any query corrections. Keep the synthetic provenance visible. Do not replace expected results with a claim of successful execution until you have evidence.
