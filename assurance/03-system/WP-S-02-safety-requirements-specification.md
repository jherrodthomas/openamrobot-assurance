# WP-S-02 Safety requirements specification for the SRP/CS

| Field | Value |
|---|---|
| Work product | WP-S-02 Safety requirements specification for the SRP/CS |
| Standard reference | Machinery: 3691-4 §4; SRP/CS: 13849-1 §5; 62061 §6; Other: 60204-1 §9; ASPICE: SYS.2 |
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

The safety requirements specification for the safety-related parts of the control system (ISO 13849-1 §5): for every safety function of WP-C-04, the detailed requirements SR-nn on inputs, logic, outputs, response time, behaviour on fault, reset and diagnostics that the chain must meet.

## 2. Requirements per safety function

SR-nn grouped by SF-nn; each with PLr inherited, category target, response time, safe state, restart conditions, diagnostic requirements.

## 3. Stop categories and E-stop requirements

EN 60204-1 §9.2 category 0 or 1 per function (DQ-014); ISO 13850 requirements on the devices, latching and reset.

## 4. Requirements on the functional layers

What the firmware and the ROS 2 stack must do so that they never defeat the chain (feeds WP-W-02); these are not safety requirements with a PL.

## 5. Traceability

To WP-C-03 hazards, WP-C-04 functions, WP-S-03 architecture elements, WP-V-01 tests; held in `trace/`.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G2 |
