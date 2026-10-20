# WP-W-05 Software unit design and implementation

| Field | Value |
|---|---|
| Work product | WP-W-05 Software unit design and implementation |
| Standard reference | SRP/CS: 13849-1 §7; 61508-3 §7.4.5, §7.4.6; IEC 62443: 62443-4-1 SI-1; ASPICE: SWE.3 |
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

Unit design and implementation of the hardened firmware and the changed ROS 2 nodes: design notes per unit, state machines, the coding-guideline deviations, and the mapping from requirements to units.

## 2. Units

Per unit: purpose, interfaces, state machine, requirements implemented, design note reference.

## 3. State machines

Firmware stop states; docking sequencer states with the monitor active in every motion state.

## 4. Deviations

DEV-nn against the coding guidelines of WP-W-01.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
