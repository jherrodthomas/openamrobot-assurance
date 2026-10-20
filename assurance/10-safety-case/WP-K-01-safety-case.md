# WP-K-01 Safety Case

| Field | Value |
|---|---|
| Work product | WP-K-01 Safety case for the Gate A unit (UL 4600 structure: claims, arguments, evidence, defeaters) |
| Standard reference | ISO 13849-1:2023 §4.7, §10 (information); ISO 12100 §7 (documentation); Regulation (EU) 2023/1230 Annex IV Part A (technical documentation); UL 4600 §5, §6 |
| Version | 0.1 (2026-10-20): initial structure, every claim draft, every defeater open |
| Status | Draft |
| PL / scope | PL d target; Gate A unit (CFG-001); mobile base only |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I2 for the safety case) |
| Approver | Project lead |
| Baseline | BL-001 |

> [!WARNING]
> Draft. No claim is accepted, no evidence is available, every defeater is open. The machine-readable copy of
> this document lives in `assurance/case/`; the validator fails if the two disagree (check X3). The dashboard in
> the README is generated from those records.

## 1. Purpose and scope

This document argues, for the reference configuration CFG-001 (the Gate A unit of WP-C-01), that the robot poses
no unreasonable risk when operated within its limits. At BL-001 the argument is a structure with open defeaters:
it records what would have to be true, what evidence would show it, and what is known to contradict it today.

## 2. Argument structure

Goal G0 is argued over four strategies: S1 per safety function (G1.x), S2 over the complementary measures (G2.x),
S3 over the command path (G3.x), S4 over the process (G4.x). GSN diagrams are generated from the records
(`case/tools`), not drawn by hand.

The cybersecurity branch of the argument is WP-K-03 ([cybersecurity case](WP-K-03-cybersecurity-case.md)); claims there that protect a safety function are referenced from the claims below, and the evidence for the safety functions themselves stays in this document.

## 3. Claims

| ID | Claim | Parent | Status | Evidence | Open defeaters |
|---|---|---|---|---|---|
| G0 | The Gate A unit poses no unreasonable risk | — | draft | Sn-01, Sn-02, Sn-03 | 4 |
| G1 | The safety functions SF-01 to SF-07 reach their required Performance Level | G0 | draft | Sn-04, Sn-05 | 0 |
| G1.1 | SF-01 emergency stop is implemented at PL d | G1 | draft | Sn-08 | 4 |
| G1.2 | SF-02 protective stop on personnel detection is implemented at PL d | G1 | draft | Sn-11, Sn-07 | 5 |
| G1.3 | SF-03 safely-limited speed is implemented at PL d | G1 | draft | Sn-11 | 2 |
| G1.4 | SF-04 stop on loss of command, communication or control is implemented at PL c | G1 | draft | Sn-06, Sn-10 | 3 |
| G1.5 | SF-05 prevention of unexpected start-up is implemented at PL c | G1 | draft | Sn-08 | 2 |
| G1.6 | SF-06 stop on drive fault is implemented at PL c | G1 | draft | Sn-06, Sn-10 | 4 |
| G1.7 | SF-07 powered-debug inhibit is implemented at PL b | G1 | draft | Sn-06, Sn-10 | 2 |
| G2 | The complementary electrical and mechanical measures are implemented | G0 | draft | — | 0 |
| G2.1 | The 24 V bus and the mains side are protected | G2 | draft | Sn-12 | 4 |
| G2.2 | Mass, payload and stability are within limits | G2 | draft | Sn-09, Sn-07 | 1 |
| G3 | The command path cannot defeat the safety functions | G0 | draft | — | 0 |
| G3.1 | Motion and parameter interfaces are authenticated and bounded | G3 | draft | Sn-13 | 4 |
| G4 | The evidence was produced under a controlled process | G0 | draft | — | 0 |
| G4.1 | A configuration baseline exists and the forks are pinned to it | G4 | draft | Sn-14 | 3 |
| G4.2 | Hazards are identified completely and rated | G4 | draft | Sn-02, Sn-01 | 2 |
| G4.3 | Verification and review evidence exists for the motion-critical code | G4 | draft | Sn-10, Sn-15 | 6 |

## 4. Assumptions of use

AOU-01 to AOU-07 of WP-C-01 §8 apply to every claim. At BL-001 each holds only procedurally.

## 5. Safety functions and Performance Levels

