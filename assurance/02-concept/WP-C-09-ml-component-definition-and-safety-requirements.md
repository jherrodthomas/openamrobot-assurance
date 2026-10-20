# WP-C-09 ML component definition and safety requirements

| Field | Value |
|---|---|
| Work product | WP-C-09 ML component definition and safety requirements (learned policy, perception models) |
| Standard reference | Other: TR 5469 §6–§8 (classes, usage levels, properties); AI Act Annex IV; ASPICE: MLE.1 |
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

Defines the learned components in or planned for the stack (perception models, a navigation or manipulation policy), classifies each under ISO/IEC TR 5469 (AI technology class, usage level) and states the requirements that keep them outside every safety function.

## 2. Inventory of learned components

What exists in the inherited repositories (to be surveyed: `openamrobot-embodied-ai`, perception packages) and what upstream plans.

## 3. Classification

Per component: technology class, usage level, the independent safeguard (the chain) and why it is sufficient.

## 4. Position

No safety function is allocated to a learned component. If a learned output were ever to trigger a safety function, WP-M-13 §5 applies and this document is rewritten.

## 5. Requirements

AIR-nn: bounded outputs, pass-through of the command arbiter, runtime monitoring, version pinning, data provenance; the insufficiencies of WP-C-10 that learned perception adds.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
