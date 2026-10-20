# WP-C-08 Cybersecurity requirements and security level target

| Field | Value |
|---|---|
| Work product | WP-C-08 Cybersecurity requirements and security level target |
| Standard reference | IEC 62443: 62443-4-1 SR-3…SR-5; 62443-4-2 CR 1–7, SL-T; ASPICE: SEC.1 |
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

Cybersecurity requirements for the robot as one IEC 62443-4-2 component: the security level target per foundational requirement (FR 1–7), the component requirements CR that follow, and the requirements CSR-nn allocated to the ROS 2 stack, the firmware, the UI and the update path.

## 2. Security level target

Decided by the lead on 2026-10-20 (DQ-013 A). The realistic threat is a person on the same Wi-Fi with public
tools, so the foundational requirements that stop such a person moving the robot or changing what it does get
SL 2; the rest get SL 1. The safety chain is designed to need neither: no attack on the software can hold a
contactor closed (WP-S-03 §1). Rationale per threat scenario in WP-C-07.

| FR | Foundational requirement | SL-T | Why |
|---|---|---|---|
| FR 1 | Identification and authentication control | **2** | Who may publish `/cmd_vel`, call lifecycle services or log into the operator UI |
| FR 2 | Use control | 1 | No personal data; roles are operator and maintainer only |
| FR 3 | System integrity | **2** | Signed images, protected safety parameters, a reproducible firmware build |
| FR 4 | Data confidentiality | 1 | Nothing confidential on the robot |
| FR 5 | Restricted data flow | **2** | Zones and conduits: the safety chain has no conduit from the ROS 2 network |
| FR 6 | Timely response to events | 1 | Logging and the field-monitoring route of WP-O-04 |
| FR 7 | Resource availability | **2** | The stop path does not depend on the network; denial of service must not block a stop |

## 3. Component requirements

CR 1.1 identification and authentication (SROS2 enclaves, UI login), CR 2.1 authorisation (who may publish `/cmd_vel`, call lifecycle services), CR 3.1/3.4 integrity (signed images, protected parameters), CR 5.1 network segmentation (safety chain has no conduit), CR 7.1 denial of service (the stop path does not depend on the network).

## 4. Allocated requirements

CSR-nn with the component that implements each and the verification in WP-W-11 or WP-V-06.

## 5. Interface to the safety functions

Which CSRs protect which SF-nn of WP-C-04; the cybersecurity goals that protect safety are traced both ways.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
