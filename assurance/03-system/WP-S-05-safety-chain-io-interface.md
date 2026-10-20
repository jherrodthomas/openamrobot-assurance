# WP-S-05 Hardware-software interface of the safety chain

| Field | Value |
|---|---|
| Work product | WP-S-05 Hardware-software interface of the safety chain (I/O map, signal semantics) |
| Standard reference | SRP/CS: 13849-1 §6, §7; ASPICE: SYS.3 |
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

The hardware-software interface of the safety chain: every signal between the chain, the firmware and the ROS 2 stack, with direction, electrical form, semantics, timing and behaviour on loss. The firmware's contract with the chain.

## 2. I/O map

Signal, source, sink, form (NC contact, OSSD, 24 V input, open collector), active level, debounce, timeout.

## 3. Semantics

What each signal means and what the receiver must do; which signals are informative only (diagnostics to the firmware) and which are safety inputs to the relay.

## 4. Gate A pin assignments

Teensy pins for `ERR/DO1` read-back, brake output, chain state; the existing pin map of the gap assessment §3.1 as the starting point.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G2 |
