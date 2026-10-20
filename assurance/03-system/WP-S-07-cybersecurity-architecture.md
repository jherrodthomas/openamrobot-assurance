# WP-S-07 Cybersecurity architecture

| Field | Value |
|---|---|
| Work product | WP-S-07 Cybersecurity architecture (zones, conduits, controls) |
| Standard reference | IEC 62443: 62443-4-1 SD-1…SD-4; 62443-3-3 §5; ASPICE: SEC.1, SYS.3 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G2** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

The cybersecurity architecture (IEC 62443-4-1 SD, 62443-3-3 zones and conduits): which zones exist on the robot, which conduits connect them, which controls sit on each conduit, and how the safety chain is kept out of reach of the network.

## 2. Zones and conduits

Safety chain; firmware and serial link; ROS 2 graph on the Pi; operator UI; update path; site network (external). The safety chain is a zone of its own with no conduit from the ROS 2 network.

## 3. Controls per conduit

SROS2 enclaves and permissions, UI authentication, a twist_mux with an authenticated stop input, signed images, pinned containers, no host networking in production.

## 4. Defence in depth and the safety argument

How the controls protect SF-nn; what remains for the chain if every control fails.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G2 |
