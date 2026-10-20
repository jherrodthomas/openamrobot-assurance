# WP-C-05 Risk reduction concept

| Field | Value |
|---|---|
| Work product | WP-C-05 Risk reduction concept (three-step method: inherently safe design, safeguarding, information for use) |
| Standard reference | Machinery: 12100 §6 (three-step method), §5.6 (adequate risk reduction), §7 (documentation); 3691-4 §4; 10218-2 §5 (CFG-002); SRP/CS: 13849-1 §5; Other: Regulation (EU) 2023/1230 Annex III §1.1.2 (principles of safety integration); ASPICE: SYS.2 |
| Version | 0.1 (2026-10-20): first content. Every rated row of WP-C-03 v0.5 §5 allocated to the three steps; residual-risk class per row; three design measures added to the WP-C-03 §6 register (DM-08 energy limit, DM-09 brakes on power loss, DM-10 control-system design); hazards introduced by the measures; adequacy criteria; traceability to the claims and defeaters of WP-K-01. 0.0: skeleton |
| Status | Draft |
| PL / scope | All hazards H-01…H-15 of WP-C-03 v0.5 on CFG-001 (Gate A unit, bench only since DQ-011 C) and CFG-002 (2.0 mobile manipulator, unverified) |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | BL-001 |

> [!WARNING]
> Draft. This document allocates measures that, with few exceptions, do not exist on any build: WP-C-03 §6 says
> what exists today, and the answer is almost nothing. The allocation is the design intent that the fork's
> builds must meet; a residual-risk class here is a statement about the design, not about a robot. Clause numbers
> of ISO 12100 and ISO 13849-1 are from memory and are to be checked against licensed copies (DQ-016, answered C:
> unscheduled). Every CFG-002 row rests on upstream's plan set and is unverified.

## 1. Purpose and method

ISO 12100 §6 reduces risk in a fixed order: first inherently safe design, then safeguarding and complementary
protective measures, then information for use. The order is the argument: a measure of a later step is used only
for the risk the earlier steps leave, and information for use is never the primary measure for a hazard that can
kill or maim. The principle of the gap assessment (§3, [GAP-30](../00-assessment/gap-assessment.md)) is restated
here as a rule: **a limitation that is only documented is not a control for a hazard rated S2.**

Inputs: the hazards, situations and ratings of [WP-C-03](WP-C-03-risk-assessment.md) §4 and §5 (25 rated rows,
15 hazards); the measure register of WP-C-03 §6, which this document extends by DM-08…DM-10; the safety functions
of [WP-C-04](WP-C-04-safety-functions-and-plr.md); the zones, limits and exclusions of
[WP-C-02](WP-C-02-operating-environment-and-tasks.md); the scenarios, misuses, collaborative rules and derived
requirements of [WP-C-06](WP-C-06-human-robot-interaction-and-misuse.md); the assumptions of use AOU-01…AOU-10 of
[WP-C-01](WP-C-01-item-definition.md) §8. Outputs: the allocation table of §5 (one row per rated row of WP-C-03
§5), the information-for-use items that [WP-O-03](../09-production-operation/WP-O-03-information-for-use.md)
carries, and the residual-risk statement that goal G0 of [WP-K-01](../10-safety-case/WP-K-01-safety-case.md)
argues.

### 1.1 Residual-risk classes

Each row of §5 carries one class for the risk that remains after the three steps, with the condition the class
depends on.

| Class | Meaning | What the residual is |
|---|---|---|
| **S** safeguarded at the PLr | A control function of WP-C-04 at the row's PLr is the primary measure | the probability of a dangerous failure of the SRP/CS at that PL (ISO 13849-1 §4.5), plus the named cases the function does not cover |
| **D** reduced by design | A design or complementary measure with no control function is the primary measure (fuse, mains installation, mass and stability, holding by design) | the correctness of the design value, proven by measurement or inspection |
| **I** carried by information for use | The hazard is S1, or the earlier steps leave a residual that a trained person avoids (P1 rows); the instruction, marking or training is the last measure, not the only one | the person's behaviour; accepted only where severity is S1 or the steps above are at the PLr |
| **E** excluded | The hazard does not arise inside the operating environment because WP-C-02 §5 excludes the situation | nothing inside the environment; the exclusion is a condition (OL-01) that a site survey and a geofence enforce |
| **O** open | No adequate measure exists in any design yet, or the design is not public (CFG-002); the row is outside the assessment per WP-C-03 §8 until it closes | not evaluated |

A row may name a second class for the part of the residual another step carries ("S, then I").

### 1.2 Configurations

