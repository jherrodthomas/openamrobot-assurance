# WP-W-09 Safety-related parameters and configuration data

| Field | Value |
|---|---|
| Work product | WP-W-09 Safety-related parameters and configuration data (speed limits, protective fields, control gains, Nav2 limits) |
| Standard reference | Machinery: 3691-4 §4 (speed); SRP/CS: 13849-1 §7 (parameterization); IEC 62443: 62443-4-2 CR 3.4; ASPICE: SWE.3 |
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

Safety-related parameters and configuration data: speed and acceleration limits, protective field sets, timeouts, control gains, the encoder calibration table, Nav2 parameters, with their source, allowed range, verification and protection against unauthorised change (ISO 13849-1 §7 parameterisation).

## 2. Parameter register

PAR-nn: value, unit, source (WP-S-04 budget, measurement), range, where it lives, who may change it, how it is verified after loading.

## 3. Integrity

Parameter integrity is a cybersecurity requirement verified in WP-W-11: signed parameter sets, read-back, no runtime injection without arming (GAP-07).

## 4. Simulation and real robot

One parameter file per configuration; the mismatches of GAP-40 resolved.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
