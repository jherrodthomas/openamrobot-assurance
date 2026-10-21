# WP-S-04 Response time, stopping performance and safety distance budget

| Field | Value |
|---|---|
| Work product | WP-S-04 Response time, stopping performance and safety distance budget |
| Standard reference | Machinery: 3691-4 §4 (braking, speed, personnel detection), §5; SRP/CS: 13849-1 §5 (response time as a requirement of the safety function); Other: ISO 13855 §6 (minimum distance; approach speed K), IEC 61496-3 (AOPDLR response time, tolerance); ASPICE: SYS.3 |
| Version | 0.1 (2026-10-20): first content. Response-time budget per stop path and configuration from the datasheet values of WP-H-02 §3.2; the SF-04 target settled (200 ms at the drive, 300 ms at the contactor); stopping-distance model with planning bounds for the unmeasured coast and the braked stop; field lengths per field set from the WP-C-06 §3 formula; speed-limit consequences per zone and for the 2.0 ceiling; the parameters handed to WP-W-09; what WP-V-02, WP-V-03 and WP-V-04 measure. 0.0: skeleton |
| Status | Draft |
| PL / scope | SF-01, SF-02, SF-03, SF-04, SF-06, SF-09 on CFG-001 (bench only, DQ-011 C) and CFG-002 (unverified); SF-10, SF-11, SF-12 on CFG-002 |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | BL-001 |

> [!WARNING]
> Draft. Not one number in this document is measured on a robot. The response times are datasheet values for
> parts not yet bought (WP-H-02); the decelerations are planning bounds chosen to bracket what WP-V-02 will
> measure; every distance follows from them by arithmetic the figure generator re-checks. The budget's job until
> the measurements exist is to say which numbers matter and by how much. Clause numbers of ISO 13855, IEC 61496-3
> and ISO 3691-4 are from memory and are to be checked against licensed copies (DQ-016, answered C: unscheduled).

## 1. Purpose, inputs and conventions

Every stop function of [WP-C-04](../02-concept/WP-C-04-safety-functions-and-plr.md) ends in a standstill, and
every protective field, speed limit and workspace boundary of [WP-S-02](WP-S-02-safety-requirements.md) is a
distance that depends on how long the standstill takes. This document is the one place those numbers are
derived, so that WP-H-02 (parts), WP-W-09 (parameters), WP-V-02 (stopping tests), WP-V-03 (field validation) and
WP-V-04 (chain timing) all work from the same budget.

Inputs: the response targets and stop categories of WP-C-04 §2 and §7; the datasheet stage times of
[WP-H-02](../04-hardware/WP-H-02-electrical-and-safety-chain-design.md) §3.2; the detection-distance formula and
parameters of [WP-C-06](../02-concept/WP-C-06-human-robot-interaction-and-misuse.md) §3; the zone speeds of
[WP-C-02](../02-concept/WP-C-02-operating-environment-and-tasks.md) §2 with DQ-006 A (ceiling), DQ-017 A (speed
with a person in the zone) and DQ-018 A (reverse); the use limits of [WP-C-01](../02-concept/WP-C-01-item-definition.md)
§4.1 and §4.5; the architecture of [WP-S-03](WP-S-03-technical-safety-concept.md) §3; upstream's 2.0 stopping
model (`mass-and-stability.md`: reaction latency plus braking at the configured deceleration; results withdrawn,
rerun pending).

Conventions, as WP-S-02 §1 defines them:

| Symbol | Meaning | Measured by |
|---|---|---|
| t_r | reaction time: from the demand at the device (field violation, button, fault output, lost command) to the start of power removal or of the braking torque, at the driver input or the contactor | WP-V-04 (oscilloscope, device to contactor) |
| d_r = v·t_r | distance travelled during t_r at the speed v | arithmetic |
| a | deceleration from power removal or brake application to standstill, taken constant | WP-V-02 |
| t_b = v / a | time from power removal to standstill | WP-V-02 |
| d_b = v² / (2a) | distance from power removal to standstill | WP-V-02 |
| d_s = d_r + d_b | stopping distance, demand to standstill | WP-V-02 |
| L | minimum detection distance ahead of the robot, WP-C-06 §3: L = v·t_r + d_b + K·(t_r + t_b) + Z + C | WP-V-03 with a test piece at the field edge |
| K | approach speed of a person, 1.6 m/s (ISO 13855) | fixed by the standard |
| Z | scanner measurement tolerance plus mounting and odometry tolerance, 0.10 m | scanner datasheet (TBC) |
| C | intrusion allowance (§4.2) | to be checked |