On CFG-001 nothing with wheels on the ground is inside the assessment (DQ-011 C); its on-ground rows below are
the design intent a future on-ground configuration must meet, and the bench rows (H-04) are its live rows. On
CFG-002 every row is open until the design is public (DQ-020 A; WP-C-01 §1.2); the allocation says what the 2.0
design must provide and names the upstream evidence it waits for.

## 2. Step 1: inherently safe design measures (ISO 12100 §6.2)

The measure register is WP-C-03 §6; this section explains the design-step measures and adds three that the
skeleton named and the register lacked. "Reduces" and "status today" are as the register states them.

| Measure | What it does | Reduces | ISO 12100 §6.2 principle (to be checked) |
|---|---|---|---|
| DM-01 payload limit, restraint, height limit | bounds the mass and the centre of gravity the stability analysis assumes (WP-H-08) | H-06 | limits of the machine; stability |
| DM-02 measured stopping distance and a deceleration limit consistent with stability | the stopping distance sizes the SF-02 field (WP-C-06 §3); the deceleration limit keeps a commanded stop from tipping the robot | H-06, H-01 | stability; limiting forces |
| DM-03 mass and centre-of-gravity record; tipping test | the stability margin for every pose and payload (on CFG-002 with the arms and lift: CA-05, the F2S cases) | H-06, H-15 | stability |
| DM-07 gripper and lift hold their load on power loss by design | a spring-closed or self-locking gripper and a brake or self-locking lift drive: the safe state needs no energy | H-14, H-15 | mechanical design; fail-safe on loss of energy |
| **DM-08 speed ceiling and drive-torque limit** (new) | the firmware command ceiling of 0.25 m/s and 0.6 rad/s (DQ-006 A, applied in the fork firmware) sits above the zone limits and below the 0.71 m/s clamp upstream shipped; at the ceiling the kinetic energy of a 45 kg robot is about 1.4 J and the drive's stall push about 70 N (WP-C-03 H-01 hand-stop row). The ceiling is not safety-rated: SF-03 is the safety function; DM-08 limits the energy any failure of the command path can release | H-01, H-02, H-03 | limiting the kinetic energy; limiting forces |
| **DM-09 brakes that engage on power loss** (new) | on CFG-002 the hub motors carry brakes (upstream, unverified): a category 0 stop is a braked stop and a stopped robot holds on a slope. CFG-001 has no brake and coasts (GAP-02), which is one reason it stays on the bench (DQ-011 C) and why its stopping distance is the input every field size waits for | H-01, H-06, H-15 | fail-safe on loss of energy; stability |
| **DM-10 control-system design** (new) | actuator power is removed by the safety chain upstream of every actuator, never through software (WP-S-03 §3.2); one command arbiter with the stop at the highest priority (SR-00.02); safety parameters not writable from the network (SR-00.05); the chain-only functions and channel 2 of the two-channel functions independent of every microcontroller, network and configuration file (WP-S-02 §1) | H-02, H-12 | inherently safe design of the control system (§6.2.11) |

Operating-environment limits OL-01 (zone exclusions) and OL-02 (speed per zone, crawl in the dock lane and in
reverse, carry limit) are limits of the machinery in the sense of ISO 12100 §5.3 and are listed with step 1
because they bound the energy and the exposure before any safeguard acts; SF-03 enforces OL-02 and a site survey
with a geofence (WP-C-02 OI-3) enforces OL-01.

What step 1 does not achieve: no hazard of WP-C-03 is eliminated by design. The robot shares the floor with
people (DQ-005), its mass is tens of kilograms, the arms of CFG-002 can pull 150 N. Every S2 hazard needs step 2.

## 3. Step 2: safeguarding and complementary protective measures (ISO 12100 §6.3)

### 3.1 Safeguards: the safety functions

The twelve safety functions of WP-C-04 are the safeguards; each is a control function of the SRP/CS at its PLr,
carried by the elements of [WP-S-03](../03-system/WP-S-03-technical-safety-concept.md) and specified as
requirements in [WP-S-02](../03-system/WP-S-02-safety-requirements.md).

