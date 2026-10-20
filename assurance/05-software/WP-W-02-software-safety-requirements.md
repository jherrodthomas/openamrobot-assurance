# WP-W-02 Software safety requirements specification

| Field | Value |
|---|---|
| Work product | WP-W-02 Software safety requirements specification (SRESW, SRASW) |
| Standard reference | SRP/CS: 13849-1 §7; 61508-3 §7.2; ASPICE: SWE.1 |
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

Software safety requirements for the firmware (SRESW) and the ROS 2 chain (SRASW) derived from WP-S-02's requirements on the functional layers: SWSR-nn that make the software unable to defeat the chain and reduce demand on it.

## 2. Firmware requirements

Hardware watchdog (GAP-03), `/cmd_vel` finite, bounded and fresh (GAP-06), driver fault read-back stops both motors (GAP-04), encoder and stall plausibility (GAP-05), debug paths off or armed with bounded parameters (GAP-07, GAP-08), version, reset cause and calibration flag published (GAP-09, GAP-10), brake output on every stop.

## 3. ROS 2 chain requirements

twist_mux with the stop at highest priority (GAP-36), docking inside the envelope and a lost tag is a halt (GAP-15), undock only when docked and with a rear check (GAP-35), bounded speed parameters, collision monitor cannot be deactivated from the network (GAP-27).

## 4. Traceability

To WP-S-02 and the hazards; verified by WP-W-06…W-08.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
