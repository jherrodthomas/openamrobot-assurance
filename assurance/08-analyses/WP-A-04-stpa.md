# WP-A-04 System-theoretic process analysis

| Field | Value |
|---|---|
| Work product | WP-A-04 System-theoretic process analysis (STPA) of the motion control chain |
| Standard reference | Machinery: 12100 §5.4; Other: STPA Handbook 2018 |
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

System-theoretic process analysis of the motion control chain: the control structure from the operator and Nav2 through the arbiter, the firmware and the chain to the wheels; unsafe control actions and loss scenarios, especially those the FMEA cannot see (mode confusion, docking, parameter injection).

## 2. Control structure

Controllers, actuators, sensors, feedback; the docking sequencer as a controller that disables a safeguard (GAP-15).

## 3. Unsafe control actions

UCA-nn per controller and command.

## 4. Loss scenarios and requirements

Scenarios → requirements for WP-S-02 and WP-W-02.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G2 |
