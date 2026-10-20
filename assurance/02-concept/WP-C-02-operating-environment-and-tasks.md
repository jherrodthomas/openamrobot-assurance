# WP-C-02 Operating environment and task specification

| Field | Value |
|---|---|
| Work product | WP-C-02 Operating environment and task specification (zones, floors, people, lighting) |
| Standard reference | Machinery: 3691-4 §4, §6; 12100 §5.3; Other: ISO 21448 §5 (informative method); ASPICE: SYS.1 |
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

Specifies the operating environment and the tasks the robot performs in it: zones, floors, slopes, lighting, obstacles, people presence per zone and per task. It is the machinery analogue of an operational design domain and the source of every operating-environment limit the safety case relies on.

## 2. Zones

Per zone: floor type and slope, obstacles, steps and drops, lighting, reflectivity, people presence (none, briefed, public). People presence per zone is an input to the misuse analysis of WP-C-06.

## 3. Tasks

Transport leg, docking, undocking, waiting, charging, manual recovery; speed and people presence per task.

## 4. Environmental limits

Temperature, humidity, dust, electromagnetic environment, Wi-Fi coverage (loss of agent is a stop, GAP-37).

## 5. What is outside the environment

Outdoor, slopes above the limit, wet floors, glass walls (LiDAR), crowds; each exclusion becomes a limit in WP-O-03.

## 6. Test area during development

The area WP-V-07 requires, as the first defined zone.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