SF-01, SF-02, SF-03 at PLr d; SF-04, SF-05, SF-06 at PLr c; SF-07 at PLr b (WP-C-03 §7, DQ-005 decided
2026-10-20). None reaches any PL at BL-001.

## 6. Evidence

Status rule: Available = performed and approved at a named baseline; Partial = drafted analysis or
specification, not reviewed; Missing = not yet performed.

**Available 0, Partial 8, Missing 7** (15 evidence items)

| ID | Evidence | Location | Status | Supports |
|---|---|---|---|---|
| Sn-01 | Item definition and limits of the machinery | `assurance/02-concept/WP-C-01-item-definition.md` | Partial | G0, G4.2 |
| Sn-02 | Risk assessment and PLr determination | `assurance/02-concept/WP-C-03-risk-assessment.md` | Partial | G0, G4.2 |
| Sn-03 | Baseline gap assessment GAP-01 to GAP-40 | `assurance/00-assessment/gap-assessment.md` | Partial | G0 |
| Sn-04 | Safety requirements specification SR-00.01 to SR-10.03 | `assurance/03-system/WP-S-02-safety-requirements.md` | Partial | G1 |
| Sn-05 | Technical safety concept: stop chain and SRP/CS architecture | `assurance/03-system/WP-S-03-technical-safety-concept.md` | Partial | G1 |
| Sn-06 | Firmware hardening change record and impact analysis | `assurance/07-supporting/impact/change-2026-10-20-fw-hardening.md` | Partial | G1.4, G1.6, G1.7 |
| Sn-07 | Stopping-distance and deceleration measurement (category 0 coast and commanded stop) | `assurance/06-validation/README.md` | Missing | G1.2, G2.2 |
| Sn-08 | Emergency-stop chain test record (each device, each channel, welded contact, reset held) | `assurance/06-validation/README.md` | Missing | G1.1, G1.5 |
| Sn-09 | Mass, centre of gravity and tipping record | `assurance/06-validation/README.md` | Missing | G2.2 |
| Sn-10 | Firmware compile and bench test of the hardening change | `assurance/06-validation/README.md` | Missing | G1.4, G1.6, G1.7, G4.3 |
| Sn-11 | Protective field and speed-limit validation (ISO 13849-2) | `assurance/06-validation/README.md` | Missing | G1.2, G1.3 |
| Sn-12 | Electrical protection inspection (fuse, disconnect, mains, source selection) | `assurance/06-validation/README.md` | Missing | G2.1 |
| Sn-13 | Network and command-path security concept and test | `assurance/06-validation/README.md` | Missing | G3.1 |
| Sn-14 | Baseline record BL-001 | `assurance/case/baselines/baselines.yaml` | Partial | G4.1 |
| Sn-15 | Safety case WP-K-01 | `assurance/10-safety-case/WP-K-01-safety-case.md` | Partial | G4.3 |

## 7. Defeaters

One defeater per finding of the gap assessment. A defeater closes only through a recorded review that names the
evidence closing it.

