# WP-C-10 Functional insufficiency analysis of sensing and navigation

| Field | Value |
|---|---|
| Work product | WP-C-10 Functional insufficiency analysis of sensing and navigation (performance limits, triggering conditions) |
| Standard reference | Machinery: 3691-4 §4 (personnel detection limits); 12100 §5.4; Other: ISO 21448 §6–§7 (informative method); IEC 62998-1 |
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

Analyses the performance limits of the sensing and navigation stack that cause hazardous behaviour without any fault, using ISO 21448's method as an informative frame (triggering conditions, functional insufficiencies, known and unknown scenarios). Each limit is closed by a safety function, an operating-environment limit, or stays as an open defeater.

## 2. Functional insufficiencies

FI-nn seeded from the gap assessment: nothing below the scan plane (GAP-14), rear sector masked (GAP-35), returns inside 0.15 m ignored and a 1 s stale-scan tolerance (GAP-16), open-loop smoother (GAP-13), LiDAR dropouts, glass and dark surfaces, docking blind advance (GAP-15), under-voltage path deviation (GAP-17).

## 3. Triggering conditions

TC-nn per insufficiency: a child or a seated person, a pallet foot, a doorway, sunlight through glass, a low battery.

## 4. Detection means and the claim SF-02 can make

Blind zones below the scan plane bound the claim SF-02 can make with the LiDAR alone; the options (type 3 safety scanner at a low plane, bumpers, a separated area) are decision DQ-009.

## 5. Known and unknown scenarios

Known ones go to WP-V-03 and WP-V-05 as tests; the unknown residual is the subject of WP-V-08 field trials.

## 6. Closure table

FI/TC → safety function, operating-environment limit, or open defeater DF-nn.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
| OI-2 | Decide the detection means (decision DQ-009); until then IX-02 stays open and SF-02 has no implementation | SM | G1 |
