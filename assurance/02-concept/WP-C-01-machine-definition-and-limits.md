# WP-C-01 Machine definition and limits

| Field | Value |
|---|---|
| Work product | WP-C-01 Machine definition and limits (intended use, foreseeable misuse, use, space and time limits) |
| Standard reference | Machinery: 12100 §5.3; 3691-4 §1, §4; SRP/CS: 13849-1 §5 (inputs); IEC 62443: 62443-4-1 SR-1; Other: Machinery Reg. Annex III §1.1.2; ASPICE: SYS.1 |
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

Defines the machine: what it is, what it is for, its limits of use, space and time, and the reasonably foreseeable misuse the risk assessment must consider (ISO 12100 §5.3). It draws the boundary of WP-M-01 T-02 and states the interface assumptions the arms and lift will later need (T-14).

## 2. Description of the machine

The Gate A unit as traced in the gap assessment §3.1: base, drive, power, sensing, compute, firmware, ROS 2 stack; plus the bench safety hardware of WP-V-07 §2. Mass, dimensions and track to be measured (GAP-23).

## 3. Intended use

Autonomous indoor transport and docking in a defined operating area; teleoperation for test. Not: outdoor use, slopes beyond the limit, carrying people, manipulation (base only, DQ-004).

## 4. Limits of use

Payload, speed, slope, floor, temperature, humidity, lighting, people presence; users and their training; the test operator during development.

## 5. Space and time limits

Operating area, docking lane, travel envelope including arms-to-come; duty cycle, battery autonomy, maintenance intervals; service life of safety components.

## 6. Reasonably foreseeable misuse

Standing in the docking lane, reaching into the robot while powered, operating from an unmanaged laptop on the same Wi-Fi, running with a low battery, bypassing the E-stop reset. Feeds WP-C-06.

## 7. Machine boundary and interfaces

Inside: base, chain, firmware, ROS 2 stack as installed. Outside with interface assumptions: docking station and charger, site network, operator computer, the arms and lift (payload, centre of gravity, stop chain hooks).

## 8. Hazard zones

Named zones for the hazard list: front, rear (masked scan sector), sides below the scan plane, docking lane, battery compartment.

## 9. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G1 |