| Function | Safeguard type | PLr | Config | Carried by (WP-S-03 §2) | Verified by |
|---|---|---|---|---|---|
| SF-01 emergency stop | complementary protective measure (ISO 12100 §6.3.5.2; ISO 13850), also the stop device of SF-10 and the power path of SF-12 | d | both | E1 devices, E2 safety relay, E3 contactors and E4 driver inhibit; on CFG-002 the PNOZ s3 and K1, K2 on traction, arms and lift | WP-V-04; Sn-08 |
| SF-02 protective stop on personnel detection | sensitive protective equipment: safety laser scanner and rear bumper, field sets per speed (DQ-007 A) | d | both | E5a, E5b into E6 and E2 | WP-V-03; Sn-11 |
| SF-03 safely-limited speed | monitoring function that enforces OL-02 and the carry limit | d | both | channel 1 firmware, channel 2 speed monitor E6 (DQ-014 B) | WP-V-02, WP-V-05; Sn-11 |
| SF-04 stop on loss of command, communication or control | monitoring function | c | both | channel 1 firmware watchdog and command validation, channel 2 hardware watchdog and heartbeat | WP-V-05; Sn-10 |
| SF-05 prevention of unexpected start-up | restart interlock (ISO 12100 §6.3.5.?; EN 60204-1 §9.2.5.4 reset, to be checked) | d | both | E7 monitored reset through E2 | WP-V-04; Sn-08 |
| SF-06 stop on drive fault | monitoring function | c | both | channel 1 firmware plausibility, channel 2 driver fault inputs and E10 undervoltage | WP-V-05; Sn-10 |
| SF-07 powered-debug inhibit | inhibit of a non-operational path; arming input on the bench image | b | both | firmware image and the E8 arming input | WP-V-05; Sn-10 |
| SF-08 warning before motion | warning device (complementary measure, ISO 12100 §6.3.5.?) | b | both | E7 stack light and sounder | WP-V-04 |
| SF-09 enabling control for teleoperation | hold-to-run control | c | both | the pendant's enabling signal into the firmware (channel 1) and E2 (channel 2) | WP-V-05 |
| SF-10 base motion inhibit while an arm is unstowed | interlock | d | CFG-002 | arm pose signals as a condition of the traction enable | WP-V-05 (CFG-002) |
| SF-11 arm safe stop on entry to the station workspace | safety-rated monitored stop (ISO 10218-2, DQ-021 A); no power-and-force limiting claimed | d | CFG-002 | station field or mat into an external safety controller and the arms' safe torque off | WP-V-03, WP-V-05 (CFG-002) |
| SF-12 lift and gripper holding on stop and power loss; lift interlock | holding by design (DM-07) proven by test; interlock on standstill, pose and the keep-clear zone | d | CFG-002 | lift brake, gripper design, PNOZ or safety PLC conditions | WP-V-05 (CFG-002) |

### 3.2 Complementary protective measures that are not control functions

| Measure | Kind (ISO 12100 §6.3.5, to be checked) | Reduces | Where specified |
|---|---|---|---|
| DM-04 fuse on the battery positive, lockable disconnect | isolation and energy dissipation (EN 60204-1 §5.3) | H-07, H-04, H-08 | WP-H-02 E11; WP-H-05 |
| DM-05 mains side per EN 60204-1: identified converter, RCD, earth, enclosure, inlet | protection against electric shock | H-08 | WP-H-05 |
| DM-06 one source at a time; battery voltage monitoring | protection against the parallel sources; the monitoring feeds SF-06 | H-09, H-03 | WP-H-02 §3.6, E10 |
| E-stop devices reachable from both long sides and a pendant in the operator's hand | part of SF-01 (ISO 13850 §4) | H-01, H-10 | SR-01.01, SR-01.02 |
| Station marking and the lift keep-clear zone (CFG-002) | physical demarcation of the workspace SF-11 and SF-12 monitor; also IFU-04 | H-13, H-15 | SR-11.01, SR-12.03 |

### 3.3 Hazards introduced by the measures

ISO 12100 §6 is iterative: a measure can create a hazard. These are the ones the allocation accounts for.

| Measure | Hazard it introduces | Where it is reduced |
|---|---|---|
| A commanded stop at −2.5 m/s² (SF-02, SF-03) | tipping of a high payload, a load thrown off the top plate (H-06) | DM-01, DM-02: the deceleration limit is set by the stability analysis (SR-02.05) |
| A braked category 0 stop (DM-09, SF-01) | the same, harder: the brake stops the wheels, not the payload | DM-01, DM-02; WP-V-02 measures the braked stop loaded |
| A robot that stops and holds in an aisle (SF-02, SF-04, DM-09) | a blocked escape route or fire door | WP-C-02 §5 excludes doors and turnstiles not interlocked with the stop; WP-O-03 site rules |
| Nuisance stops of a safety scanner | the operator deactivates the monitor or widens a parameter (MU-10) | DM-10: safety parameters locked (SR-00.05); field switching at PL d, not software deactivation (SR-02.07) |
| A silent stop (SF-02, SF-04) | a stopped robot is pushed or ignored, then restarts (H-05, MU-14) | SF-05 reset, SF-08 warning, SR-00.04 indication, IFU-01 |
| The emergency stop removes arm and lift power (SF-01, CA-03) | a dropped load (H-14) | DM-07 and SF-12: the load is held without energy |
| The monitored stop on the arms (SF-11) | a stopped arm invites a person to clear the jam by hand (MU-15) | SF-11 resumes only on a deliberate action with the workspace clear (SR-11.03); IFU-04; AOU-10 |
| The warning device (SF-08) | habituation: the warning is ignored | the warning precedes motion by a bounded time and is the last measure, not the first (SF-02 and SF-05 are) |

