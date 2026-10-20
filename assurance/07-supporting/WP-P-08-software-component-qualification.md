# WP-P-08 Qualification of software components

| Field | Value |
|---|---|
| Work product | WP-P-08 Qualification of software components (ROS 2, Nav2, micro-ROS, linorobot2, third-party) |
| Standard reference | SRP/CS: 61508-3 §7.4.2.12; IEC 62443: 62443-4-1 SM-9, SM-10 |
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

Qualification of pre-existing software components the functional layers use: ROS 2 Jazzy, Nav2, micro-ROS, the linorobot2 firmware base, rosbridge, the drivers; what each is relied on for, its known defects, and why none is inside the SRP/CS.

## 2. Component list

Per component: version pinned, role, interfaces, known issues, update policy.

## 3. Argument

Functional use only (WP-M-01 T-03, T-05); what would change if any were promoted into the chain.

## 4. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
