# WP-C-07 Cybersecurity threat and risk assessment

| Field | Value |
|---|---|
| Work product | WP-C-07 Cybersecurity threat and risk assessment |
| Standard reference | IEC 62443: 62443-4-1 SR-2; 62443-3-2 §5; ASPICE: SEC.1 |
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

Threat and risk assessment of the robot under IEC 62443-4-1 SR-2 and 62443-3-2: assets, zones and conduits, threat scenarios TS-nn, attack paths, likelihood and impact, with the safety impact rated against the hazard list.

## 2. Assets and zones

ROS 2 graph (domain 0, multicast discovery), operator UI ports 5050, 9090, 8080, micro-ROS serial, firmware image, Nav2 parameters, docking triggers, update path, Wi-Fi.

## 3. Threat scenarios

Seeded from GAP-27, GAP-28, GAP-29 and GAP-07: unauthenticated `/cmd_vel`, `/dock_trigger`, `/undock_robot`, `/debug/tune`, `/debug/enc_cal`, the lifecycle service that deactivates the collision monitor, the UI's software E-stop, unpinned images and workflows.

## 4. Risk rating

Likelihood and impact per scenario; Safety impact is anchored to the hazard list of WP-C-03 (the hazard each scenario can cause).

## 5. Treatment

Security level target (WP-C-08), requirements CSR-nn, residual risk accepted by the lead (DQ-013).

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