The field is sized for the **category 0 path**: the chain removes actuator power and the robot coasts on CFG-001
(no brake, GAP-02) or is braked by the spring-applied hub-motor brakes on CFG-002 (upstream, unverified). The
controlled stop that channel 1 commands first (stop category 1, SR-02.05, SR-03.03) shortens the typical stop and
is not credited: in the single-fault case that Category 3 must survive, channel 1 has failed and the chain path
is what remains.

## 2. Response time budget per safety function

Stage values are the datasheet figures of WP-H-02 §3.2 for the candidate parts of CFG-001 (E2 Pilz PNOZ s3
drop-out ≤ 30 ms; E6 PNOZ s30 reaction ≤ 20 ms; K1/K2 Schneider LC1D09 opening ≤ 20 ms with a varistor, not a
plain diode, across the coil; E5a nanoScan3 Core 70 ms at two scans or TiM-S 100 ms, the worse taken). On
CFG-002 upstream names the same relay (PNOZ s3) and Gigavac GX11CAC contactors; their drop-out is **(TBC:
datasheet)** and the stage values are carried over as planning values. The brake engagement column is the time
from coil de-energisation to full braking torque of the ZLLG80ASM250 brakes, **(TBC: upstream has requested the
dynamic rating)**; it adds to t_r on CFG-002 only.

| SF | Path (demand → power removal) | Detection (ms) | Logic (ms) | Power removal (ms) | Brake engagement (ms, CFG-002) | t_r (ms) | Target (ms) | Requirement | Config |
|---|---|---|---|---|---|---|---|---|---|
| SF-01 | E1 contact opens → E2 → K1/K2 | 0 | 30 | 20 | **(TBC)** | 50 | 200 | SR-01.03 | both |
| SF-02 | scanner OSSD → E6 → E2 → K1/K2 | 100 | 50 | 20 | **(TBC)** | 170 | 170 | SR-02.02, SR-02.05 | both |
| SF-02 | bumper edge → monitoring unit → E6 → E2 → K1/K2 | 20 **(TBC: unit)** | 50 | 20 | **(TBC)** | 90 | 170 | SR-02.04 | both |
| SF-03 | speed above the limit for the 100 ms window → E6 → E2 → K1/K2 | 100 | 50 | 20 | **(TBC)** | 170 | 200 | SR-03.03 | both |
| SF-04 | last valid command + 200 ms → channel 1 sets PWM 0 | 200 | 2 | 0 (drive) | — | 202 | 200 at the drive | SR-04.01 | both |
| SF-04 | the same demand through channel 1's demand output → E2 → K1/K2 | 200 | 32 | 20 | **(TBC)** | 252 | 300 at the contactor | SR-04.01, SR-00.07 | both |
| SF-04 | channel 1 silent: hardware watchdog window → E6 → E2 → K1/K2 | 1000 | 50 | 20 | **(TBC)** | 1070 | 1100 | SR-04.04 | both |
| SF-06 | driver fault output → E6 → E2 → K1/K2 | 0 | 50 | 20 | **(TBC)** | 70 | 100 | SR-06.01 | both |
| SF-06 | stall or encoder loss: 1 s detector in channel 1 → PWM 0, demand → chain | 1000 | 32 | 20 | **(TBC)** | 1052 | 1100 | SR-06.02 | both |
| SF-09 | enabling signal released → E2 (teleoperation mode) → K1/K2 | 0 | 50 | 20 | **(TBC)** | 70 | 200 | SR-09.01, SR-09.02 | both |
| SF-10 | pose signal lost → safety relay → traction contactors | 0 | 50 | 20 | **(TBC)** | 70 | 200 | SR-10.02 | CFG-002 |
| SF-11 | station device (scanner field or mat) → safety controller → arm safe torque off | 100 | 50 | 20 **(TBC: STO path)** | arm joint brakes **(TBC)** | 170 | 200 | SR-11.03 | CFG-002 |
| SF-12 | keep-clear device or emergency stop → safety relay → lift actuator power | 100 | 50 | 20 | lift brake **(TBC)** | 170 | 200 | SR-12.04 | CFG-002 |