## 4. Step 3: information for use (ISO 12100 §6.4)

What remains for the user after steps 1 and 2. Each item is a residual by construction: the row of §5 it serves
has a step 1 or step 2 measure, and the item covers the part those leave. The rule of §1 is enforced by the §5
check: no row rated c or higher has information for use as its only measure. The items land in WP-O-03 (manual,
markings, warnings), in WP-O-02 (operating and maintenance procedures) and in training.

| Item | Content | Serves (WP-C-03 rows) | Why it is the residual, not the measure | Lands in |
|---|---|---|---|---|
| IFU-01 operator training and rules | the on-screen stop is not an emergency stop (HR-05); watch the robot, not the screen (MU-02); a stopped robot is not an idle one (MU-14); nobody within reach during testing; the bench rule (AOU-03) | H-01 aisle and hand-stop, H-02, H-04, H-05, H-10 | SF-01 is physical and reachable; SF-05 and SF-08 cover the restart; training removes the P2 the operator's own error would add | WP-O-03 §2; WP-O-02 training record |
| IFU-02 site measures | blind corners, one-way rules for people, lane marking, recorded in the site survey (HR-09) | H-01 blind corner and dock lane | the field cannot cover a corner (WP-C-06 §3); the site measure is a condition of the operating environment: a site that cannot provide it excludes the corner (OL-01) | WP-O-03 §3; WP-O-01 site survey |
| IFU-03 payload, height and restraint markings | on the top plate (HR-08) | H-06 | DM-01…DM-03 set the limits; the marking makes them visible at the point of loading | WP-O-03 §4; WP-H-08 |
| IFU-04 station marking, hand-over rule, lift keep-clear zone (CFG-002) | the workspace boundary and the keep-clear zone painted; hand-over only with the arm stopped (CA-06); nothing hung on an arm or the carriage (MU-16) | H-13, H-14, H-15 | SF-11 and SF-12 monitor the marked zones; the marking tells people where the zones are | WP-O-03 §4; WP-O-01 |
| Operating-environment limits and exclusions | the limits of WP-C-02 §4 and the exclusions of §5, as operating limits and warnings | every row (OL-01, OL-02) | the limits are what the ratings assume; a site outside them is outside the assessment | WP-O-03 §3 |
| Assumptions of use AOU-01…AOU-10 | the conditions WP-C-01 §8 places on the operator and the site | the rows that name them | each is procedural today; those that bound an S2 row (AOU-01, AOU-02, AOU-08, AOU-09, AOU-10) hold only until the function that replaces them exists, and the row is open until then | WP-O-03 §2; WP-S-06 |
| Residual-risk warnings | the residual of every S and D row of §5, in the words of the residual column | every row | ISO 12100 §6.4.5: the user is told what the measures do not cover | WP-O-03 §2 |

## 5. Allocation table

One row per rated row of WP-C-03 §5, with the same first cell. PLr is the value adopted there. Measures are
named by the IDs of WP-C-03 §6 (DM, OL, SF, IFU) and, where a condition rather than a measure applies, by the
assumption (AOU), collaborative rule (CA) or derived requirement (HR). "—" means the step contributes nothing to
the row. Verification names the evidence item of WP-K-01 §6 or the validation work product. Figure 5-1 is drawn
from this table; CI fails if a measure is not in the WP-C-03 §6 register, if a hazard-measure pair here is not in
that register (or the reverse), if a row rated c or higher has no step 1 or step 2 measure, or if a row's PLr
disagrees with WP-C-03 §5.

