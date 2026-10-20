# WP-S-03 Safety-related control system architecture

| Field | Value |
|---|---|
| Work product | WP-S-03 Safety-related control system architecture (designated architectures, categories, channels, diagnostics) |
| Standard reference | SRP/CS: 13849-1 §6; Other: 60204-1 §9.4; ASPICE: SYS.3 |
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

The architecture of the safety-related control system (ISO 13849-1 §6): the designated architecture per safety function, the channels, the input, logic and output subsystems, the diagnostic measures and their coverage, the reset and the interfaces to the functional layers.

## 2. Architecture per safety function

SF-01: two-channel E-stop inputs → safety relay (Category 3 or 4 logic) → two contactors with mirror contacts in the reset loop → drivers de-energised and brakes engaged. SF-02: scanner OSSD pair → the same relay. SF-04: firmware fault/agent-loss output as a diagnostic input, not a channel.

## 3. Diagnostics

Cross-monitoring in the relay, mirror contact monitoring of the contactors, scanner self-test, feedback of brake state; DC estimate per block feeding WP-H-04.

## 4. Independence from the functional layers

Power, wiring and signal paths such that no input of the safety chain is reachable from the network or from the Raspberry Pi; detailed in WP-A-05.

## 5. Interfaces

To the firmware (diagnostic status, brake command for functional stops), to the operator (pendant, reset, lamp), to WP-S-05 for the I/O map.

## 6. Upstream 2.0 chain as a claim

Upstream's `SAFETY-PROCUREMENT`, `ESTOP-SCOPE` and `SAFETY-CHAIN-IO` decisions mapped onto this architecture, each marked as not yet in any repository (GAP-33).

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G2 |
