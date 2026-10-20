# WP-M-04 Organization-specific rules, safety culture, competence management

| Field | Value |
|---|---|
| Work product | WP-M-04 Organization-specific rules, safety culture, competence management |
| Standard reference | SRP/CS: 61508-1 §6.2 (competence); 13849-1 §4; IEC 62443: 62443-4-1 SM-4 |
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

Organisation-specific rules for safety: safety culture, competence requirements and evidence per role, and the rules under which a single-maintainer open-source project can still claim independence where the standards require it.

## 2. Safety culture

Rules: no claim without evidence; defeaters are published; the lead holds every risk acceptance; a stop is never argued away after the fact. Upstream's two-human approval on safety paths is adopted for the fork's safety-relevant paths ([`safety-relevant-paths.txt`](../07-supporting/safety-relevant-paths.txt)).

## 3. Roles and independence

By reference to WP-M-02 §3.1 and WP-M-06 §3. One person may hold several authoring roles; nobody reviews their own work at I1 or above.

## 4. Competence requirements matrix

Per role: machinery risk assessment (ISO 12100, ISO 3691-4), SRP/CS design and PL calculation (ISO 13849-1/-2, SISTEMA), electrical (EN 60204-1), embedded C and MISRA, ROS 2 and Nav2, IEC 62443, ML evaluation; level required and how it is shown.

## 5. Competence evidence record template

Name, role, evidence (training, experience, prior assessments), gaps, plan; one record per person, kept outside the repository where it holds personal data.

## 6. Training plan

What the test operators must know before WP-V-07 lets them drive: the stop chain, the limits of §3, the anomaly rule.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
| OI-2 | Decide whether a legal entity is needed before the first contract with an assessor or a notified body | PM | G1 |
