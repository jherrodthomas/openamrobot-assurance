# WP-H-04 Reliability data and PL calculation

| Field | Value |
|---|---|
| Work product | WP-H-04 Reliability data and PL calculation (MTTFD, DCavg, CCF, SISTEMA) |
| Standard reference | SRP/CS: 13849-1 §6, Annex C–F, Annex K |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G3** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

The reliability data and the PL calculation for each safety function (ISO 13849-1 §6 and Annexes C–F): MTTFD per channel from B10D and component data, DCavg from the diagnostics of WP-H-03, the CCF score, the category, and the achieved PL, with the SISTEMA project as the record.

## 2. Input data

Per component: B10D or MTTFD, source (manufacturer, Annex C tables, well-tried), nop per year for the E-stop and contactors.

## 3. Calculation per safety function

Channels, MTTFD per channel, DCavg, CCF ≥ 65, category, resulting PL; margin to PLr.

## 4. SISTEMA project

File reference and version; the calculation is reproducible from it.

## 5. Mission time and proof tests

20 years or the replacement interval; T10D of wearing components.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