| ID | Defeater | Gap | Claims | Status |
|---|---|---|---|---|
| DF-01 | No emergency-stop function exists in the documented design | GAP-01 | G1.1 | open |
| DF-02 | The only stop is a coast (PWM 0, no brake, BRK unwired) | GAP-02 | G1.1 | open |
| DF-03 | Stop depends on the same core and software that drives the motors; no hardware watchdog | GAP-03 | G1.4 | open |
| DF-04 | No motor-driver fault feedback (ERR/DO1 unwired) | GAP-04 | G1.6 | open |
| DF-05 | No plausibility checks on actuation (encoder loss, stall) | GAP-05 | G1.6 | open |
| DF-06 | /cmd_vel has no validity or freshness semantics | GAP-06 | G1.4 | open |
| DF-07 | Runtime parameter injection changes motor behaviour without a gate | GAP-07 | G1.7 | open |
| DF-08 | Raw-PWM diagnostic path enabled in the deployed build | GAP-08 | G1.7 | open |
| DF-09 | Per-boot calibration is safety-relevant and enforced by nothing | GAP-09 | G1.5 | open |
| DF-10 | Firmware cannot identify itself; build not reproducible | GAP-10 | G1.5 | open |
| DF-11 | Firmware has no verification evidence | GAP-11 | G4.3 | open |
| DF-12 | Documentation disagrees with code on safety behaviour | GAP-12 | G0 | open |
| DF-13 | The software envelope is best-effort and carries no safety claim | GAP-13 | G1.3 | open |
| DF-14 | Objects below the scan plane are invisible to every layer | GAP-14 | G1.2 | open |
| DF-15 | Docking removes every reactive protection | GAP-15 | G1.2 | open |
| DF-16 | Collision monitor tolerates a stale scan for 1 s and masks 0.15 m | GAP-16 | G1.2 | open |
| DF-17 | Operating limits rest on an operational battery rule | GAP-17 | G1.6 | open |
| DF-18 | Real-robot bring-up in progress; no recorded acceptance test | GAP-18 | G0 | open |
| DF-19 | No battery fuse and no battery disconnect | GAP-19 | G1.1, G2.1 | open |
| DF-20 | Battery and mains in parallel with no source selector; mains side undocumented | GAP-20 | G2.1 | open |
| DF-21 | Logic power not independent of compute (Teensy on Pi USB) | GAP-21 | G2.1 | open |
| DF-22 | No safety-rated detection of persons | GAP-22 | G1.2 | open |
| DF-23 | No mechanical safety data (mass, CoG, tipping, stopping distance) | GAP-23 | G2.2, G4.2 | open |
| DF-24 | No regenerative-braking path | GAP-24 | G1.6, G2.1 | open |
| DF-25 | The BOM does not describe the robot | GAP-25 | G0 | open |
| DF-26 | Licence statements conflict | GAP-26 | G0 | open |
| DF-27 | Any participant on ROS domain 0 can move the robot or retune it | GAP-27 | G3.1 | open |
| DF-28 | The on-screen E-STOP is a software request over a network | GAP-28 | G1.1, G3.1 | open |
| DF-29 | Supply chain is unpinned | GAP-29 | G3.1, G4.1 | open |
| DF-30 | No risk assessment, hazard list, safety functions or PLr upstream | GAP-30 | G4.2 | open |
| DF-31 | Safety review is a checkbox | GAP-31 | G4.3 | open |
| DF-32 | The release is not a configuration baseline | GAP-32 | G4.1 | open |
| DF-33 | Safety-relevant design decisions are not in any repository | GAP-33 | G4.1 | open |
| DF-34 | Process capability at CL0 for engineering processes | GAP-34 | G4.3 | open |
| DF-35 | Undock is a blind 0.7 m reverse; rear sector masked; backup enabled | GAP-35 | G1.2 | open |
| DF-36 | No command arbitration; unbounded docking speeds | GAP-36 | G1.3, G3.1 | open |
| DF-37 | Failure handling is report-only | GAP-37 | G1.4 | open |
| DF-38 | Safety documentation diverges from the configuration | GAP-38 | G4.3 | open |
| DF-39 | The motion-critical code has no tests | GAP-39 | G4.3 | open |
| DF-40 | Simulation and real robot differ in the parameters that matter | GAP-40 | G4.3 | open |

## 8. Reviews

None at BL-001.

## 9. Residual risk statement

Not yet possible: no safety function exists on the configuration, so no operation with people in reach of the
robot is within this case (WP-C-03 §8).

## 10. Open items

| ID | Item | Needed by | Claims |
|---|---|---|---|
| OI-1 | Weigh the Gate A unit, record height, castors and centre of gravity | G1 | G2.2, G4.2 |
| OI-2 | Measure stopping distance from 0.20 m/s, coast and commanded, loaded and unloaded | G1 | G2.2, G1.2 |
| OI-3 | Set a payload limit and a payload height limit | G1 | G2.2 |
| OI-4 | Resolve what the panel E-stop button switches on the as-built unit | G1 | G1.1 |
| OI-5 | Decide the regulatory frame (DQ-003) and the item scope (DQ-004) | G1 | G0 |
| OI-6 | Reviewer with Gate A operating experience confirms every rating in WP-C-03 | G1 | G4.2 |
| OI-7 | Choose the detection device and the speed monitor for the bench build; budget decision | G2 | G1.2, G1.3 |
| OI-8 | Read the ZBLD.C20 manual for BRK/DI5, SPD/DO2 and ERR/DO1 semantics | G2 | G1.1, G1.6 |
| OI-9 | Compile and bench-test the firmware hardening change | G2 | G1.4, G1.6, G1.7, G4.3 |
| OI-10 | Push the BL-001 tags to the forks and pin the reusable CI workflow to a SHA | G1 | G4.1 |
| OI-11 | Interface change for stamped or sequenced velocity commands (SR-04.03) | G2 | G1.4 |
