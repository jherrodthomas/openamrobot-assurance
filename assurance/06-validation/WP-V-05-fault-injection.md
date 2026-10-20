# WP-V-05 Fault injection and fault-list validation specification and report

| Field | Value |
|---|---|
| Work product | WP-V-05 Fault injection and fault-list validation specification and report |
| Standard reference | SRP/CS: 13849-2 §5, Annex A–D; ASPICE: SYS.4, SWE.6 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G4** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

Fault injection against the ISO 13849-2 fault lists and the failure analyses: each single fault of WP-H-03 and WP-W-04 injected or justified as excluded, with the observed behaviour of the safety function.

## 2. Fault catalogue

FI-nn from the fault lists: open channel, short across contacts, stuck contactor, scanner OSSD short, lost serial, stalled MCU, driver fault latch, under-voltage.

## 3. Injection method per fault

Bench or robot; how injected; what is observed.

## 4. Report

Per fault: detected, safe state reached, time; exclusions with justification.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G4 |