What the table settles:

- **SF-04 has two targets, not one** (WP-C-04 OI-7). The 200 ms of SR-04.01 is at the drive: channel 1 zeroes
  the PWM 202 ms after the last valid command, and that is the time the stopping distance of §3 uses. Power
  removal through the chain follows 50 ms later by the same demand (252 ms), with a target of **300 ms at the
  contactor**; the 250 ms of WP-C-04 v0.3 §7 was the drive figure applied to the contactor and is replaced.
  The third row is the fault path: channel 1 dead, no demand, the hardware watchdog of SR-04.04 trips the chain
  within 1.1 s. During that second the drives hold the last PWM only if channel 1 died with PWM applied; the
  firmware's own watchdog cannot run, so the robot travels up to v × 1.07 s before coasting: at 0.20 m/s, 0.21 m
  plus the coast. That path is why the hardware watchdog window is a parameter to shorten once the bench shows
  the control loop's real period (WP-W-09; 1 s is the first value, SR-04.04 allows "at most 1 s").
- **SF-02 by the bumper** is faster than by the scanner (90 ms) but has no distance before contact: the edge's
  overtravel must exceed the stopping distance at the reverse speed (§4.3).
- **SF-11 includes its detection device.** WP-C-04 v0.3 §7 budgets SF-11 without the station device; the row
  here adds the 100 ms of a scanner field or a mat and is inside the 200 ms target only if the safe-torque-off
  path and the joint brakes engage within the 50 ms the contactor column allows, which is **(TBC)**.
- The **stall path of SF-06** and the **fault path of SF-04** are the two stops longer than a second. Both are
  functional detectors with a chain backstop; neither sizes a field. They bound how far a faulty drive can carry
  the robot: at 0.20 m/s about 0.2 m plus the coast.

Figure 7-1 of WP-C-04 draws the demand-to-power-removal part of the first eight paths; its SF-04 and SF-11 rows
follow this table.

## 3. Stopping distance model

### 3.1 Parameters

| Parameter | CFG-001 (Gate A unit) | CFG-002 (2.0) | Status |
|---|---|---|---|
| Mass m | **(unknown)**; the motor sizing assumes 45 kg total (WP-C-01 §4.1) | to be weighed; drive pair rated for 120 kg | GAP-23; WP-H-08 |
| Wheel radius r | 0.100 m (`WHEEL_DIAMETER 0.2`) | 0.100 m (200 mm wheels) | configured |
| Drive torque at the wheel | 4.77 N·m rated per wheel (ZD 60 W through 1:25) | hub motor **(TBC)** | datasheet |
| Torque-limited deceleration a_torque | 2 × 4.77 / 0.1 / 45 ≈ **2.1 m/s²** at the rated torque and 45 kg; about twice that at peak current for seconds | **(TBC)** | arithmetic |
| Friction-limited deceleration μ·g | ≥ 4.9 m/s² for μ ≥ 0.5 (WP-C-02 §4) | the same floors | assumed |
| Tipping-limited deceleration a_tip | **(TBC: WP-H-08 §3)**; for a low base with a 0.2 m centre-of-gravity height and 0.2 m to the castor axis, of the order of 10 m/s², not the limit | **(TBC)**: with the lift at 1.7 m the centre of gravity rises and a_tip falls to a few m/s²; upstream's F2S rerun gives it | WP-H-08; upstream |
| Commanded deceleration a_cmd (stop category 1) | configured −2.5 m/s² (`nav2_params.yaml`), which the drive cannot deliver at 45 kg: the stop saturates at a_torque | upstream's "configured deceleration", value **(TBC)** | SR-02.05 bounds it by stability |
| Coasting deceleration a_coast (category 0, CFG-001) | **(TBC: WP-V-02)**; planning bounds **0.1 m/s²** (free-wheeling, rolling resistance only) and **0.5 m/s²** (gearbox drag through the 1:25 reduction); neither is measured | — (brakes fitted) | WP-V-02 ST-01 |
| Braked deceleration a_brake (category 0, CFG-002) | — | **(TBC)**; planning value **1.0 m/s²**, bounded above by μ·g and a_tip | upstream brake rating; WP-V-02 on CFG-002 |

