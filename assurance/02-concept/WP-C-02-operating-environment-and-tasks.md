# WP-C-02 Operating environment and task specification

| Field | Value |
|---|---|
| Work product | WP-C-02 Operating environment and task specification (zones, floors, people, lighting) |
| Standard reference | Machinery: 3691-4 §4, §6; 12100 §5.3; Other: ISO 21448 §5 (informative method); ASPICE: SYS.1 |
| Version | 0.2 (2026-10-20): DQ-004 B and DQ-020 A applied: tasks T-09…T-11 of the arms and lift on CFG-002; T-06 names SF-09; the status column distinguishes the configurations. 0.1: zones Z0–Z5, tasks T-01–T-08, environmental limits, exclusions, the development test area; Figures 2-1 and 3-1. 0.0: skeleton |
| Status | Draft |
| PL / scope | PL d target (DQ-005); CFG-001 Gate A unit (bench only, DQ-011 C) and CFG-002 2.0 mobile manipulator (unverified); the base with the arms and lift (DQ-004 B) |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1; someone who has operated the robot on a real floor) |
| Approver | Safety manager |
| Baseline | BL-001 |

> [!WARNING]
> Draft. Upstream publishes no operating-environment specification: its documentation pages on zones, speed limits
> and working around robots are unfilled templates, and the only environment statements in its record are "flat
> indoor floors", "thresholds and cable covers at crawl speed" and "the 35 mm castor wheels stop on small steps"
> (2.0 mass-and-stability page). Every numeric limit below marked **(TBC)** is a proposal for the lead or a value
> the tests of WP-V-02 and WP-V-03 must set. Nothing here has been walked on a real site with the robot.

## 1. Purpose

Specifies the operating environment and the tasks the robot performs in it: zones, floors, slopes, lighting,
obstacles, people presence per zone and per task. It is the machinery analogue of an operational design domain and
the source of every operating-environment limit the safety case relies on. The risk assessment
([WP-C-03](WP-C-03-risk-assessment.md)) rates its situations OS-01…OS-12 against these zones and tasks; the
information for use ([WP-O-03](../09-production-operation/WP-O-03-information-for-use.md)) carries the exclusions of
§5 to the operator; the test procedure ([WP-V-07](../06-validation/WP-V-07-test-operations.md)) uses the test
area of §6 as its condition C-7.

People presence per zone is an input to the misuse analysis of WP-C-06.

## 2. Zones

A zone is a floor area with one set of environmental properties, one people-presence class and one speed limit. The
site owner marks zones on the floor and in the map; the robot's zone-dependent limits are safety parameters
(WP-S-02 SR-00.05) selected through the safety controller, never through the ROS 2 stack alone.

People-presence classes: **none** (the zone is empty of people while the robot moves; entry stops the robot or is
prevented), **briefed** (trained staff who know the robot, its stop devices and its blind zones), **public**
(anyone, including children and visitors).

| Zone | Name | Floor and slope | Obstacles, steps, drops | Lighting and reflectivity | People | Speed limit | Detection needed | Status at BL-001 |
|---|---|---|---|---|---|---|---|---|
| Z0 | Excluded | anything in §5 | | | | 0 | | robot must not enter; no geofence exists today (map limits only) |
| Z1 | Development test area (§6) | level, dry, sealed concrete, epoxy or vinyl; slope ≤ 1 % **(TBC)**; no threshold | marked boundary; no fixed obstacles inside except test props; no steps, drops or edges within 2 m of the boundary | ≥ 200 lx diffuse **(TBC)**; no glass or mirror walls inside the LiDAR range; matte test props | none: operator with the stop pendant and one observer, both outside the robot's path (WP-V-07) | 0.20 m/s forward, 0.05 m/s reverse, 0.5 rad/s | none claimed; the operator is the protective measure | the only zone; after DQ-011 C (2026-10-20) no on-ground run on CFG-001, so bench work only until the 2.0 base with its chain exists |
| Z2 | Transport aisle | level indoor floor; slope ≤ 2 % **(TBC)**; thresholds and cable covers ≤ 10 mm **(TBC)**, crossed at the crawl limit | fixed racks, pallets, parked carts; no loading-dock edges, no stairs or pits without a barrier; aisle width ≥ footprint + 2 × 0.5 m **(TBC)** | ≥ 100 lx **(TBC)**; no glass partitions or mirrors facing the aisle at LiDAR height; no direct low sun on the dock tags | briefed; public only when SF-02 is validated for public contact | 0.20 m/s navigation; DQ-017 sets the limit when a person is inside the protective field's warning zone | SF-02 (front scanner) and SF-03 at PL d | **not permitted**: no protective stop exists (GAP-14, GAP-22) |
| Z3 | Dock lane | as Z2, plus the dock's approach surface level to ± 5 mm over the last 1 m **(TBC)** | the dock itself; nothing else within the lane; lane marked on the floor (length of the pre-dock approach, 2 m, plus the robot's length) | tags well lit, no glare, matte print (upstream `04_apriltag.md`) | none while a dock or undock runs; entry aborts the manoeuvre | crawl: 0.05 m/s **(TBC)**; reverse only here | SF-02 dock-lane field set; rear bumper for undock | not permitted with people in the lane: docking bypasses every reactive layer (GAP-15, GAP-35) |
| Z4 | Charging and parking bay | as Z2 | the charger and its cable; the mains inlet | — | briefed technician only during connection | 0: the robot is stopped and, when charging, the safety chain is open (upstream 2.0 charge interlock) | none (robot stopped); electrical safety DM-04, DM-05 | mains and battery are paralleled today (GAP-20); charging is a manual bench procedure |
| Z5 | Shared public floor (showroom, office corridor, visitor route) | as Z2 | people, doors, furniture that moves | — | public | **(TBC)**: the lower of walking pace and DQ-017; zero where children are present | SF-02 validated for public contact, SF-03, audible and visual warning | **excluded** until SF-02 is validated and WP-C-06 covers public misuse |