| Hazard · situation | PLr | Step 1 design | Step 2 safeguarding | Step 3 information | Residual risk (class) | Verification |
|---|---|---|---|---|---|---|
| H-01 · aisle, staff crossing or walking beside the robot (OS-01: IS-01, IS-03) | d | DM-08, DM-02, DM-09, OL-02 | SF-02, SF-03, SF-01 | IFU-01 | **S.** The SRP/CS at PL d; a person below the detection height until HR-02 is confirmed (SR-02.03); a person who steps into the field inside the stopping distance, met at ≤ 0.20 m/s with the energy of DM-08 | Sn-11 (WP-V-03), Sn-07 (WP-V-02) |
| H-01 · aisle, blind corner (OS-01: IS-02) | d | DM-08, OL-02 | SF-02, SF-03 | IFU-02, IFU-01 | **S, then I.** The field cannot cover the corner; the zone speed makes a 0.5 m warning enough for a walking adult (WP-C-06 §3); the one-way rule or mirror is a site condition, and a site that cannot provide it excludes the corner (OL-01) | Sn-11; WP-O-01 site survey; WP-V-08 |
| H-01 · test area (OS-02) | c | — | SF-01 | AOU-01, AOU-02, IFU-01 | **S, then I.** Nobody in the path during a run; the observer's emergency stop and the pendant are the measure if someone enters; bench only on CFG-001 (DQ-011 C), so the row is the intent for an on-ground configuration | Sn-08 (WP-V-04); WP-V-07 |
| H-01 · dock lane, docking and reverse (OS-03: IS-04, IS-05) | d | DM-08, OL-02 | SF-02, SF-03 | IFU-02 | **S.** The lane field set and the rear bumper at crawl; the final approach inside the switched field is blind beyond the bumper's travel, so a person who enters the lane in the last 0.3 m meets the robot at 0.05 m/s; the lane marking and the dock indication keep people out of it (MU-04) | Sn-11; GAP-15 and GAP-35 closure (WP-S-03 OI) |
| H-01 · teleoperation and mapping (OS-04: IS-06) | c | DM-08 | SF-09, SF-03, SF-01, SF-02 | IFU-01 | **S, then I.** Motion only while the control is held, capped at the zone limit and at 0 m/s with a person in the zone and no detection (DQ-017 A); the operator watches the robot (MU-02); the pendant stop is in the same hand (SR-09.05) | WP-V-05; Sn-11 |
| H-01 · public floor (OS-15: IS-09) | excluded | OL-01 | — | — | **E.** Rated e; not operated (DQ-019 open on whether a PL e or force-limited argument is ever made); the exclusion is enforced by the map limits today and by a geofence when WP-C-02 OI-3 closes | WP-C-02 §5; WP-O-01 site survey |
| H-01 · a person pushes or hand-stops the robot (OS-14: IS-12) | a | DM-08 | SF-06 | IFU-01 | **I.** About 70 N of push; a stalled drive is a fault that stops both wheels (SR-06.02); a standing adult steps back; the hand-contact limit is measured under WP-C-06 OI-4 | WP-V-05 (stall test) |
| H-02 · uncommanded motion near people (OS-01, OS-09, OS-12) | d | DM-10, DM-08 | SF-01, SF-04, SF-05, SF-07, SF-03, SF-08 | IFU-01 | **S.** Every uncommanded path is bounded by SF-03 and ends in SF-04 or SF-01; a restart needs the reset of SF-05 and is announced by SF-08; what remains is a motion inside the speed limit for the watchdog time (200 ms) before the stop, and the SRP/CS failure probability | Sn-10 (WP-V-05), Sn-08 |
| H-03 · loss of control (OS-11, OS-14) | c | DM-06, DM-08, OL-02 | SF-06, SF-03 | AOU-04 | **S.** A swerve at a speed bounded by SF-03 for up to 1 s before the stall or following-error stop (SR-06.02, SR-06.03); the battery rule is procedural until E10 exists | Sn-10; WP-V-05 |
| H-04 · bench, wheels off the ground (OS-05) | a | — | SF-07 | AOU-03, IFU-01 | **I.** A finger or cable in the drive train on the bench; the technician can cut 24 V; the debug image reports itself (SR-07.02) | WP-V-07 bench rules |
| H-04 · bench image with wheels on the ground (OS-06) | b | DM-04 | SF-07, SF-01 | IFU-01 | **S.** The bench image needs the arming input (SR-07.03); the disconnect removes power for calibration with the wheels down; the emergency stop covers a run that starts | Sn-10; Sn-12 |
| H-05 · restart after a chain, fault or watchdog stop (OS-09) | d | — | SF-05, SF-01 | IFU-01 | **S.** No restart without a deliberate reset at the robot with no demand present (SR-05.01…SR-05.04); the residual is the SRP/CS failure probability at PL d and a reset given while a person is behind the robot, which SF-08 announces | Sn-08 (WP-V-04) |
| H-05 · resume after waiting on a person (OS-13: IS-10) | d | — | SF-02, SF-08 | IFU-01 | **S.** Resume only with the field clear (SR-02.08) after the warning of SR-08.02; the residual is a person who is beside the robot, outside the field, and starts to cross as it resumes: at PL b the warning is the measure, the field is the backstop | Sn-11; WP-V-04 (warning timing) |
| H-06 · tipping, payload, a person on the robot (OS-10, OS-14) | c | DM-01, DM-02, DM-03, DM-09, OL-01, OL-02 | — | IFU-03, AOU-06, AOU-07 | **D, then I.** The stability margin is a design value proven by test (Sn-09) and respected by the deceleration limit (SR-02.05) and the slope and threshold limits; a person sitting on the robot (MU-05) and an unrestrained load (MU-06) are the information-for-use residual, acceptable because exceeding the limit needs a deliberate act and the mass is tens of kilograms, not tonnes | Sn-09; Sn-07 (WP-V-02 loaded stop) |
| H-07 · electrical fire (OS-07, OS-08, any) | n/a | DM-04 | — | — | **D.** A fused, disconnectable 24 V bus (EN 60204-1 §7.2); the residual is a fault downstream of the fuse within the fuse's let-through, bounded by cable sizing (WP-H-05) | Sn-12 (inspection) |
| H-08 · electric shock (OS-07, OS-08) | n/a | DM-05, DM-04 | — | — | **D.** Mains present only when charging, through an identified converter with RCD, earth and enclosure; the residual is the installation's conformity, inspected, and charging by a trained operator (WP-O-02) | Sn-12 |
| H-09 · battery (OS-07, any) | n/a | DM-06 | SF-06 | AOU-04 | **D.** One source at a time; over-discharge stopped by SR-06.05; gassing is slow and the AGM cells are sealed; the BMS of CFG-002 replaces the relay | Sn-12; WP-V-05 (undervoltage) |
| H-10 · mode confusion (OS-04, OS-09: IS-06, IS-11; MU-01) | d | HR-05 | SF-01, SF-05, SF-08, SF-09 | IFU-01 | **S.** The interface cannot be mistaken for the stop once HR-05 is applied (SR-01.09), the physical stop is reachable, the state is shown from every side (SR-00.04) and a restart is announced; the residual is the operator's error against a correctly indicating robot, which training reduces | WP-V-04; WP-V-08 (operator trials) |
| H-11 · loss of sensing (OS-11) | c | — | SF-04, SF-02 | — | **S.** The navigation sensing can fail silently; the safety scanner is independent of it (SR-02.06) and the loss of the agent or the heartbeat is a stop (SR-04.01, SR-04.04); the residual is the SRP/CS failure probability | Sn-10; Sn-11 |
| H-12 · unauthorised command (OS-12) | c | DM-10 | SF-03, SF-07 | AOU-05 | **S.** A malicious or mistaken command moves the robot inside the speed limit until a person is detected or the operator stops it; it cannot change a safety parameter or defeat a chain-only function (SR-90.03); channel 1's command input is covered at SL 2 (DQ-013 A, WP-C-08); the private network is an assumption until WP-S-07 exists | Sn-13 (WP-V-06); WP-V-05 |
| H-13 · arm contact at a station (OS-16: IS-13; CFG-002) | d | — | SF-11, SF-01, SF-08 | IFU-04, AOU-10 | **O.** No arm safety function exists in any repository; the monitored stop is the design intent (DQ-021 A) with no contact claimed (SR-11.05); until the station device exists, nobody is within reach of a moving arm (AOU-10), which is procedural and therefore not a control for an S2 row | WP-V-03, WP-V-05 on CFG-002; upstream OpenArm pose and safe-torque-off outputs (WP-S-02 OI-8) |
| H-13 · base moves with an arm extended (OS-16, OS-18: IS-15; CFG-002) | d | — | SF-10, SF-02, SF-03 | AOU-08, IFU-04 | **O.** The interlock is a planned upstream motion rule, not a safety function; the carry field set and the carry limit are unsized; AOU-08 holds until SF-10 exists | WP-V-05 on CFG-002; upstream `LIFT` motion rules |
| H-14 · load drops from the gripper or the lift (OS-16…OS-18: IS-14, IS-15; CFG-002) | d | DM-07 | SF-12, SF-01, SF-11 | IFU-04, AOU-09 | **O.** Holding by design is the measure and is unproven: the DOLD holding evidence is an upstream release gate not passed; the gripper's behaviour on power loss is not published; the emergency stop removes arm and lift power (CA-03), so the holding test of SR-12.05 is what closes the row | WP-V-05 (SR-12.05); upstream `LIFT` release gate |
| H-15 · crushing or shearing at the lift (OS-17: IS-14; CFG-002) | c | DM-07 | SF-12, SF-08, SF-10 | IFU-04, AOU-09 | **O.** The interlock on standstill, pose and the keep-clear zone (SR-12.03) and the warning before lift motion exist in no design; 18 mm/s gives a hand time to withdraw, a foot none; AOU-09 holds until SF-12 exists | WP-V-05 on CFG-002 |
| H-15 · tipping with an arm extended or while carrying (OS-16, OS-18; CFG-002) | c | DM-03, OL-02, DM-09 | SF-03, SF-10 | IFU-04 | **O, then D.** Upstream's F2S model covers the cases (CA-05) but its rerun is pending; the carry limit (CA-07) and the carry pose (SF-10) are the design conditions; the row becomes D when the stability record (Sn-09) covers the arm poses and the braked stop | Sn-09 on CFG-002; upstream F2S rerun |

