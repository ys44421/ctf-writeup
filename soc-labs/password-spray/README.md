# SOC lab investigating suspected password spraying

A small defensive portfolio exercise for an entry-level SOC analyst. It covers alert triage, evidence review, false-positive assessment, MITRE ATT&CK mapping, and escalation. The investigation uses fictional Windows-style authentication records and includes Splunk searches and a runnable Python reference analyzer.

**Provenance and validation:** Prepared with AI assistance for Younes Sarioul. All 23 records are generated synthetic training data, not a Windows EVTX export or a real incident. No attack or live login attempt was performed. The Python analyzer and automated checks were run during preparation. The SPL searches have not been executed in a Splunk instance; hands-on Splunk validation by the portfolio owner remains pending. This lab does not establish production SOC experience.

## Start here

1. Read the [investigation report](report.md).
2. Inspect the [synthetic CSV](data/synthetic_windows_auth.csv).
3. Run the offline analysis using Python 3.10 or newer, with no extra packages:

```bash
cd soc-labs/password-spray
python analyze.py
python -m unittest discover -s tests -v
```

Use `python3` if that is your Python command. The scripts use paths relative to their own location, except unittest discovery, which should be run from the directory shown above.

The expected result is one candidate campaign: **16 failures, 8 accounts**, and one correlated success for `LAB\alice`. Compare your output with [expected findings](expected_findings.json). See [validation notes](validation.md) for what was and was not tested.

## Try it in Splunk

1. In a Splunk app where you can manage lookups, upload `data/synthetic_windows_auth.csv` as a lookup table file named **synthetic_windows_auth.csv**. Keep its header and contents unchanged. Do not upload it as indexed events for these queries.
2. Set your Splunk display timezone to **UTC** so formatted times match this report. These `inputlookup` queries read the complete fixture; they do not depend on the search time picker.
3. Run [01_detect_spray.spl](queries/01_detect_spray.spl). Expected: one row for `10.20.30.45`, 16 failures and 8 accounts.
4. Run [02_correlate_success.spl](queries/02_correlate_success.spl). Expected: two rows, including the benign `nora` control and `alice`. This query finds failure-to-success sequences generally; it does **not** label both as attacks.
5. Match those rows to query 1 by source IP, destination computer and domain. Confirm the preceding failure belongs to the alerted interval. Only `alice` belongs to the candidate spray campaign in this fixture. Her success is 80 seconds after her most recent failure.
6. Save actual query output and screenshots after running the searches yourself. Record your Splunk version, timezone, and any field or query changes. Mark Splunk validation complete only after verifying both results.

The fixture uses simplified field names. `SourceIp` is a normalized name for the Windows event's `IpAddress` field; `EventCode` represents `EventID`; `TimeCreated` represents the UTC event time. The remaining columns are a subset of Windows event fields plus `Synthetic`. This is not Splunk CIM and is not a drop-in search for a production Windows index. Production field extractions must be checked first.

## Files

| File | Purpose |
|---|---|
| `report.md` | Investigation, evidence, alternative explanations and escalation handoff |
| `data/synthetic_windows_auth.csv` | 23 fictional records with stable record IDs |
| `generate_dataset.py` | Deterministically rebuilds the fixture without contacting any system |
| `queries/01_detect_spray.spl` | Detects a multi-account failure pattern in fixed five-minute buckets |
| `queries/02_correlate_success.spl` | Finds a success within ten minutes after a failure for the same source, host, domain and user |
| `analyze.py` | Offline reference result, including campaign membership correlation |
| `expected_findings.json` | Saved reference output |
| `tests/test_analyze.py` | Positive and negative checks of the Python analysis |
| `validation.md` | Validation status and known detection limitations |

## Portfolio owner next steps

Run the Python exercise, then execute the SPL searches in your own lab. Explain why `nora` is excluded, why `alice` is escalated, and what evidence is still missing. Add your own screenshots and observations. Describe this as a **synthetic SOC investigation lab**, with the actual tools you personally ran, rather than as a real customer incident.

Official references are linked in the [report](report.md#references).