The deceleration the budget assumes is bounded by the tip-over margin of WP-H-08: a_cmd and a_brake are taken at or
below a_tip once WP-H-08 §3 gives it, and the planning values above are provisional until then.

The three planning cases used below: **coast slow** (a = 0.1 m/s²), **coast fast** (a = 0.5 m/s²) and **braked**
(a = 1.0 m/s²). The measured value replaces them; until then, every field and limit is quoted for the worst case
that applies to the configuration.

### 3.2 Stopping distance per speed and stop path

t_r = 0.17 s is the scanner path of §2, the longest of the field-sizing paths. d_s = v·t_r + v²/(2a).

| Speed v (m/s) | Where it applies | d_r (m) | coast slow: t_b (s), d_s (m) | coast fast: t_b (s), d_s (m) | braked: t_b (s), d_s (m) |
|---|---|---|---|---|---|
| 0.05 | crawl: dock lane, reverse (DQ-018 A), thresholds | 0.009 | 0.50, 0.021 | 0.10, 0.011 | 0.05, 0.010 |
| 0.20 | navigation (Z1, Z2) | 0.034 | 2.00, 0.234 | 0.40, 0.074 | 0.20, 0.054 |
| 0.25 | channel 1 ceiling (DQ-006 A): the most a command-path failure can reach | 0.043 | 2.50, 0.355 | 0.50, 0.105 | 0.25, 0.074 |
| 0.30 | ceiling with a person in the zone and detection active (DQ-017 A); carry (CFG-002) | 0.051 | 3.00, 0.501 | 0.60, 0.141 | 0.30, 0.096 |
| 1.50 | upstream's 2.0 software ceiling, "an analytical limit" (CFG-002) | 0.255 | — (not coasting) | — | 1.50, 1.380 |

Reading it: on CFG-001 the stopping distance is the coast, and the coast is between 0.07 m and 0.23 m from
navigation speed, a factor of three that only the measurement removes. On CFG-002 at 1.5 m/s even a braked stop
at 1 m/s² travels 1.4 m; at 2 m/s² (if the brake and the tipping margin allow it) 0.8 m. Upstream's requirement
that obstacle detection "reach at least 0.9 m ahead" at that speed is a functional-sensing figure and is below
the stopping distance of the braked case; it is not a safety distance (§4.4).

## 4. Safety distances and protective fields

### 4.1 Field length per field set

L = v·t_r + d_b + K·(t_r + t_b) + Z + C with K = 1.6 m/s, t_r = 0.17 s, Z = 0.10 m and, in this version, C = 0
(§4.2). The field sets are the ones E6 selects from the speed-limit input (WP-H-02 §3.3; SR-02.02, SR-02.10) and
WP-W-09 configures. Each planning case is a row; the figure generator recomputes every number from the formula.

| ID | Field set | v (m/s) | Case | a (m/s²) | t_b (s) | d_s (m) | L (m) | Config |
|---|---|---|---|---|---|---|---|---|
| FS-1a | navigation | 0.20 | coast slow | 0.1 | 2.00 | 0.234 | 3.81 | CFG-001 |
| FS-1b | navigation | 0.20 | coast fast | 0.5 | 0.40 | 0.074 | 1.09 | CFG-001 |
| FS-1c | navigation | 0.20 | braked | 1.0 | 0.20 | 0.054 | 0.75 | CFG-002 |
| FS-2a | crawl: dock lane, thresholds | 0.05 | coast slow | 0.1 | 0.50 | 0.021 | 1.19 | CFG-001 |
| FS-2b | crawl: dock lane, thresholds | 0.05 | coast fast | 0.5 | 0.10 | 0.011 | 0.54 | CFG-001 |
| FS-2c | crawl: dock lane, thresholds | 0.05 | braked | 1.0 | 0.05 | 0.010 | 0.46 | CFG-002 |
| FS-3a | person in the zone, detection active | 0.30 | coast slow | 0.1 | 3.00 | 0.501 | 5.67 | CFG-001 |
| FS-3b | person in the zone, detection active | 0.30 | coast fast | 0.5 | 0.60 | 0.141 | 1.47 | CFG-001 |
| FS-3c | person in the zone, detection active | 0.30 | braked | 1.0 | 0.30 | 0.096 | 0.95 | CFG-002 |
| FS-4 | carry pose (T-11), carry footprint | 0.30 | braked | 1.0 | 0.30 | 0.096 | 0.95 | CFG-002 |
| CK-1a | channel 1 ceiling, not a field set | 0.25 | coast slow | 0.1 | 2.50 | 0.355 | 4.73 | CFG-001 |
| CK-1b | channel 1 ceiling, not a field set | 0.25 | coast fast | 0.5 | 0.50 | 0.105 | 1.28 | CFG-001 |
| CK-2a | 2.0 software ceiling, not a field set | 1.50 | braked | 1.0 | 1.50 | 1.380 | 4.15 | CFG-002 |
| CK-2b | 2.0 software ceiling, not a field set | 1.50 | braked at 2.0 | 2.0 | 0.75 | 0.818 | 2.39 | CFG-002 |

