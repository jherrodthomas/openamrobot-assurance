# WP-W-08 Software validation on the target

| Field | Value |
|---|---|
| Work product | WP-W-08 Software validation on the target (firmware bench, hardware-in-the-loop) |
| Standard reference | SRP/CS: 13849-1 §10; 61508-3 §7.7; ASPICE: SWE.6 |
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

Validation of the software on the target: the firmware bench (Teensy, drivers, encoders, a chain simulator) and the hardware-in-the-loop rig, with the tests that show the hardened behaviour on real hardware before the robot moves.

## 2. Bench

Design, owner (WP-M-02 §3.1), what it can and cannot inject.

## 3. Test specification

VS-SW-nn: watchdog timeout, agent loss, driver fault, stale and NaN commands, debug topics, reset cause.

## 4. Report

Results per build.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G4 |