![Figure 5-1: allocation map: one row per rated row of the risk assessment grouped by hazard, with the adopted Performance Level in a coloured chip on the left, then three columns for the three steps of ISO 12100 holding one chip per measure, coloured by kind, and on the right the residual-risk class as a coloured marker; the five CFG-002 rows are marked open and the public-floor row excluded](figures/fig-c05-5-1-allocation.svg)

*Figure 5-1.* The table above as a map: left to right is the ISO 12100 order, and the residual class on the right says which step carries what remains. Every row rated c or higher has a chip in step 1 or step 2. Generated by [`figures/fig_c05.py`](figures/fig_c05.py) from the §5 table; CI fails if it is stale or if the table disagrees with WP-C-03 §5 and §6.

## 6. Adequate risk reduction and residual risk (ISO 12100 §5.6)

The criteria ISO 12100 §5.6.2 gives for adequate risk reduction (to be checked), and where each stands.

| Criterion | Status at BL-001 | Where |
|---|---|---|
| All operating conditions and intervention procedures considered | 18 situations over 9 modes and 11 tasks; maintenance and decommissioning interventions still to be added (WP-O-02) | WP-C-03 §3; WP-C-02 §3 |
| Hazards eliminated or risks reduced to the lowest practicable | no hazard eliminated (§2); every S2 row has a step 2 measure at its PLr or is excluded; the five CFG-002 rows are open | §5 |
| Hazards introduced by the measures addressed | eight identified and allocated | §3.3 |
| Users informed and warned of the residual risks | the residual column of §5 is the content of WP-O-03 §2; WP-O-03 is a skeleton (G5) | §4; WP-O-03 |
| Protective measures compatible with each other | the stop categories and priorities are consistent (WP-C-04 §7; SR-00.02); the deceleration limit of SF-02 and SF-03 is set by the stability analysis (§3.3) | WP-C-04; WP-S-03 §4 |
| Consequences of use in a non-industrial context considered | the public floor is excluded (OL-01, DQ-019); the item is for staff who are briefed (WP-C-02 §2 people classes) | WP-C-02 §5 |
| Measures do not adversely affect the operating conditions or usability (which would invite defeat) | nuisance stops and the deactivation they invite are allocated (§3.3, MU-10); the scanner's field switching keeps docking possible without deactivation (SR-02.07) | §3.3; WP-C-06 §5 |

