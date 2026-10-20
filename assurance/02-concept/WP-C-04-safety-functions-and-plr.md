# WP-C-04 Safety functions specification with required Performance Level, stop category and response time

| Field | Value |
|---|---|
| Work product | WP-C-04 Safety functions specification with required Performance Level, stop category and response time |
| Standard reference | Machinery: 3691-4 §4; 13850 §4; SRP/CS: 13849-1 §5, Annex A (PLr); Other: 60204-1 §9.2 (stop categories); ASPICE: SYS.2 |
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

Specifies the safety functions of the machine (ISO 13849-1 §5): for each, the triggering condition, the safe state, the response time, the stop category (EN 60204-1 §9.2), the required Performance Level from the risk graph, and the operating modes it applies in. SF-nn IDs are never reused.

## 2. Safety functions

SF-01 emergency stop (ISO 13850; stop category decided in DQ-014); SF-02 protective stop on personnel detection (ISO 3691-4 §4); SF-03 safely limited speed in shared zones; SF-04 stop on loss of control (agent, driver fault, watchdog); SF-05 safe brake holding on slopes; SF-06 prevention of unexpected restart; further functions from WP-C-03.

## 3. Required Performance Level

PLr per function from WP-C-03's S, F, P; the planning assumption is PL d for SF-01 and SF-02 (DQ-005).

## 4. Allocation

Every safety function is allocated to the hardwired safety chain (WP-M-01 T-03; DQ-013). The firmware and the ROS 2 stack are functional layers; learned components are outside every safety function.

## 5. Detection means for SF-02

The detection means of SF-02 is settled in WP-C-10 and decision DQ-009: safety laser scanner, bumpers, or a separated area. Until then SF-02 has a PLr and no implementation.

## 6. Response time and stop category per function

Placeholders until WP-S-04 budgets them and WP-V-02 measures the stopping distance.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
| OI-2 | Set the stop category of SF-01 (decision DQ-014) | SM | G1 |
