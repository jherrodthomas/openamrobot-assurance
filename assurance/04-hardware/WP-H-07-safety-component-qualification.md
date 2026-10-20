# WP-H-07 Qualification of safety components

| Field | Value |
|---|---|
| Work product | WP-H-07 Qualification of safety components (safety relay, contactors, scanner, brakes, well-tried components) |
| Standard reference | SRP/CS: 13849-1 §6 (well-tried components); 13849-2 Annex A–D; 62061 §7 (subsystems); Other: IEC 61496-1/-3 (ESPE) |
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

Qualification of the safety components the chain uses: certificates and declarations of conformity, reliability data, the fault exclusions the manufacturer allows, and the well-tried component arguments (ISO 13849-1, 13849-2) for the parts without certificates.

## 2. Certified components

Safety relay (upstream names a Pilz PNOZ s3), E-stop devices (Schneider XB4BS8445 with ZBE-102), contactors (Gigavac GX11CAC), safety scanner (type 3 per IEC 61496-3, to be selected in DQ-008), brakes.

## 3. Well-tried components

Which parts are argued as well-tried under ISO 13849-2 and on what basis.

## 4. Not safety-related

Motor drivers, motors, encoders, LiDAR A1/S3, compute: why the chain removes the need to qualify them.

## 5. Evidence index

Per component: document, version, where stored.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
