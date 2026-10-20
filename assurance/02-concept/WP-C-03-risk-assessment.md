# WP-C-03 Hazard identification and risk assessment

| Field | Value |
|---|---|
| Work product | WP-C-03 Hazard identification and risk assessment (hazard list, risk estimation and evaluation) |
| Standard reference | Machinery: 12100 §5.4–§5.6; 3691-4 Annex A; 10218-2 Annex A; SRP/CS: 13849-1 Annex A (risk graph inputs); Other: Machinery Reg. Annex III §1 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G1** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

Identifies the hazards of the machine within its limits and estimates and evaluates the risk of each (ISO 12100 §5.4–§5.6), using the ISO 3691-4 Annex A list of significant hazards for driverless trucks as the checklist and the ISO 13849-1 Annex A risk graph as the input to the required PL. It is the one hazard log of the project.

## 2. Method

Hazard identification per life phase and zone; risk estimation by severity, frequency and possibility of avoidance (the ISO 13849-1 risk graph parameters S, F, P); evaluation against the three-step method; one row per hazard H-nn, never reused.

## 3. Hazard list

Seeded from the gap assessment: crushing and impact by the moving base (no protective stop, GAP-14, GAP-22), run-over below the scan plane, blind reverse (GAP-35), docking contact (GAP-15), loss of control on driver fault (GAP-04), runaway on parameter injection (GAP-07), electrical fire and shock (GAP-19, GAP-20), tip-over (GAP-23), unexpected restart, remote command (GAP-27).

## 4. Risk estimation and required PL per hazard

S, F, P and the resulting PLr for the safety function that mitigates it; feeds WP-C-04.

## 5. Hazard log cross-references

Cyber-induced hazards are analysed in WP-C-07 and rated here; performance limits of sensing from WP-C-10 appear as hazards with their triggering conditions; misuse from WP-C-06.

## 6. Residual risk

Per hazard after the measures of WP-C-05; what remains for information for use.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
