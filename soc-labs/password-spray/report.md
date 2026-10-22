# Investigation of suspected password spraying followed by a successful logon

**Case:** SOC-LAB-001  
**Type:** Synthetic training scenario  
**Status:** Investigation example; Splunk execution pending  
**Scenario event date:** 20 October 2026; all times below are UTC  
**Preparation date:** 21 October 2026

## Executive assessment

The synthetic dataset contains 16 failed network logons against eight accounts from `10.20.30.45` to `FS-LAB-01`, followed by a successful network logon for one targeted account, `LAB\alice`. This warrants escalation as suspected multi-account credential guessing with possible account misuse. Password spraying is a reasonable hypothesis, but authentication logs do not reveal the attempted passwords and cannot prove that the same password was used across accounts.

The fixture was deliberately generated to represent an attack pattern plus two benign controls. The candidate alert is therefore a true positive **within the simulation**. In a live case, the appropriate status would remain **suspicious, pending validation** until asset ownership, authorization and account activity are checked. A successful logon does not by itself prove an account was compromised.

## Scope and evidence

This is an AI-assisted portfolio lab prepared for Younes Sarioul. The events are normalized synthetic CSV rows, not collected EVTX files. Record IDs are fictional but stable within the dataset. There are no real users, passwords, customer records or external indicators. The offline Python analysis was executed during preparation; no production incident handling or completed Splunk execution is claimed.

| Evidence | Observation |
|---|---|
| Source | `10.20.30.45`, a private lab address; ownership unknown from logs |
| Destination | `FS-LAB-01`, fictional Windows file server |
| Event 4625 | 16 failed logons, records 10004 through 10019 |
| Accounts | alice, ben, carla, dan, emma, faisal, grace, hugo in domain LAB |
| Failure interval | 06:01:00 through 06:02:15; two failures per account |
| Failure details | Status `0xC000006D`, SubStatus `0xC000006A` |
| Event 4624 | Record 10020: `LAB\alice` at 06:03:00, same source and destination |
| Logon type | 3, network logon; this alone does not identify the application or prove RDP |
| Authentication package | NTLM in the synthetic records |

Microsoft documents 4625 as a failed logon and 4624 as creation of a successful logon session on the destination computer. SubStatus `0xC000006A` indicates a bad password. These event meanings guide interpretation, rather than establishing malicious intent by themselves. [1][2]

## Detection and investigation steps

1. Check field completeness and timestamps. All 23 fixture rows contain source, destination, domain, user, event code and UTC time. The `Synthetic` field explicitly identifies training data.
2. Group network logon failures by source, destination and domain in fixed five-minute buckets. The example rule requires at least 12 failures across at least six distinct users. These are lab thresholds chosen for demonstration, not vendor defaults or tuned production thresholds.
3. Inspect the targeted accounts and individual records. Source `10.20.30.45` produces two failures per account across eight accounts in 75 seconds. Breadth across accounts makes this more suspicious than repeated typos by one user.
4. Search successes for the same source, destination, domain and user after a preceding failure, within ten minutes. Record 10020 follows alice's failure at 06:01:40, record 10012, by 80 seconds. Confirm that the preceding failure belongs to the candidate campaign.
5. Compare controls. `nora` has two failures and then a success from `10.20.30.60`; `svc_backup` has three failures from `10.20.30.99` against one account. Neither meets the multi-account rule. The fixture design identifies them as benign examples; real incidents would still require contextual verification.

## Timeline

| UTC time | Observation | Interpretation |
|---|---|---|
| 06:00:05 to 06:00:35 | Two failures, then success for nora from another source | Control showing that failure followed by success can be ordinary user activity |
| 06:01:00 to 06:02:15 | 16 failures across eight users from 10.20.30.45 | Candidate multi-account guessing campaign |
| 06:03:00 | Successful network logon for alice from 10.20.30.45 | Increases urgency; requires confirmation of legitimate use |
| 06:03:05 to 06:03:15 | Three failures for svc_backup from a third source | Single-account control; investigate separately if seen in production |

## Alternative explanations and confidence

A misconfigured application, shared gateway, authorized security test or stale saved credentials could generate repeated failures. The CSV contains no CMDB ownership, approved testing schedule, user confirmation or endpoint process telemetry. These explanations have not been ruled out by real evidence.

The breadth of accounts, short interval and subsequent success on a targeted account support escalation. Confidence is high that the fixture matches the defined detection; confidence in malicious intent in a real equivalent case would depend on the missing context. An internal IP address is neither an external reputation indicator nor evidence of safety.

## MITRE ATT&CK mapping

**Primary hypothesis: T1110.003 Password Spraying, Credential Access.** MITRE describes attempts using one or a small number of passwords across many accounts. The observed multi-account pattern is consistent with this hypothesis; these logs do not contain passwords, so the exact sub-technique remains unconfirmed outside the known synthetic scenario. [3]

The successful logon raises possible credential misuse. Do not treat it alone as confirmed Valid Accounts activity, lateral movement, data access or exfiltration. Additional telemetry is needed before extending the mapping.

## Escalation decision and handoff

**Decision:** Escalate to Tier 2 or the incident-response lead for urgent investigation. Assign high priority in this example because a candidate spray is followed by a success on a targeted account. Actual priority must follow the organization's severity matrix and asset criticality.

> Synthetic case SOC-LAB-001: FS-LAB-01 recorded 16 failed network logons across eight LAB accounts from 10.20.30.45 between 06:01:00 and 06:02:15 UTC. LAB\alice then logged on successfully at 06:03:00 from the same source, 80 seconds after her prior failure. Please validate source ownership, authorized testing and alice's activity. Possible password spraying and account misuse; compromise and impact are not yet confirmed. Evidence: CSV records 10004-10020 and the attached query logic.

Requested follow-up:

- Identify the source host and whether it is an approved scanner, shared service or testing system.
- Verify alice's activity through an established contact channel; check privileges and usual logon patterns.
- Review relevant domain-controller authentication records and source/destination EDR telemetry. Correlate process, session and file-share activity where collected.
- Preserve original event exports and related telemetry with timestamps, collection details and integrity hashes in a real investigation.
- If unauthorized activity is confirmed, follow the response playbook for session termination, credential reset or host isolation with the authorized team. No containment action was performed in this lab.

## Limits and next steps

The detection uses fixed five-minute buckets and can miss campaigns split across bucket boundaries. Slow or distributed spraying can evade these thresholds. NTLM-style failure examples do not cover every authentication path; relevant Kerberos or cloud events may be necessary. The tiny fixture is a demonstration, not evidence of production detection coverage or accuracy.

Complete the Splunk steps in the [lab guide](README.md), preserve actual results and document any differences. See [validation notes](validation.md) for executed checks and the distinction between broad failure-success correlation and campaign membership.

## References

1. [Microsoft Learn: Event 4625, an account failed to log on](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625).
2. [Microsoft Learn: Event 4624, an account was successfully logged on](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624).
3. [MITRE ATT&CK: T1110.003 Password Spraying](https://attack.mitre.org/techniques/T1110/003/).
4. [Splunk documentation: inputlookup](https://help.splunk.com/en/splunk-enterprise/search/spl-search-reference/9.4/search-commands/inputlookup).
5. [Splunk documentation: streamstats](https://help.splunk.com/en/splunk-enterprise/search/spl-search-reference/9.4/search-commands/streamstats).
