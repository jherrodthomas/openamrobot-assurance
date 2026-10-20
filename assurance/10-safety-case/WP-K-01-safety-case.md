# WP-K-01 Safety case

| Field | Value |
|---|---|
| Work product | WP-K-01 Safety case (claims, arguments, evidence, defeaters) |
| Standard reference | SRP/CS: 61508-1 §8 (assessment input); Other: UL 4600; Machinery Reg. Annex IV |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G1→G5 (living)** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

The safety case: the top-level claim of WP-M-01 §3.2, the sub-claims G1…G6, the argument under each, the evidence items with their review state, the assumptions, and the defeaters, seeded with GAP-01…GAP-40. Structured on UL 4600 principles; the machine-readable records and the generated dashboard are planned under `case/`.

## 2. Claim structure

G0 and G1…G6 as in WP-M-01 §3.2; the argument per sub-claim to be drawn as GSN from records.

## 3. Assumptions

AOU-nn on the operating environment, the operator, the docking station, the site network.

## 4. Evidence status

Per claim: evidence items recorded, accepted (none until a confirmation review accepts one).

## 5. Defeaters

DF-nn: GAP-01…GAP-40 registered as the first defeaters against G1…G6; each with the work product that closes it.

## 6. Cybersecurity branch

The cybersecurity branch of the argument is WP-K-03; claims that protect a safety function are referenced from here.

## 7. Baselines and reviews

Named states of the record and the confirmation reviews recorded against them.

## 8. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
