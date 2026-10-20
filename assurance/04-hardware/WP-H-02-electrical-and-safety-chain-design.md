# WP-H-02 Electrical and safety-chain design

| Field | Value |
|---|---|
| Work product | WP-H-02 Electrical and safety-chain design (schematics, wiring, enclosure) |
| Standard reference | SRP/CS: 13849-1 §6; IEC 62443: 62443-4-2 CR 2.13 (physical); Other: 60204-1 §5–§13; ASPICE: HWE.2 |
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

The electrical and safety-chain design: schematics, wiring diagrams, panel layout, the bench chain of WP-V-07 as its first version and the 2.0 chain as its target, under EN 60204-1.

## 2. Power distribution

Battery, fuse, disconnect, contactors, driver supply, logic supply independent of compute (GAP-21), charger and source selection (GAP-20).

## 3. Safety chain schematic

E-stop circuits, scanner OSSDs, relay, contactors, reset, lamp, brake release; diagnostic signals to the firmware. Diagnostic signals from the chain to the firmware are informative only.

## 4. Wiring and installation

Wire gauges, colours, connectors, routing, strain relief, labelling; enclosure and IP rating.

## 5. Bill of materials

Every safety component with manufacturer, part number and certificate reference (WP-H-07); closes GAP-25 for the chain.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
