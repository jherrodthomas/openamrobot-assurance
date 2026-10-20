# WP-A-05 Independence of the safety chain from the functional stack

| Field | Value |
|---|---|
| Work product | WP-A-05 Independence of the safety chain from the functional stack (freedom from interference) |
| Standard reference | SRP/CS: 13849-1 §6, §7; 61508-3 Annex F; IEC 62443: 62443-3-3 §5 (zoning) |
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

Analysis of the independence of the safety chain from the functional layers: every shared resource (power, chassis, wiring, operator, parameters, network) and every path by which a fault or an attack in the stack could prevent the chain from acting; the argument that none exists, or the measure that closes it.

## 2. Shared resources

Logic power from the Pi (GAP-21), the 24 V bus, the enclosure, the pendant, the firmware's diagnostic inputs.

## 3. Interference paths

Firmware holding PWM after a chain trip (cannot: power removed upstream), parameter injection (GAP-07), lifecycle services (GAP-27), the docking sequencer (GAP-15), the UI E-stop (GAP-28).

## 4. Argument

Per path: closed by design, by a measure, or open as a defeater.

## 5. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G2 |