Residual-risk statement, per configuration:

- **CFG-001, the Gate A unit.** Inside the assessment: bench work with the wheels off the ground (H-04 bench row,
  class I under AOU-03 and SF-07). Everything else is outside it (DQ-011 C): no row with wheels on the ground is
  claimed, and the on-ground rows of §5 are the design intent for a configuration that carries the chain of
  WP-H-02. The unit's residual risk on the bench is a trapped finger or cable under a debug image, carried by the
  bench rules of WP-V-07.
- **CFG-002, the 2.0 mobile manipulator.** Every row is open: the design is not public, no safety function exists
  in a repository, and the holding, pose and force evidence is upstream's to produce (WP-S-02 OI-8). The rows say
  what the design must provide; none is claimed.
- **What the allocation claims, for any configuration that implements it.** Eleven rows rated d are class S at
  PL d or class O; no S2 row rests on information for use alone; the four D rows rest on measured or inspected
  design values that do not exist yet (Sn-07, Sn-09, Sn-12); one row is excluded. The claim of goal G0 of WP-K-01
  follows from this table once the evidence of its last column exists, and from nothing else.

## 7. Traceability

| Hazard | WP-C-03 §5 rows | Measures (§5) | Requirements | Claims (WP-K-01) | Defeaters open (WP-K-01 §7) |
|---|---|---|---|---|---|
| H-01 | 7 | DM-02, DM-08, DM-09, OL-01, OL-02, SF-01, SF-02, SF-03, SF-06, SF-09, IFU-01, IFU-02 | SR-01, SR-02, SR-03, SR-06.02, SR-09; HR-01…HR-04, HR-09 | G1.1, G1.2, G1.3, G1.6, G1.9 | DF-01, DF-02, DF-13, DF-14, DF-15, DF-16, DF-22, DF-35 |
| H-02 | 1 | DM-08, DM-10, SF-01, SF-03, SF-04, SF-05, SF-07, SF-08, IFU-01 | SR-00.02, SR-00.05, SR-04, SR-05, SR-07, SR-08 | G1.1, G1.4, G1.5, G1.7, G1.8, G3.1 | DF-01, DF-06, DF-07, DF-08, DF-27, DF-36 |
| H-03 | 1 | DM-06, DM-08, SF-03, SF-06 | SR-03, SR-06 | G1.3, G1.6 | DF-04, DF-05, DF-17, DF-24 |
| H-04 | 2 | DM-04, SF-01, SF-07, IFU-01 | SR-07; AOU-03 | G1.7, G2.1 | DF-08, DF-09 |
| H-05 | 2 | SF-01, SF-02, SF-05, SF-08, IFU-01 | SR-02.08, SR-05, SR-08; HR-06, HR-07 | G1.2, G1.5, G1.8 | DF-09, DF-10, DF-37 |
| H-06 | 1 | DM-01, DM-02, DM-03, DM-09, OL-01, OL-02, IFU-03 | SR-02.05; HR-08; AOU-06, AOU-07 | G2.2 | DF-23, DF-38 |
| H-07 | 1 | DM-04 | WP-H-05 | G2.1 | DF-19, DF-24 |
| H-08 | 1 | DM-04, DM-05 | WP-H-05 | G2.1 | DF-20 |
| H-09 | 1 | DM-06, SF-06 | SR-06.05; AOU-04 | G2.1, G1.6 | DF-20, DF-21 |
| H-10 | 1 | SF-01, SF-05, SF-08, SF-09, IFU-01 | SR-01.09, SR-00.04; HR-05, HR-07 | G1.1, G1.8, G1.9 | DF-28, DF-12, DF-38 |
| H-11 | 1 | SF-02, SF-04 | SR-02.06, SR-04 | G1.2, G1.4 | DF-03, DF-16, DF-37 |
| H-12 | 1 | DM-10, SF-03, SF-07 | SR-90; WP-C-08; AOU-05 | G3.1, G1.3 | DF-27, DF-29 |
| H-13 | 2 | SF-01, SF-02, SF-03, SF-08, SF-10, SF-11, IFU-04 | SR-10, SR-11; CA-01, CA-02, CA-06; AOU-08, AOU-10 | G1.10, G1.11 | DF-22, DF-36 |
| H-14 | 1 | DM-07, SF-01, SF-11, SF-12, IFU-04 | SR-12; CA-03; AOU-09 | G1.12 | DF-23 |
| H-15 | 2 | DM-03, DM-07, DM-09, OL-02, SF-03, SF-08, SF-10, SF-12, IFU-04 | SR-12, SR-03.06, SR-10.03; CA-04, CA-05, CA-07; AOU-08, AOU-09 | G1.12, G2.2 | DF-23 |

