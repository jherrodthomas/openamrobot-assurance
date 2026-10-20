# WP-M-11 Impact analysis of the inherited OpenAMRobot baseline

| Field | Value |
|---|---|
| Work product | WP-M-11 Impact analysis of the inherited OpenAMRobot baseline (modification of existing machinery) |
| Standard reference | Machinery: 12100 §4; SRP/CS: 61508-1 §7.16 (modification); IEC 62443: 62443-4-1 SM-3; Other: Machinery Reg. Art. 3 (substantial modification); ASPICE: SUP.10 |
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

Impact analysis of using the inherited OpenAMRobot baseline as the starting point of a machine that is to carry a safety case: what is reused, what is reworked, what is discarded, and what each inherited element's state means for the lifecycle entry (WP-M-01 T-01).

## 2. Baseline

The commits of the gap assessment header; every finding GAP-01…GAP-40 is an input.

## 3. Reuse classification per element

Per repository and element: reuse unchanged (functional only), reuse with hardening (firmware, Nav2 chain), replace (stop chain hardware), new (every safety work product). With the rationale and the gaps it inherits.

## 4. Consequences for the lifecycle

Full concept phase; no inherited safety work product; the firmware is hardened as defence in depth; the chain is new hardware.

## 5. Change impact analysis records

Later changes are analysed per change under [`07-supporting/impact/`](../07-supporting/impact/README.md); this document covers only the entry.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
