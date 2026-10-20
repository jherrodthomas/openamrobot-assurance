# WP-P-01 Configuration management plan

| Field | Value |
|---|---|
| Work product | WP-P-01 Configuration management plan (safety-relevant file list, baselines across the fork repositories) |
| Standard reference | SRP/CS: 61508-1 §6.2.3; 13849-1 §12; IEC 62443: 62443-4-1 SM-6, SM-7; ASPICE: SUP.8 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G0** ([WP-M-00](../01-management/WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

Configuration management for the fork: the configuration items across this repository and the three forked platform repositories, the safety-relevant file list, baselines and tags, pins and how they move, and the branch rules.

## 2. Configuration items

This repository; `openamr-platform-sw`, `-hw`, `-fw` forks; the linorobot2 base; the container image; the release manifest; the SISTEMA project; test logs.

## 3. Safety-relevant file list

The authoritative, machine-readable copy is [`safety-relevant-paths.txt`](safety-relevant-paths.txt): classes SR-A (safety chain design files, firmware safety layer, safety parameter sets), SR-Q (functional layers that feed hazards or configure limits), SR-T (build, CI, toolchain, pins). Anything else is NSR.

## 4. Baselines

`BL-nnn` tags across the repositories at each gate and at each release; the Living Safety Case baseline records once ported.

## 5. Branch and review rules

Pull requests only; two approvals on SR-A paths (upstream's rule adopted); CODEOWNERS.

## 6. Pins

How a pin moves: change record, impact analysis, one pull request.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