What the table says:

- **The person's walk dominates.** In FS-1a the robot itself travels 0.23 m and the person 3.5 m. A coasting stop
  costs 1.6 m of field per second of coast, which is why a brake on the drive (DM-09) is worth more to SF-02 than
  any reduction of speed, and why the coast measurement (WP-V-02 ST-01) is the first on-ground test.
- **The 1.0 m starting field of WP-H-02 §3.3 holds only for the coast-fast case, and not quite** (1.09 m). With
  the nanoScan3 Core's 3 m protective field the navigation set can be 3.8 m long if the coast is slow, but an
  aisle rarely gives 3.8 m of clear floor ahead: the slow-coast case means the navigation speed comes down, or
  the drive gets a brake. The TiM-S (2 m) covers only the coast-fast case.
- **The crawl set** is 0.5 to 1.2 m long, almost all of it the person's walk during t_r and the short coast. The
  dock lane needs that much clear ahead of the robot during the approach, which is a lane-length requirement for
  WP-O-01, or the dock approach's last metre is accepted blind under the bumper and the lane marking (WP-C-05
  §5, H-01 dock lane).
- **The 0.3 m/s ceiling with a person in the zone** (FS-3) needs 1.5 m of field on a fast coast and 5.7 m on a
  slow one: on CFG-001 the ceiling is usable only with a measured fast coast; on CFG-002 it needs 0.95 m braked.
- **FS-4 carry** equals FS-3c in length but is sized on the carry footprint, which includes the arms in the carry
  pose and the sweep of a turn (CA-07, SR-02.10); its width, not its length, is the new term.

![Figure 4-1: line chart of the minimum detection distance L in metres against the robot speed from 0 to 1.6 m/s, four curves for the planning decelerations 0.1, 0.5, 1.0 and 2.0 m/s², horizontal lines at the 1 m starting field and the 2 m and 3 m protective-field ranges of the candidate scanners, vertical markers at the crawl, navigation, ceiling and person-in-zone speeds and at the 2.0 software ceiling, and a dot on each table row](figures/fig-s04-4-1-field-length-vs-speed.svg)

*Figure 4-1.* The §4.1 table as curves: field length against speed for the four planning decelerations. The gap between the 0.1 and 0.5 m/s² curves at 0.20 m/s is the price of not having measured the coast; the 2.0 ceiling at 1.5 m/s needs 2.4 m of field even braked at 2 m/s². Generated by [`figures/fig_s04.py`](figures/fig_s04.py) from the §3.1 and §4.1 tables; CI fails if a table value disagrees with the formula or the figure is stale.

### 4.2 The intrusion allowance C

ISO 13855 §6 (to be checked) gives, for a horizontal field detecting a person approaching a fixed hazard,
C = 1200 − 0.4·H mm with a floor of 850 mm, H the field height above the floor: at the 0.18 to 0.22 m scan
plane of the candidate scanners that is about 1.1 m. The term exists because a person can reach over or step
into a fixed field before being detected; for a mobile platform whose field moves with it, ISO 3691-4 (to be
checked) sizes the field on the stopping distance plus tolerances and sets the scan-plane height so that a
standing or walking person's legs are detected, and the approach term is K·T. This document takes **C = 0 as the
planning value** with the conditions that make it defensible: scan plane ≤ 0.2 m, detection resolution 70 mm
(leg), the field width covering the footprint plus Z plus the lateral sway on each side (SR-02.02), and the
below-plane case closed separately by SR-02.03 (0.3 m detection height, **(TBC)**). The assessor's reading of the
two standards may add C back; the figure shows what that costs (the WP-C-06 §3 band). This is a technical
interpretation (`decider: claude`), reversible, recorded as OI-3; it is not put to the lead.

