# WP-P-04 Documentation management

| Field | Value |
|---|---|
| Work product | WP-P-04 Documentation management |
| Standard reference | Machinery: 12100 §7; SRP/CS: 13849-1 §12; IEC 62443: 62443-4-1 SG-1; Other: Machinery Reg. Annex IV; ASPICE: SUP.7 |
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

Documentation management: the document-control header, versions and status, where each kind of document lives, generated documents and their checks, the technical documentation of the Machinery Regulation, retention (ten years after the last unit), and controlled copies.

## 2. Rules

Header per the assurance README; status meanings; generated files never edited by hand; relative links checked by `check_links.py`; tables by `check_tables.py`.

## 3. Technical documentation

Assembled by WP-K-02 from WP-M-00; retention and availability to authorities.

## 4. Controlled copies and snapshots

A snapshot workflow that publishes the safety case as a PDF at a named baseline with a manifest of hashes, and a controlled-copy workflow that issues a numbered copy to a named recipient and records it.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
