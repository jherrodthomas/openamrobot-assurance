# WP-S-04 Response time, stopping performance and safety distance budget

| Field | Value |
|---|---|
| Work product | WP-S-04 Response time, stopping performance and safety distance budget |
| Standard reference | Machinery: 3691-4 §4 (braking, speed); SRP/CS: 13849-1 §5 (response time); Other: ISO 13855 §6; ASPICE: SYS.3 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G2** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

The timing and distance budget every safety function depends on: detection time, chain response time, driver and brake response, deceleration, stopping distance per speed, and the resulting safety distances and protective field sizes (ISO 13855) and speed limits per zone.

## 2. Response time budget per safety function

Sensor, relay, contactor drop-out, brake engagement; measured and datasheet values.

## 3. Stopping distance model

Speed, mass, deceleration, floor; the model is validated by WP-V-02. The deceleration the budget assumes is bounded by the tip-over margin of WP-H-08.

## 4. Safety distances and protective fields

ISO 13855 formula with the approach speed of WP-C-06, per zone and per speed; the field set WP-W-09 configures and WP-V-03 validates.

## 5. Speed limits per zone

Derived from the above; replaces the development limits of WP-V-07 §3.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G2 |