![Figure 2-1: schematic site plan with the five zones: the development test area Z1, the transport aisle Z2, the dock lane Z3 with the dock at its end, the charging bay Z4, the shared public floor Z5 hatched as excluded, and the excluded surroundings Z0; each zone labelled with its people class and speed limit, and the robot's footprint with the front scanner field and the rear bumper drawn to scale in Z1](figures/fig-c02-2-1-zones.svg)

*Figure 2-1.* The zones of the table as a schematic plan. Z1 is the only zone the robot may run in at BL-001; Z2, Z3 and Z4 need the safety functions named in the table; Z5 and Z0 are excluded. The robot, the 1.0 m starting protective field of WP-H-02 §3.3 and the rear bumper are drawn to scale against a 1 m grid. Generated by [`figures/fig_c02.py`](figures/fig_c02.py) from the §2 and §3 tables; CI fails if it is stale.

## 3. Tasks

| Task | What the robot does | Zone | Mode (WP-C-01 §5) | Speed | People during the task | Protective function needed | Status at BL-001 |
|---|---|---|---|---|---|---|---|
| T-01 | Transport leg: drive from one goal pose to another along the planned path, avoiding seen obstacles | Z2 (Z1 in development) | M3 | 0.20 m/s | briefed (Z2); none (Z1) | SF-02, SF-03 | Z1 only, under WP-V-07 |
| T-02 | Wait: stand at a goal or a waypoint with the stack running | Z2, Z1 | M3 (idle) | 0 | briefed | SF-05 (no unexpected start-up) | nothing prevents a restart on the next command |
| T-03 | Docking approach: drive to the pre-dock pose, align on the tags, push onto the dock | Z3 | M4 | crawl 0.05 m/s **(TBC)**; today the sequencer's `drive_speed` is unbounded | none | SF-02 dock-lane field, SF-03 crawl limit | not permitted with people present |
| T-04 | Undocking: reverse 0.7 m straight back, then turn | Z3 | M4 | 0.05 m/s **(TBC)**; today 0.10 m/s blind | none | rear bumper, SF-03 reverse limit (DQ-018) | not permitted with people present |
| T-05 | Charging: stopped in the bay, connected to the charger | Z4 | M0 | 0 | briefed technician | safety chain open while charging (interlock) | manual; battery and mains paralleled (GAP-20) |
| T-06 | Manual recovery and teleoperation: an operator drives the robot out of a stuck state or to a safe place | Z1, Z2 | M2 | 0.20 m/s; **(TBC)** 0.10 m/s when a person is within 2 m | briefed; the operator watches the robot, not the screen | SF-01 within reach, SF-03, SF-09 (enabling control, WP-C-04 §3.9) | no deadman; teleop bypasses the smoother and the monitor |
| T-07 | Mapping: teleoperation while SLAM runs | Z1, Z2 (empty) | M5 | as T-06 | none or briefed | as T-06 | as T-06 |
| T-08 | Bench, calibration and powered debug: wheels off the ground | bench (not a zone) | M1 | n/a | technician | SF-07 arming, AOU-03 | the per-boot calibration needs the powered path; on CFG-001 the only permitted powered activity (DQ-011 C) |
| T-09 | Manipulation at a station: an arm picks, places, pulls a drawer or door (≤ 150 N) or hands over an item, with the base stopped (CFG-002) | Z2 (at a marked station) | M7 | base 0; arm speed **(TBC)** | briefed; outside arm reach until power-and-force limiting is proven (AOU-10) | SF-10 (base inhibited while an arm is unstowed), SF-11 (arm safe stop and force limit), SF-01 | CFG-002 only: no arm exists on CFG-001; nothing upstream names an arm safety function |
| T-10 | Lift raising or lowering the arms and their load between the calibrated stops, arms in the stowed or carry pose, base stopped (CFG-002) | Z2 (at a station) | M8 | 18 mm/s | briefed; clear of the column and of the space under the arms | SF-12 (lift holding and interlock), SF-01 | CFG-002 only: the DOLD holding evidence is an upstream release gate not yet passed |
| T-11 | Carrying: a transport leg with a load held in the arms in the carry pose (CFG-002) | Z2 | M9 | ≤ 0.3 m/s (upstream hold-and-move limit) **(TBC)** | briefed | SF-02, SF-03 with the carry limit, SF-10 | CFG-002 only: the raised centre of gravity and the wider footprint wait on the F2S rerun |

![Figure 3-1: task-by-zone matrix: tasks T-01 to T-08 down the side, zones Z1 to Z5 across, each cell coloured by whether the task is permitted in that zone at BL-001, permitted once the named safety functions exist, or excluded, with the speed limit written in the cell](figures/fig-c02-3-1-task-zone-matrix.svg)

*Figure 3-1.* Where each task may run, now and once the safety functions exist. The one green cell, bench work with the wheels off the ground, is all that is inside the case at BL-001: since DQ-011 C no drive task runs on CFG-001, so every other test-area cell waits for the 2.0 base with its chain. Amber cells open when the named safety function is validated; grey cells are excluded. T-09 to T-11 exist only on CFG-002. Generated by [`figures/fig_c02.py`](figures/fig_c02.py) from the §3 table; CI fails if it is stale.

## 4. Environmental limits

| Limit | Value | Basis | Consequence of exceeding |
|---|---|---|---|
| Ambient temperature | 5 to 35 °C **(TBC)** | the Pi 5 throttles at ≈ 83 °C with no cooler (hw README); lead-acid capacity falls below 5 °C; no datasheet range for the ZBLD drivers in the record | compute stalls → watchdog stop; battery rule (AOU-04) fails earlier |
| Humidity | non-condensing, ≤ 80 % RH **(TBC)** | motors IP20, open electronics bracket | electrical fault (H-07) |
| Dust, water | dry indoor only; no washdown, no spills on the path | IP20 motors, no robot-level IP rating | wheel slip, electrical fault |
| Floor friction | sealed dry floor, μ ≥ 0.5 **(TBC)**; stopping-distance tests on the worst floor in use | stopping distance and the stick-slip floors were measured on one floor only (upstream 2026-07-02) | SF-02 field sized for a shorter stop than achieved |
| Floor loading | robot mass **(unknown)** plus payload limit (WP-H-08) | — | — |
| Slope | ≤ 1 % (Z1), ≤ 2 % (Z2) **(TBC)**; ramps excluded | no holding brake: a coasting stop on a slope rolls (H-06); castor wheels 35 mm | roll-away after a category 0 stop |
| Steps and thresholds | ≤ 10 mm **(TBC)**, crossed at the crawl limit; nothing higher | "the 35 mm castor wheels stop on small steps" (upstream) | stuck robot, tipping of a high payload |
| Drops and edges | none within the mapped area without a physical barrier | no cliff sensing on the Gate A unit (the 2.0 TF-Luna cliff sensors are "not a safety device") | fall |
| Lighting | ≥ 100 lx in aisles, ≥ 200 lx diffuse at the dock **(TBC)**; no glare on the tags | AprilTag detection; LiDAR is independent of lighting | docking aborts or goes blind (GAP-15) |
| Reflectivity and transparency | no glass partitions, mirrors or polished metal at LiDAR height (0.18 m) along the path; no retro-reflective floor markings in the dock lane | 2D LiDAR; the body filter already masks self-reflections | phantom or missing obstacles in the costmap |
| Electromagnetic environment | industrial environment per EN 61000-6-2 **(assumed, not tested)**; no welding or large VFDs within 5 m of the dock | not assessed (GAP, WP-H-05) | sensor or serial-link errors → stops |
| Wi-Fi coverage | continuous coverage of every zone the robot enters, verified by a site survey; dead zones are Z0 | loss of the agent is a stop (SF-04) and today a silent one (GAP-37) | unexpected stops in the aisle; the on-screen stop does nothing |
| Acoustic | — | no audible warning exists | people are not warned of an approaching robot (WP-C-06) |

## 5. What is outside the environment

Each exclusion becomes an operating limit in WP-O-03 §3 and a marking where it applies.

| Exclusion | Why |
|---|---|
| Outdoor use, wet or icy floors, rain | no IP rating; LiDAR and friction assumptions fail |
| Slopes above the zone limit; ramps; loading docks; lifts and elevators | no brake; coasting stop; tipping; unknown drop edges |
| Stairs, pits, dock edges, platforms without a fixed barrier | no cliff sensing; a fall is unrecoverable |
| Glass walls, mirrors, polished metal along the path at LiDAR height | 2D LiDAR phantom or missing returns |
| Crowds, public areas, children, animals | no protective stop; even with SF-02 the field sizing assumes an adult walking pace |
| Aisles shared with forklifts or other vehicles without physical separation | the robot has no means to detect or yield to a fast vehicle |
| Automatic doors, fire doors, turnstiles unless interlocked with the robot's stop | closing door on the robot; robot blocking an escape route |
| Carrying a person, towing, pushing carts, any payload above the WP-H-08 limit or above the top plate's height limit | stability unknown |
| Areas without Wi-Fi coverage; areas without a marked E-stop within reach | loss of the agent is a silent stop; no reachable stop |
| Any operation with the arms or lift fitted | second item (DQ-004) |

## 6. Test area during development

The first defined zone is Z1, the area [WP-V-07](../06-validation/WP-V-07-test-operations.md) condition C-7 requires:

- at least 6 m × 6 m of level, dry, sealed floor **(TBC)**, with 2 m of clear floor beyond the marked boundary on
  every side and no step, drop or edge within that margin;
- boundary marked on the floor; the dock, if used, at one end with its 2 m lane marked;
- no glass or mirror within the LiDAR range (12 m for the A1) at 0.18 m height, or masked by a solid barrier;
- lighting ≥ 200 lx diffuse at the dock tags, no direct glare;
- Wi-Fi coverage verified at every corner before each session (WP-V-07 §4);
- nobody inside except the operator holding the stop pendant and one observer, both outside the robot's path and
  never behind a reversing robot;
- the test props (obstacles, person-simulating test piece of WP-V-03) are matte and of known size.

Until the safety chain of WP-H-02 is fitted and validated, Z1 is the whole operating environment of the Gate A unit.

## 7. Traceability

| This document | Used by |
|---|---|
| Zones Z0–Z5, people classes | WP-C-03 situations OS-01 (Z2, Z5), OS-02 (Z1), OS-03 (Z3), OS-07 (Z4); WP-C-06 misuse per people class; WP-O-03 §3 limits and §4 markings |
| Tasks T-01–T-11 | WP-C-03 situations OS-01…OS-18; WP-C-04 safety functions per task; WP-V-01 validation scenarios |
| Environmental limits §4 | WP-C-01 §4.4 (other limits, replaces its placeholders); WP-H-05 (electrical), WP-H-08 (stability); WP-V-02 test conditions |
| Exclusions §5 | WP-O-03 §3; AOU-02, AOU-05, AOU-06 of WP-C-01 §8 |
| Test area §6 | WP-V-07 C-7; `06-validation/test-sites/` site records |

## 8. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Set every **(TBC)** value: slopes, thresholds, lighting, friction, temperature, aisle width, test-area size; from the stopping and stability tests (WP-V-02) and a site walk | Safety manager | G1 |
| OI-2 | Lead decision DQ-017 (speed when a person is in the zone) and DQ-018 (reverse motion) | Project lead | G1 |
| OI-3 | A geofence or map-based exclusion that keeps the robot out of Z0 without relying on the planner alone | Software lead | G2 |
| OI-4 | Audible and visual warning for Z2 and Z5 (ISO 3691-4 expects a warning device) | Hardware lead | G2 |
| OI-5 | Site survey template for Wi-Fi coverage and lighting, filed under `06-validation/test-sites/` | Safety manager | G1 |
| OI-6 | Reviewer with floor experience confirms the zone table against a real SME floor | Reviewer | G1 |