### 4.3 Reverse and the bumper

Reverse is permitted only at the crawl limit (DQ-018 A) and is covered by the rear bumper (E5b), which detects by
contact. The condition is that the edge's overtravel exceeds the stopping distance on the bumper path of §2
(t_r = 0.09 s) at 0.05 m/s: d_s = 0.0045 m + d_b, that is **16 mm** on the slow coast and **6 mm** on the fast
one. A pressure-sensitive edge of the Mayser SL/BK class has an overtravel of about 20 to 40 mm **(TBC:
datasheet)**, so the margin holds at the crawl speed and fails above about 0.1 m/s on a slow coast: the speed
monitor's direction-and-speed rule (SR-03.02) is what keeps the bumper adequate, and the undock speed of
0.05 m/s is a safety parameter, not a tuning value.

### 4.4 The 2.0 configuration at its ceiling

Rows CK-2a and CK-2b are why the 2.0 ceiling of 1.5 m/s cannot be the operating speed: the field would have to
be 2.4 to 4.2 m long, beyond the 3 m protective range of the nanoScan3 Core on the slow side and beyond any
aisle on both. The speed a given field allows, with the braked planning decelerations:

| Protective field available | a = 0.5 m/s² | a = 1.0 m/s² | a = 2.0 m/s² |
|---|---|---|---|
| 1.0 m | 0.18 m/s | 0.32 m/s | 0.57 m/s |
| 2.0 m (TiM-S) | 0.43 m/s | 0.76 m/s | 1.27 m/s |
| 3.0 m (nanoScan3 Core) | 0.65 m/s | 1.13 m/s | 1.84 m/s |

The accepted operating speed of CFG-002 is therefore set by the measured braked deceleration (bounded by the
tipping margin with the lift extended, WP-H-08) and by the field the sites allow, not by the software ceiling;
0.3 m/s (the carry and person-in-zone value) needs about 1 m of field braked, which any of the candidate
scanners provides.

### 4.5 The arm workspace and the lift (CFG-002)

SR-11.02 sizes the station workspace as the arm's reach plus K·(t_r + t_b) of the arm. With the SF-11 row of §2
(t_r = 0.17 s) and the arm's stopping time unknown: the walk term is 0.32 m at 0.2 s total, 0.48 m at 0.3 s and
0.80 m at 0.5 s. The reach of the OpenArm 2.0 is about 0.6 m shoulder to fingertip as a planning value read from the description
package's joint offsets (`assurance/sim/blender`), so the boundary is about 1.1 m from the shoulder at a 0.3 s stop;
the stopping time is **(TBC: WP-C-01 OI-6)** and until it exists the boundary is provisional and AOU-10 holds. The lift moves at 18 mm/s: a stop within the 200 ms of
SR-12.04 travels 3.6 mm after the demand, so the keep-clear detection, not the lift's speed, sets the hazard.

## 5. Speed limits per zone

The limits of WP-C-02 §2 with what this budget says about each. The development limits of WP-V-07 §3 stay in
force until WP-V-02 measures the coast; they are not relaxed by this document (WP-V-07 OI-3).

