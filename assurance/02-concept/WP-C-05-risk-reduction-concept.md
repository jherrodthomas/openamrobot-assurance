# WP-C-05 Risk reduction concept

| Field | Value |
|---|---|
| Work product | WP-C-05 Risk reduction concept (three-step method: inherently safe design, safeguarding, information for use) |
| Standard reference | Machinery: 12100 §6; 3691-4 §4; 10218-2 §5; SRP/CS: 13849-1 §5; Other: Machinery Reg. Annex III §1.1.2; ASPICE: SYS.2 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G1** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

Allocates the risk reduction for every hazard of WP-C-03 to the three steps of ISO 12100 §6, in order: inherently safe design, safeguarding and complementary protective measures, information for use. It is the concept-level argument that the safety functions of WP-C-04 and the limits of WP-C-02 together make the residual risk acceptable.

## 2. Inherently safe design measures

Speed and mass limits, brakes that engage on power loss, no live parts accessible, the chain upstream of every actuator, command arbitration with the stop at highest priority.

## 3. Safeguarding and complementary protective measures

The safety chain, the detection means, the E-stop devices, the disconnect and fuse, the restart interlock.

## 4. Information for use

What remains for the user: zones, speeds, battery rule, docking lane. Feeds WP-O-03. The gap assessment's principle applies: a limitation that is only documented is not a control for a hazard that can kill.

## 5. Allocation table

Hazard H-nn → measures per step → residual risk → safety function or limit → verification reference.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
