# WP-W-01 SW development environment, languages and coding guidelines

| Field | Value |
|---|---|
| Work product | WP-W-01 SW development environment, languages and coding guidelines |
| Standard reference | SRP/CS: 13849-1 §7; 61508-3 §7.4.4; IEC 62443: 62443-4-1 SI-1, SI-2; Other: MISRA C:2012 (firmware); ASPICE: SWE.3 |
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

The software development environment of the fork: languages, toolchains, coding guidelines, static analysis and build reproducibility for the Teensy firmware (C++ with MISRA C:2012 as the basis), the ROS 2 packages (Python and C++) and the tooling.

## 2. Toolchains and pins

PlatformIO with a pinned `platformio.ini` and toolchain (GAP-10), ROS 2 Jazzy pinned by distribution snapshot, container image by digest, reusable workflows by SHA (GAP-29).

## 3. Coding guidelines

MISRA C:2012 subset for the firmware with deviation records; style and lint for Python; forbidden constructs (dynamic allocation after init, unbounded parameters).

## 4. Static analysis and CI

cppcheck or equivalent, clang-tidy, coverage; a firmware build in CI on every pull request (GAP-11).

## 5. Tool list

Cross-reference to WP-P-07.

## 6. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G3 |