| Zone | Limit (WP-C-02) | Budget consequence | Field set |
|---|---|---|---|
| Z1 test area | 0.20 m/s forward, 0.05 m/s reverse, 0.5 rad/s | FS-1 and FS-2 apply; with nobody in the path (AOU-02) the field is a backstop, not the measure | FS-1, FS-2 |
| Z2 transport aisle | 0.20 m/s; 0.30 m/s ceiling with a person in the zone and detection active, 0 without (DQ-017 A) | 0.20 m/s needs 1.1 to 3.8 m of field on CFG-001 (coast unmeasured) and 0.75 m on CFG-002; the 0.30 m/s ceiling needs 1.5 m on a fast coast and is not usable on a slow one; a blind corner cannot be covered by field length at any of these speeds (WP-C-06 §3), it is a site measure (IFU-02) | FS-1, FS-3 |
| Z3 dock lane | 0.05 m/s crawl **(TBC)**; reverse only here | FS-2 is 0.5 to 1.2 m long: the lane must be that clear ahead during the approach, or the last metre is accepted blind under the bumper (WP-C-05 §5); reverse at 0.05 m/s is inside the bumper's overtravel (§4.3) | FS-2; bumper |
| Z4 charging bay | 0 | no motion; the chain is open while charging | — |
| Z5 public floor | excluded (DQ-019); 0.3 m/s with detection, else 0, if ever opened | as Z2 at 0.30 m/s plus the below-plane case of a child (SR-02.03), which no field length covers | — |
| Channel 1 ceiling | 0.25 m/s, 0.6 rad/s (DQ-006 A) | the most a failed command path can reach before SF-03 trips: 0.36 m coasting slow, 0.11 m fast (CK-1); 25 % above the navigation limit, which the speed-monitor window of 100 ms detects before the ceiling is reached from 0.20 m/s at the configured 0.5 m/s² acceleration (0.1 s × 0.5 m/s² = 0.05 m/s) | — |
| CFG-002 ceiling | 1.5 m/s (upstream, analytical) | not an operating speed (§4.4); the accepted speed follows the brake measurement and the field the site allows | — |

Speed-monitor trip thresholds (channel 2, E6) are set above the zone limit by the measurement tolerance of the
pulse input, with the 100 ms window of SR-03.03: proposed **limit + 15 %** (0.23 m/s for the navigation set,
0.0575 m/s for the crawl set, 0.345 m/s for the 0.30 m/s sets) until the pulse resolution of `SPD/DO2` is known
(WP-H-02 OI-1). A threshold closer to the limit trips on the drive's own overshoot; one further above it extends
CK-1. The values are parameters (§7), not design constants.

## 6. Verification: what is measured, where

| What | Test | Work product | Evidence (WP-K-01) |
|---|---|---|---|
| t_r of every path in §2 at the contactor and at the driver input, each device, each channel | oscilloscope from the device contact or OSSD to the K1/K2 auxiliary contact; 10 repetitions; worst case against the target | WP-V-04 (chain), WP-V-05 (channel 1 paths) | Sn-08 |
| a_coast, t_b, d_s from 0.05, 0.20, 0.25 and 0.30 m/s, loaded and unloaded, on the worst floor in use, forward and reverse; the controlled stop at a_cmd for comparison | marked floor and video, encoder log, 5 repetitions per point; the measured a replaces the planning cases of §3.1 and the table of §3.2 | WP-V-02 ST-01…ST-04 | Sn-07 |
| a_brake on CFG-002, lift retracted and extended, carry load | the same, with the tipping margin of WP-H-08 as the ceiling | WP-V-02 on CFG-002 | Sn-07, Sn-09 |
| L of every field set with a test piece at the field edge (IEC 61496-3 test piece, 70 mm), at the set's speed, stop before contact | WP-V-03 field validation; the measured d_s of WP-V-02 as the input | WP-V-03 | Sn-11 |
| bumper overtravel against d_s at 0.05 m/s reverse | reverse into the bumper on the worst floor, loaded | WP-V-03 | Sn-11 |
| speed-monitor thresholds and the 100 ms window | forced command above the limit on channel 1; channel 2 trips inside the window | WP-V-05 | Sn-10 |
| the SF-04 fault path: channel 1 held in reset, hardware watchdog trips the chain within 1.1 s | fault injection | WP-V-05 | Sn-10 |

## 7. Parameters handed to WP-W-09

Each becomes a PAR entry with this document as its source; the value column is the planning value until the
measurement named in §6 replaces it.

