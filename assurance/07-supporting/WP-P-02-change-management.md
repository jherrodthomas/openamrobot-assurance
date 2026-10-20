# WP-P-02 Change management plan

| Field | Value |
|---|---|
| Work product | WP-P-02 Change management plan |
| Standard reference | SRP/CS: 61508-1 §7.16; IEC 62443: 62443-4-1 SM-3; ASPICE: SUP.10 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G0** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

Change management: how a change to a configuration item is requested, classified, impact-analysed, approved, implemented, verified and recorded, and how a change to a confirmed work product re-opens its confirmation.

## 2. Change classes

By the safety-relevant file list class and by whether a work product is touched.

## 3. Procedure

Request (issue) → classification → impact analysis (WP-M-11 format, record under [`impact/`](impact/README.md)) → change board (safety manager, CM manager) → pull request → verification → record.

## 4. Re-confirmation

WP-M-06 §4.2 step 6.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
