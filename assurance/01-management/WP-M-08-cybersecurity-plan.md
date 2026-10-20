# WP-M-08 Cybersecurity plan

| Field | Value |
|---|---|
| Work product | WP-M-08 Cybersecurity plan |
| Standard reference | IEC 62443: 62443-4-1 §5 (SM-1…SM-13); 62443-4-2 §4; ASPICE: MAN.7 (CS) |
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

How cybersecurity is managed for the fork under IEC 62443-4-1 (secure product development lifecycle) and 62443-4-2 (component requirements), and how it interfaces with safety. The robot is treated as one component with a security level target decided by the lead (DQ-013).

## 2. Scope and security context

The three platform repositories, the robot's ROS 2 graph, the operator UI (Flask, rosbridge, video server), the micro-ROS serial link, the update path. The site network and the operator's computer are external zones (WP-M-01 T-11).

## 3. Practices of IEC 62443-4-1 and where each lands

SM (management) here and WP-M-04/M-05; SR (requirements) WP-C-07, WP-C-08; SD (design) WP-S-07; SI (implementation) WP-W-01, WP-W-05, WP-W-11; SVV (verification) WP-W-11, WP-V-06; DM (defect management) WP-P-03, WP-O-05; SUM (updates) WP-P-10, WP-O-05; SG (guidelines) WP-S-06, WP-O-02.

## 4. Interface to safety

Threat scenarios that can cause a hazard are rated against the hazard list (WP-C-07 ↔ WP-C-03); the safety chain is a zone with no network conduit (WP-S-07 ↔ WP-S-03); safety parameters are protected assets (WP-W-09 ↔ WP-W-11).

## 5. Roles

| Role | Holder (today) | Duty |
|---|---|---|
| Cybersecurity manager | Jherrod Thomas (acting); permanent holder TBD | Owns this plan, the TRA and the security level target |
| External cybersecurity assessor | TBD | CS-I1 at G1, CS-A1 at G5 (WP-M-06 §7) |

## 6. Known starting position

GAP-27 (anyone on ROS domain 0 can move the robot), GAP-28 (the on-screen E-stop is a network request), GAP-29 (unpinned supply chain). SROS2, a twist_mux with an authenticated stop input and pinned builds are the first three measures.

## 7. Schedule

By gate, aligned with WP-M-06 §9.

## 8. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
