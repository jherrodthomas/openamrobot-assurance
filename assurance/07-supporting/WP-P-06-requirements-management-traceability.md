# WP-P-06 Requirements management and traceability procedure

| Field | Value |
|---|---|
| Work product | WP-P-06 Requirements management and traceability procedure |
| Standard reference | SRP/CS: 13849-1 §5; 61508-3 §7.2; IEC 62443: 62443-4-1 SR-5; ASPICE: SYS.2, SWE.1 |
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

Requirements management and traceability: identifiers, attributes, the trace levels hazard → safety function → SRS → HWSR/SWSR → test, the machine-readable data in `trace/` and the consistency checks CI runs.

## 2. Identifiers and attributes

H-, SF-, SR-, HWSR-, SWSR-, CSR-, AIR-, PAR-, VS-; status, source, verification.

## 3. Trace levels and completeness rules

Every hazard has a safety function or a limit; every safety function has SRS rows; every SRS row has a test.

## 4. Tooling

To be ported from LionDriver's `trace/tools/`.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
