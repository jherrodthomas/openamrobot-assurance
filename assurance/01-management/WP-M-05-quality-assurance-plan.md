# WP-M-05 Quality management and quality assurance plan

| Field | Value |
|---|---|
| Work product | WP-M-05 Quality management and quality assurance plan |
| Standard reference | SRP/CS: 61508-1 §6.2; IEC 62443: 62443-4-1 SM-5; Other: ISO 9001 (informative); ASPICE: SUP.1 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G0** ([WP-M-00](WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

How quality is assured on the fork: the quality rules for work products and code, the audits QA performs, and how QA findings reach the gate reviews.

## 2. Quality objectives

Every work product has a document-control header, a review record and traceable open items; every safety-relevant change has an impact analysis; every generated figure is checked by CI.

## 3. Quality assurance activities

Work product audits per gate (checklists of WP-P-05), process audits (configuration management, change control, problem resolution), tool checks (WP-P-07).

## 4. Independence of QA

QA is independent of the author (WP-M-02 §3.1, role TBD).

## 5. Findings

Raised as issues labelled `qa-finding`; summarised to the gate review (WP-M-02 §10).

## 6. Relationship to the confirmation measures

QA audits are I1 at best; the functional safety audits AUD-1 and AUD-2 of WP-M-06 are I3 and external.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
