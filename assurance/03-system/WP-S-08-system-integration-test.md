# WP-S-08 System integration and test strategy, specification and report

| Field | Value |
|---|---|
| Work product | WP-S-08 System integration and test strategy, specification and report |
| Standard reference | SRP/CS: 13849-1 §8; IEC 62443: 62443-4-1 SVV-1; ASPICE: SYS.4 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G4** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

Strategy, specification and report for integrating the chain, the firmware and the ROS 2 stack on the robot and testing the integrated system before PL verification.

## 2. Integration strategy

Order: chain alone on the bench, chain with firmware, full stack; entry and exit criteria per step.

## 3. Test specification

IT-nn cases: stop paths, restart, mode changes, agent loss, driver fault, parameter load.

## 4. Report

Results per case, anomalies, deviations.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G4 |