| Parameter | Value | Unit | Set by | Replaced by |
|---|---|---|---|---|
| navigation speed limit (Z1, Z2) | 0.20 | m/s | WP-C-02 §2 | — |
| crawl limit (Z3, reverse, thresholds) | 0.05 | m/s | DQ-018 A; WP-C-02 **(TBC)** | — |
| ceiling with a person in the zone and detection active | 0.30 | m/s | DQ-017 A | — |
| carry limit (CFG-002) | 0.30 | m/s | upstream `LIFT`, CA-07 **(TBC)** | WP-H-08 |
| channel 1 command ceiling | 0.25 linear, 0.6 angular | m/s, rad/s | DQ-006 A | — |
| speed-monitor trip thresholds | limit + 15 % | m/s | §5 | WP-H-02 OI-1 (pulse resolution) |
| speed-monitor window | 100 | ms | SR-03.03 | — |
| command watchdog | 200 | ms | SR-04.01 | — |
| hardware watchdog window | 1000 (at most) | ms | SR-04.04 | bench measurement of the loop period |
| standstill time-out before power removal (stop category 1) | 1 | s | SR-02.05, SR-03.03 **(TBC)** | WP-V-02 (t_b measured) |
| commanded deceleration a_cmd | ≤ min(a_torque, a_tip); −2.5 m/s² as configured is above a_torque | m/s² | §3.1 | WP-H-08 |
| field set lengths FS-1…FS-4 | §4.1, worst applicable case | m | §4.1 | WP-V-02 then WP-V-03 |
| field width margin per side | Z + lateral sway **(TBC)** | m | SR-02.02 | WP-V-03 |
| scanner tolerance Z | 0.10 | m | §1 | scanner datasheet |
| intrusion allowance C | 0 (planning, §4.2) | m | §4.2 | assessor's reading (OI-3) |
| warning time before motion | 2 **(TBC)** | s | SR-08.01 | WP-V-04 |
| stall detector | 60 % PWM, 2 rpm, 1 s | — | DQ-008 A | WP-W-08 bench |

## 8. Traceability

| Requirement | Budget row or section | Verified by |
|---|---|---|
| SR-01.03 | §2 SF-01 | WP-V-04 |
| SR-02.02, SR-02.10 | §4.1 FS-1…FS-4; §4.2 | WP-V-03 |
| SR-02.03 | §4.2 (below-plane case, outside the formula) | WP-V-03 |
| SR-02.04 | §4.3 | WP-V-03 |
| SR-02.05, SR-03.03 | §2 SF-02, SF-03; §3.1 a_cmd; §7 standstill time-out | WP-V-02, WP-V-05 |
| SR-03.02, SR-03.04 | §5 | WP-V-05 |
| SR-04.01, SR-04.04, SR-00.07 | §2 SF-04 three paths | WP-V-05 |
| SR-06.01, SR-06.02 | §2 SF-06 | WP-V-05 |
| SR-09.01, SR-09.02 | §2 SF-09 | WP-V-05 |
| SR-10.02 | §2 SF-10 | WP-V-05 (CFG-002) |
| SR-11.02, SR-11.03 | §2 SF-11; §4.5 | WP-V-03, WP-V-05 (CFG-002) |
| SR-12.04 | §2 SF-12; §4.5 | WP-V-05 (CFG-002) |
| WP-C-04 §7 | §2 (SF-04 targets, SF-11 detection stage) | — |
| WP-H-08 §3 | §3.1 a_tip, a_cmd | WP-V-02 |

## 9. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | ~~Write the content~~ v0.1 written; the hardware lead confirms the stage values of §2 against the datasheets of the parts bought (WP-H-02 OI-1 for the pulse input) | Hardware lead | G2 |
| OI-2 | Measure a_coast on the Gate A unit (WP-V-02 ST-01; WP-C-01 OI-2) and replace the planning cases of §3.1; every table of §3 and §4 is recomputed | Hardware lead | G4 |
| OI-3 | The intrusion allowance C: confirm the planning value 0 against licensed ISO 13855 and ISO 3691-4 (§4.2); **unscheduled** with DQ-016 C; if C returns, FS-1 grows by up to 1.1 m | Safety manager | with the assessor |
| OI-4 | CFG-002: the brake engagement time and dynamic rating, the contactor drop-out, the arm's reach and stopping time, the lift brake (§2, §4.5); all upstream's to publish (WP-S-02 OI-8) | Safety manager | when CFG-002 is public |
| OI-5 | WP-H-08: the tipping-limited deceleration for both configurations, the lift extended; until then a_cmd stays at the torque limit and the configured −2.5 m/s² is unreachable | Hardware lead | G2 |
| OI-6 | Carry the §7 table into WP-W-09 as PAR entries when it is written | Software lead | G3 |
| OI-7 | Update WP-H-02 §3.3 (field start value 1.0 m) to the field-set table of §4.1 and its worst applicable case | Hardware lead | G2 |
