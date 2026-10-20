# WP-W-03 Software architectural design

| Field | Value |
|---|---|
| Work product | WP-W-03 Software architectural design (firmware safety layer, separation from the ROS 2 stack) |
| Standard reference | SRP/CS: 13849-1 §7; 61508-3 §7.4.3; IEC 62443: 62443-4-1 SD-2; ASPICE: SWE.2 |
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

The software architecture: the firmware safety layer and its separation from the rest of the firmware, the ROS 2 command chain with its arbiter, and the interfaces between them and the chain. The I/O semantics of WP-S-05 are the firmware's contract with the safety chain.

## 2. Firmware architecture

Command validation → watchdog → clamps → PWM; fault inputs; brake output; status publication; the linorobot2 base as an overlaid library (vendored, pinned).

## 3. ROS 2 chain architecture

Nav2 → smoother → collision monitor → twist_mux ← docking, teleop, UI; lifecycle management; what may publish where.

## 4. Separation

What runs on the Teensy, what on the Pi, what in hardware; shared resources and how WP-A-05 analyses them.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