## 8. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | ~~Write the content~~ v0.1 written; a reviewer with operating experience confirms the allocation and the residual classes with WP-C-03 OI-5 | Reviewer | G1 |
| OI-2 | Confirm the ISO 12100 clause numbers cited in §2, §3 and §6 against a licensed copy; **unscheduled** (DQ-016 option C) | Safety manager | G1 |
| OI-3 | Carry the residual column of §5 into WP-O-03 §2 and the limits of §4 into WP-O-03 §3 when WP-O-03 is written (G5) | Safety manager | G5 |
| OI-4 | Add the maintenance and decommissioning interventions (WP-O-02) to WP-C-03 §3 and allocate them here | Safety manager | G2 |
| OI-5 | The four D rows and the S rows wait on the measurements of WP-V-02 (stopping, loaded), WP-H-08 (mass, stability) and the inspection of WP-H-05; the class is confirmed when the evidence exists | Hardware lead | G4 |
| OI-6 | CFG-002: re-allocate the five open rows when the design is public and upstream's holding, pose and force evidence exists (WP-S-02 OI-8); until then they stay O | Safety manager | when CFG-002 is public |
| OI-7 | DQ-019 (public floor): if the lead ever opens a PL e or force-limited argument, the H-01 public-floor row needs a step 1 and step 2 allocation that does not exist | Project lead | DQ-019 |
