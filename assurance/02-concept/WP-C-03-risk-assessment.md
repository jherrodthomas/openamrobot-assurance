# WP-C-03 Risk Assessment and Required Performance Levels

| Field | Value |
|---|---|
| Work product | WP-C-03 Risk assessment (ISO 12100) and determination of the required Performance Level per safety function (ISO 13849-1) |
| Standard reference | ISO 12100:2010 §5.4–§5.6, Annex B; ISO 13849-1:2023 §5, Annex A (risk graph); ISO 3691-4:2023 §4, Annex A; ISO 13850:2015; EN 60204-1:2018 §9.2.2 (stop categories); Regulation (EU) 2023/1230 Annex III §1.1.2 |
| Version | 0.5 (2026-10-20): DQ-017 A, DQ-018 A and DQ-021 A applied in OL-02 and H-13. 0.4 (2026-10-20): DQ-004 B and DQ-020 A applied: the arms and lift on CFG-002 join the assessment as OS-16…OS-18, H-13…H-15, five rated rows, DM-07, IFU-04 and SF-10…SF-12; the configuration each row belongs to is stated. 0.3: situations reworked against the zones and tasks of WP-C-02 and the scenarios and misuses of WP-C-06 (OS-13…OS-15 added); risk estimated per zone; the risk-graph readings of v0.2 corrected (§5.2); SF-08 and SF-09 identified; the specification of each function moved to WP-C-04; Figures 3-1, 5-1, 6-1. 0.2: DQ-005 applied, PLr d confirmed as the target. 0.1: initial draft |
| Status | Draft |
| PL / scope | Highest PLr: **d** (SF-01, SF-02, SF-03, SF-05, SF-10, SF-11, SF-12), decided by the lead 2026-10-20 (DQ-005 option A: people share the space); one situation rates **e** and is excluded from the operating environment (Z5, §5); the base with the arms and lift (DQ-004 B) on CFG-001 (Gate A unit, bench only) and CFG-002 (2.0 mobile manipulator, unverified) |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1); the ratings need a reviewer who has operated the robot |
| Approver | Project lead |
| Baseline | BL-001; item as defined in [WP-C-01](WP-C-01-item-definition.md) |

> [!WARNING]
> Draft. Severity and probability ratings below are engineering judgement from the record, not from measurement:
> the robot's mass, stopping distance and payload are unknown (WP-C-01 §10). The lead has set PL d as the target
> for the stop functions (DQ-005, 2026-10-20); the ratings still need a reviewer who has driven the Gate A unit.
> Nothing here lowers a rating to fit the existing hardware. Version 0.2 misread the risk graph in five rows;
> §5.2 lists each correction so a reviewer can see what moved and why.

## 1. Scope and inputs

- **Item:** the mobile manipulator of WP-C-01 v0.4 on its two configurations: CFG-001, the Gate A base, in modes
  M1–M6 within the limits of WP-C-01 §4 (bench only since DQ-011 C); CFG-002, the 2.0 base with the lift and the
  two arms, in modes M1–M9 within the quoted limits of WP-C-01 §4.5. Rows that exist only on CFG-002 say so; their
  ratings rest on upstream's plan set and are to be re-rated when the design is public.
- **Inputs:** WP-C-01 (item, functions, modes, assumptions of use); [WP-C-02](WP-C-02-operating-environment-and-tasks.md)
  (zones Z0–Z5 with their people classes and speed limits, tasks T-01–T-08, exclusions);
  [WP-C-06](WP-C-06-human-robot-interaction-and-misuse.md) (interaction scenarios IS-01…IS-12, misuse MU-01…MU-14,
  the detection-distance derivation, requirements HR-01…HR-10); the gap assessment (GAP-01…GAP-40); upstream's
  hazard-relevant statements (`docs/safety/`, hardware "Known limitations", `use/monitoring/safety.md`,
  `decisions.yaml`); ISO 3691-4 Annex A hazard list; ISO 12100 Annex B.
- **Outputs:** the hazard list H-nn (§4), the risk estimation per zone (§5), the measures (§6) and the safety
  functions SF-nn with their PLr (§7). The specification of each safety function (demand, safe state, response
  time, stop category, modes) is [WP-C-04](WP-C-04-safety-functions-and-plr.md).
- **Out of scope:** arms, lift, learned policy (second item, DQ-004); mains-side electrical installation beyond
  the robot's inlet (covered as H-08 only where the robot carries the converter).

## 2. Method

1. **Situations** (§3): one row per way the robot is used, from the tasks and zones of WP-C-02, with the people
   class of the zone and the WP-C-06 scenarios and misuses that occur in it. People class and speed limit are
   zone properties, so a hazard is rated per zone, not once for the whole robot.
2. **Hazard identification** (§4): ISO 12100 Annex B hazard origins crossed with the situations; each hazard
   `H-nn` names the hazardous event and the hazard zone.
3. **Risk estimation** (§5): ISO 13849-1 Annex A risk graph for each hazard and zone that a control function must
   address: severity S1 (slight, normally reversible) or S2 (serious, normally irreversible, or death); frequency
   or exposure F1 (seldom to less often, or short) or F2 (frequent to continuous, or long); possibility of
   avoiding P1 (possible under specific conditions) or P2 (scarcely possible). The graph gives PLr a–e (§2.2).
   Where a rating depends on another safety function already being in place (speed bounded by SF-03, the person
   kept in the field by SF-02), the dependency is written in the row and carried into WP-C-04.
4. **Type-C check.** ISO 3691-4 assigns required Performance Levels to the standard safety functions of
   driverless industrial trucks (emergency stop, personnel detection, speed control, among others; **to be
   checked against a licensed copy**). Where the type-C value and the risk graph differ, the higher is adopted
   unless the row says why not; where the graph gives **e** the situation is excluded from the operating
   environment rather than argued down.
5. **Risk evaluation** (§6): adequate risk reduction per ISO 12100 §6: inherently safe design first, then
   safeguarding and complementary measures (the safety functions `SF-nn` with their PLr), then information for use.
6. **Safety functions** (§7): each `SF-nn` with its adopted PLr and the hazards and scenarios it addresses;
   WP-C-04 specifies it.
7. The hazard IDs, safety-function IDs and assumptions of use are the trace anchors for every later work product.

### 2.1 Severity scale used

| Class | Meaning here | Basis |
|---|---|---|
| S1 | bruise, laceration, a fall without lasting injury | ISO 13849-1 Annex A |
| S2 | fracture, crushing, amputation, death; also any injury to a child or a person who cannot step away | ISO 13849-1 Annex A; ISO 3691-4 treats contact with a person by a driverless truck as S2 unless the truck's kinetic energy and geometry prove otherwise |

The base's mass is unknown. The sizing example upstream uses 45 kg; a chassis of steel panels, two 12 V 7 Ah
lead-acid batteries (about 2.4 kg each) and two geared motors makes 40–60 kg plausible. At 0.20 m/s the kinetic
energy is small (about 1 J), but crushing against a fixed structure at motor stall torque (3.5 N·m per wheel at
0.1 m radius: about 70 N of push, sustained) and a collision with a person who falls are what the S2 ratings rest
on. Until the mass and the stopping distance are measured (WP-C-01 OI-1, OI-2) the conservative class holds.

### 2.2 Risk graph

The eight paths of ISO 13849-1 Figure A.1, as used in §5 (to be checked against a licensed copy; the mapping
below is the published one and the figure of §5 is drawn from this table).

| S | F | P | PLr |
|---|---|---|---|
| S1 | F1 | P1 | a |
| S1 | F1 | P2 | b |
| S1 | F2 | P1 | b |
| S1 | F2 | P2 | c |
| S2 | F1 | P1 | c |
| S2 | F1 | P2 | d |
| S2 | F2 | P1 | d |
| S2 | F2 | P2 | e |

## 3. Situations

Zones, tasks and people classes are those of WP-C-02 §2 and §3 (**none**: the zone is empty of people while
the robot moves; **briefed**: trained staff who know the robot and its stop devices; **public**: anyone,
including children). Scenarios and misuses are those of WP-C-06 §2 and §5.

| ID | Situation | Zone | Task | People | Modes | Scenarios (WP-C-06) | Misuse (WP-C-06) |
|---|---|---|---|---|---|---|---|
| OS-01 | Autonomous navigation along a transport aisle with staff present, including blind corners and people walking beside the robot | Z2 | T-01 | briefed | M3 | IS-01, IS-02, IS-03 | MU-07 |
| OS-02 | Autonomous navigation in the development test area; the operator holds the stop pendant and an observer watches, both outside the path | Z1 | T-01, T-02 | none | M3 | — | MU-07 |
| OS-03 | Docking approach and final push, and the undocking reverse, in the marked dock lane | Z3 | T-03, T-04 | none | M4 | IS-04, IS-05 | MU-03, MU-04 |
| OS-04 | Teleoperation and mapping; the operator looks at the screen, not the robot | Z1, Z2 | T-06, T-07 | briefed | M2, M5 | IS-06, IS-11 | MU-01, MU-02 |
| OS-05 | Bench test and calibration with the wheels off the ground | bench | T-08 | technician | M1 | — | — |
| OS-06 | A bench (debug-enabled) image or a calibration run with the wheels on the ground (foreseeable misuse; upstream's own diagnostics record it) | Z1 | T-08 | technician | M1 | — | MU-08 |
| OS-07 | Charging and battery handling; the mains converter connected | Z4 | T-05 | briefed | M0 | IS-07 | MU-12 |
| OS-08 | Wiring, flashing and maintenance with 24 V present | bench, Z4 | — | technician | M0 | — | — |
| OS-09 | Stopped robot assumed safe: after a watchdog stop, a fault, a UI stop or a chain stop; people within reach | Z1, Z2, Z3 | T-02 | briefed | M6 | IS-11 | MU-09, MU-11, MU-14 |
| OS-10 | Payload carried; a threshold, cable cover or slope crossed | Z2 | T-01 | briefed | M3 | — | MU-06, MU-13 |
| OS-11 | Loss of Wi-Fi, the agent, the navigation LiDAR, battery voltage or a wheel during OS-01…OS-04 | as the parent situation | as the parent | as the parent | any | — | — |
| OS-12 | Another person's computer or device on the same network publishes commands or parameters (misuse or attack) | any | any | anyone | any | — | MU-09, MU-10 |
| OS-13 | The robot waits on a person standing in its path, then the person steps aside and the robot resumes | Z2 | T-01, T-02 | briefed | M3 | IS-10 | MU-14 |
| OS-14 | A person touches the moving or stopped robot: pushes it, leans or sits on it, or tries to stop it by hand | Z2, Z5 | T-01, T-02 | anyone | M3, M6 | IS-08, IS-12 | MU-05 |
| OS-15 | Shared public floor: children, animals, a person lying or crouching below the detection plane, visitors who do not know the robot | Z5 (excluded) | T-01 | public | M3 | IS-09 | MU-07 |
| OS-16 | Manipulation at a station (CFG-002): an arm picks, places, pulls a drawer or door or hands an item over, with the base stopped and staff at the station | Z2 | T-09 | briefed | M7 | IS-13 | MU-15, MU-16 |
| OS-17 | Lift motion at a station (CFG-002): the carriage with the arms and their load moves between the calibrated stops, base stopped | Z2 | T-10 | briefed | M8 | IS-14 | MU-16 |
| OS-18 | Carrying (CFG-002): a transport leg with a load held in the arms in the carry pose, people in the aisle | Z2 | T-11 | briefed | M9 | IS-15 | MU-06, MU-16 |

![Figure 3-1: situation-by-zone matrix: situations OS-01 to OS-18 down the side, the test area, aisle, dock lane, charging bay, public floor and bench across, each cell filled where the situation occurs in that zone and coloured by the people class of the zone, with the task IDs written in the cell and the WP-C-06 scenarios listed at the right](figures/fig-c03-3-1-situations-zones.svg)

*Figure 3-1.* Where each situation occurs and who is exposed there. The colour is the people class of WP-C-02 (none, briefed, public); the public column is hatched because Z5 is excluded at BL-001. Generated by [`figures/fig_c03.py`](figures/fig_c03.py) from the §3 table; CI fails if it is stale.

## 4. Hazard identification

| ID | Hazard (ISO 12100 Annex B origin) | Hazardous event | Zone | Situations |
|---|---|---|---|---|
| H-01 | Mechanical: impact, crushing (moving robot vs person) | The robot drives into a person or pins a person against a fixed structure because the person is not detected, is below the scan plane, is behind the robot, steps out of a blind corner, or the command path keeps driving | path of travel, within one stopping distance of the footprint | OS-01, OS-03, OS-04, OS-10, OS-14, OS-15 |
| H-02 | Mechanical: impact (uncommanded motion) | The robot moves when nobody commanded it, or continues after a stop was requested: watchdog fed by a stale publisher, debug path active, a stuck command, a wrong parameter, an unauthenticated publisher | path of travel; dock lane; around a stopped robot | OS-01…OS-04, OS-06, OS-09, OS-12 |
| H-03 | Mechanical: loss of control (run-away, swerve) | One wheel stops (driver fault latch, loose connector, under-voltage) while the other is driven, or the PID saturates on a dead encoder, or a driver potentiometer or gain is wrong: the robot pivots or runs away at up to 0.71 m/s | path of travel | OS-01…OS-04, OS-10, OS-11, OS-14 |
| H-04 | Mechanical: entanglement, crushing (bench) | Powered debug or calibration spins the wheels at up to 70 % PWM while a hand, cable or the floor is in contact | wheels, drive train | OS-05, OS-06 |
| H-05 | Mechanical: unexpected start-up | After a stop (watchdog, UI stop, fault, chain trip) the robot restarts as soon as commands resume, with nobody having reset it; or it resumes after waiting on a person without warning; or a reboot drops the calibration table and the PID limit-cycles | around a stopped robot | OS-09, OS-11, OS-13 |
| H-06 | Mechanical: instability, tipping | A high or shifting payload, a ramp, a threshold at speed, a person leaning or sitting on the top plate, or the −2.5 m/s² stop tips the robot or throws the payload | around the robot | OS-10, OS-14 |
| H-07 | Electrical: short circuit, fire | A short on the unfused 24 V bus (hundreds of amps from lead-acid), a chafed motor cable, a regenerative spike with no bleed | inside the chassis; charging area | OS-07, OS-08, any |
| H-08 | Electrical: shock | 230 V mains converter fed in parallel with the battery, converter model unknown, no documented RCD, earth or enclosure as built | charging area, inside the chassis | OS-07, OS-08 |
| H-09 | Thermal / chemical: battery | Over-discharge, back-feed between battery and mains, lead-acid gassing in an enclosed bay, no BMS | battery bay | OS-07, any |
| H-10 | Ergonomic / information: mode confusion | The on-screen E-STOP is believed to be an emergency stop; the map on screen is not the room the robot is in; the operator watches the screen; a stopped robot is taken for an idle one | wherever the operator is | OS-04, OS-01, OS-09 |
| H-11 | Combination: loss of sensing not acted upon | The navigation LiDAR stops publishing (known fault), the scan is stale for up to 1 s, the agent is lost: the software keeps the last plan or coasts | path of travel | OS-11 |
| H-12 | Cybersecurity-induced: unauthorised command | Any DDS participant on domain 0 publishes `/cmd_vel`, retunes the PID, loads a wrong encoder table or deactivates the collision monitor | path of travel | OS-12 |
| H-13 | Mechanical: impact, clamping by an arm (CFG-002) | An arm moving at a station strikes a person or clamps a hand, forearm or head against a shelf, the item, the column or the other arm; or the base moves with an arm outside the stowed or carry pose and the sweep reaches beyond the base's protective field | the arm's reach around the station; head height beside a carrying robot | OS-16, OS-18 |
| H-14 | Mechanical: falling or thrown load (CFG-002) | The gripper or the lift releases its load on power loss, an emergency stop, an over-payload or a grip fault; an item is swept off a shelf; the load leaves the gripper in a turn at the carry speed | under and beside the arms | OS-16, OS-17, OS-18 |
| H-15 | Mechanical: crushing, shearing at the lift; tipping with an arm extended (CFG-002) | The lift lowers the carriage onto a hand or foot or raises an arm into a person; a hand is drawn between the column and the arm profile; the robot tips with an arm extended with payload, during a 150 N pull or when braking while carrying | the lift column and the space under the arms; around the robot | OS-16, OS-17, OS-18 |

## 5. Risk estimation

Ratings are for the Gate A unit **as inherited** (no safety function exists), per zone of WP-C-02, under the
assumptions of WP-C-01 §8 that hold only procedurally. "Depends on" names a safety function whose presence the
P rating assumes; WP-C-04 carries the dependency as a requirement on that function. The PLr adopted is the level
the function addressing the row must reach; it is the risk-graph value unless the row says otherwise.

| Hazard · situation | Zone | S | F | P | Rationale | Risk graph | PLr adopted | Addressed by |
|---|---|---|---|---|---|---|---|---|
| H-01 · aisle, staff crossing or walking beside the robot (OS-01: IS-01, IS-03) | Z2 | S2 | F2 | P1 | People share the aisle continuously; at 0.20 m/s a briefed person who sees the robot steps aside; the lateral and crossing cases are what the SF-02 field must cover | d | **d** | SF-02, SF-03, SF-01 |
| H-01 · aisle, blind corner (OS-01: IS-02) | Z2 | S2 | F1 | P2 | Occasional; nothing to see until 0.5 m ahead, so avoidance is scarcely possible for either party; field length cannot cover it (WP-C-06 §3) | d | **d** | SF-02, SF-03; site measure IFU-02 (HR-09); zone speed DQ-017 |
| H-01 · test area (OS-02) | Z1 | S2 | F1 | P1 | Nobody in the path; the operator and observer enter only with the robot stopped | c | **c** (d by the same hardware) | SF-01, AOU-01, AOU-02 |
| H-01 · dock lane, docking and reverse (OS-03: IS-04, IS-05) | Z3 | S2 | F1 | P2 | The lane is meant to be empty, so exposure is occasional; the final approach and the reverse are blind, so a person who is there cannot be avoided | d | **d** | SF-02 (lane field set, rear bumper), SF-03 crawl limit, DQ-018 |
| H-01 · teleoperation and mapping (OS-04: IS-06) | Z1, Z2 | S2 | F1 | P1 | Occasional; the operator is present and can release the control or press the stop | c | **c** | SF-09, SF-03, SF-01; SF-02 where fitted |
| H-01 · public floor (OS-15: IS-09) | Z5 | S2 | F2 | P2 | Continuous exposure of people who do not know the robot; a child or a person below the detection plane cannot avoid it | e | **excluded** (OL-01; DQ-019) | not operated; revisit for 2.0 |
| H-01 · a person pushes or hand-stops the robot (OS-14: IS-12) | Z2 | S1 | F1 | P1 | About 70 N of push at stall torque; a standing adult steps back; the hand-contact limit is to be measured (WP-C-06 OI-4) | a | **a** | SF-06 (stall), IFU-01 |
| H-02 · uncommanded motion near people (OS-01, OS-09, OS-12) | Z2 | S2 | F2 | P1 | Can occur at any time with no warning and the robot looks stopped; at a speed bounded by SF-03 a briefed person next to it can step away. **Depends on** SF-03 (d) and SF-08 (warning) | d | **d** | SF-01, SF-04, SF-05, SF-07 |
| H-03 · loss of control (OS-11, OS-14) | Z2 | S2 | F1 | P1 | Driver fault latches and the known wheel dropout are occasional; a swerve at a speed bounded by SF-03 is avoidable by a briefed person. **Depends on** SF-03 (d); without it P2 and d | c | **c** | SF-06, SF-03 |
| H-04 · bench, wheels off the ground (OS-05) | bench | S1 | F1 | P1 | 60 W motors through a 1:25 gearbox can trap a finger or cable; wheels in the air; the technician can cut 24 V | a | **a** | SF-07, AOU-03, IFU-01 |
| H-04 · bench image with wheels on the ground (OS-06) | Z1 | S1 | F1 | P2 | A foot or cable under a driven wheel with the robot's weight on it; the motion is unannounced | b | **b** | SF-07 (arming), DM-04 |
| H-05 · restart after a chain, fault or watchdog stop (OS-09) | Z1, Z2 | S2 | F1 | P2 | Rare, but the robot restarts with no reset and no indication; a person working next to a stopped robot has no warning | d | **d** (v0.2: c) | SF-05, SF-01 |
| H-05 · resume after waiting on a person (OS-13: IS-10) | Z2 | S2 | F2 | P1 | Frequent in an aisle; the person who stepped aside is out of the path, and is in the SF-02 field while in it. **Depends on** SF-02 (resume only when the field is clear); the residual with SF-02 in place is S1 F2 P1 → b, which is SF-08's rating | d | **d** via SF-02; SF-08 at **b** | SF-02 (SR-02.08), SF-08, IFU-01 |
| H-06 · tipping, payload, a person on the robot (OS-10, OS-14) | Z2 | S2 | F1 | P1 | Unknown margins; a heavy payload and a person leaning on it are foreseeable; crew can keep clear if trained | c | **c** (design measures, no control function) | DM-01…DM-03, OL-02, AOU-06, AOU-07, IFU-03 |
| H-07 · electrical fire (OS-07, OS-08, any) | any | S2 | F1 | P2 | A short is rare; its consequence is uncontrolled | d | n/a (complementary measure) | DM-04 fuse and disconnect |
| H-08 · electric shock (OS-07, OS-08) | Z4 | S2 | F1 | P1 | Mains present only when charging; competent person | c | n/a | DM-05 mains installation per EN 60204-1 |
| H-09 · battery (OS-07, any) | Z4 | S1 | F1 | P1 | AGM is sealed; gassing and back-feed are slow events | a | n/a | DM-06 source selection, battery monitoring |
| H-10 · mode confusion (OS-04, OS-09: IS-06, IS-11; MU-01) | Z1, Z2 | S2 | F2 | P1 | Enables H-01 and H-02; it is the operator's own error, so a trained operator can avoid it; frequent because the UI invites it | d | **d** as a contributor to SF-01 | SF-01 (physical, reachable, marked), HR-05, IFU-01 |
| H-11 · loss of sensing (OS-11) | Z2 | S2 | F1 | P1 | Known LiDAR dropouts; the software coasts on stale data; the path stays covered by the safety scanner, which is independent of the navigation sensor. **Depends on** SF-02 (independent of the navigation LiDAR) | c | **c** | SF-04, SF-02 (SR-02.06) |
| H-12 · unauthorised command (OS-12) | any | S2 | F1 | P1 | Depends on the network; a malicious or mistaken publisher is credible on a shared Wi-Fi; the speed and the stop stay with the chain. **Depends on** SF-03 (d) and SF-01 | c | **c** (security target of DQ-013) | Cybersecurity requirements of [WP-C-08](WP-C-08-cybersecurity-requirements-and-sl-target.md) (threat scenario in WP-C-07); SF-03, SF-07 |
| H-13 · arm contact at a station (OS-16: IS-13; CFG-002) | Z2 | S2 | F2 | P1 | Staff work at the station through the task; a 6 kg payload arm that can pull 150 N can fracture a hand against a shelf; a briefed person sees the arm and keeps clear, and hand-over invites them not to; with the monitored stop of DQ-021 A contact is possible only when the stop fails | d | **d** | SF-11 (monitored stop), SF-01; AOU-10 until the station field exists |
| H-13 · base moves with an arm extended (OS-16, OS-18: IS-15; CFG-002) | Z2 | S2 | F1 | P2 | Occasional (a command arrives mid-task, or the carry pose is wrong); the sweep is outside the field the base's detection is sized for and at head height, so a person beside the robot cannot avoid it | d | **d** | SF-10, SF-02 field for the carry footprint |
| H-14 · load drops from the gripper or the lift (OS-16…OS-18: IS-14, IS-15; CFG-002) | Z2 | S2 | F1 | P2 | A power loss or an emergency stop is occasional; a 6 kg load from shoulder height onto a foot or a head gives no warning | d | **d** | SF-12, DM-07, IFU-04 |
| H-15 · crushing or shearing at the lift (OS-17: IS-14; CFG-002) | Z2 | S2 | F1 | P1 | The lift moves at 18 mm/s with 800 N; a hand under the carriage is crushed slowly enough to withdraw, a foot under it is not; lift motion is occasional and with the base stopped | c | **c** | SF-12 (interlock), IFU-04 |
| H-15 · tipping with an arm extended or while carrying (OS-16, OS-18; CFG-002) | Z2 | S2 | F1 | P1 | Upstream's F2S model analyses the arm-forward, one-arm-sideways and 150 N cases but its rerun is pending; the 0.3 m/s carry limit and the carry pose are the margins | c | **c** (design measures, no control function) | DM-03 (F2S rerun), OL-02 carry limit, CA-05, CA-07 |

![Figure 5-1: the ISO 13849-1 risk graph drawn as a tree from the starting point through severity, frequency and avoidance to the five required Performance Levels a to e, each leaf coloured by level, with the hazard rows of the table written at the leaf their path reaches; the single row at PL e is marked excluded](figures/fig-c03-5-1-risk-graph.svg)

*Figure 5-1.* The §5 rows placed on the risk graph of §2.2. The one path that reaches **e** (public floor, Z5) is closed by excluding the zone, not by a function; the d leaf carries the stop functions. Generated by [`figures/fig_c03.py`](figures/fig_c03.py) from the §2.2 and §5 tables; CI fails if a row's S, F, P and graph value disagree.

### 5.1 Counts

15 hazards rated in 25 rows across the zones and the two configurations. Highest PLr adopted: **d** (eleven rows:
H-01 in Z2 and Z3, H-02, H-05 both cases, H-10 as a contributor, H-07 as a complementary measure, and on CFG-002
both H-13 cases and the H-14 load drop). One row rates **e** (H-01 on the public floor) and is excluded from the
operating environment. Nine rows at c, one at b, three at a. Twelve safety functions (SF-01…SF-12, §7); seven
design or complementary measures (DM-01…DM-07); two operating-environment limits (OL-01, OL-02); four
information-for-use items (IFU-01…IFU-04). The five CFG-002 rows rest on upstream's plan set.

### 5.2 Corrections from version 0.2

Version 0.2 rated H-01 and H-02 as S2 F2 P2 and wrote **d**; the graph gives **e** for that path. It rated
H-03, H-05, H-11 and H-12 as S2 F1 P2 and wrote **c**; the graph gives **d**. It rated the separated-area case
as S2 F1 P1 and wrote **b**; the graph gives **c**. Version 0.3 does not change the graph; it re-rates per zone:

| Row | v0.2 | v0.3 | What changed |
|---|---|---|---|
| H-01 collision, people share the floor | S2 F2 P2 → "d" | Z2: S2 F2 P1 → d; blind corner S2 F1 P2 → d; Z5: S2 F2 P2 → e, excluded | P2 applied to briefed staff at 0.20 m/s was too strict for the aisle and too lenient for a public floor; the zones of WP-C-02 separate the two |
| H-01 separated area | S2 F1 P1 → "b" | c | arithmetic |
| H-02 uncommanded motion | S2 F2 P2 → "d" | S2 F2 P1 → d, depends on SF-03 and SF-08 | the dependency is now explicit instead of hidden in the reading |
| H-03 loss of control | S2 F1 P2 → "c" | S2 F1 P1 → c, depends on SF-03 | as above |
| H-05 unexpected start-up | S2 F1 P2 → "c" | d | SF-05 rises to PLr d; the monitored reset of the chain already meets it at no cost |
| H-11 loss of sensing | S2 F1 P2 → "c" | S2 F1 P1 → c, depends on SF-02 | the safety scanner, not the navigation LiDAR, is the detection means (DQ-007) |
| H-12 unauthorised command | S2 F1 P2 → "c" | S2 F1 P1 → c, depends on SF-03 | as H-03 |

The reviewer of OI-5 confirms or rejects each re-rating; none of them lowers a PLr below v0.2 and one raises one.

## 6. Risk evaluation and reduction

ISO 12100 §6 order. None of the measures exists on the Gate A unit; the table says what the fork must add.
"Reduces" lists the hazards the measure acts on; Figure 6-1 is drawn from it.

| Measure | Type | Reduces | Status today |
|---|---|---|---|
| DM-01 payload limit and restraint; payload height limit | inherently safe design (limits) | H-06 | no limit stated |
| DM-02 measured stopping distance and deceleration limit consistent with stability | inherently safe design | H-06, H-01 | not measured |
| DM-03 mass and centre-of-gravity record; tipping test | inherently safe design | H-06 | not done |
| DM-04 fuse on the battery positive, lockable disconnect | complementary (EN 60204-1 §5.3, §7.2) | H-07, H-04, H-08 | none fitted (GAP-19) |
| DM-05 mains side per EN 60204-1: identified converter, RCD, earth, enclosure, inlet | complementary | H-08 | unknown converter (GAP-20) |
| DM-06 one source at a time (selector or charge interlock), battery voltage monitoring | complementary | H-09, H-03 | parallel sources, no monitor |
| DM-07 gripper and lift hold their load on power loss by design (spring-closed or self-locking gripper, brake or self-locking lift drive); payload limit of the gripper marked (CFG-002) | inherently safe design | H-14, H-15 | upstream `LIFT` release gate "written DOLD holding on E-stop and power loss" not passed; gripper behaviour not published |
| OL-01 zone exclusions of WP-C-02 §5: no public floor (Z5), no Z0, no ramps, edges, glass, crowds | operating-environment limit | H-01, H-06 | map limits only; no geofence (WP-C-02 OI-3) |
| OL-02 speed limit per zone and the crawl limit for the dock lane and reverse (WP-C-02 §2; DQ-017 A: 0.3 m/s with detection, 0 without; DQ-018 A: no blind back-up, undock at 0.05 m/s) | operating-environment limit, enforced by SF-03 | H-01, H-03 | Nav2 limit only; docking unbounded |
| SF-01 emergency stop | safeguarding, control function | H-01, H-02, H-04, H-05, H-10 | none |
| SF-02 protective stop on personnel detection | safeguarding, control function | H-01, H-05, H-11 | none |
| SF-03 safely-limited speed | safeguarding, control function | H-01, H-03, H-12 | none |
| SF-04 stop on loss of command, communication or control | safeguarding, control function | H-02, H-11 | partly (firmware watchdog) |
| SF-05 prevention of unexpected start-up | safeguarding, control function | H-05, H-02 | none |
| SF-06 stop on drive fault | safeguarding, control function | H-03, H-01 | none |
| SF-07 powered-debug inhibit | safeguarding, control function | H-04, H-02, H-12 | compile-time define only |
| SF-08 warning before motion | safeguarding, complementary (warning device) | H-05, H-10 | none |
| SF-09 enabling control for teleoperation | safeguarding, control function | H-01, H-10 | none (keyboard teleop floods `/cmd_vel`) |
| SF-10 base motion inhibit while an arm is outside the stowed or carry pose (CFG-002) | safeguarding, control function | H-13, H-15 | none: an upstream motion rule, no interlock |
| SF-11 arm safe stop and collaborative force limiting (CFG-002) | safeguarding, control function | H-13 | none: no arm safety function named upstream |
| SF-12 lift and gripper holding on stop and power loss; lift interlock (CFG-002) | safeguarding, control function | H-14, H-15 | none: holding evidence is a release gate |
| IFU-01 operator training; the on-screen stop is not an emergency stop; markings; the rule that a stopped robot is not an idle one | information for use | H-10, H-01, H-04, H-05 | upstream user page exists |
| IFU-02 site measures: blind corners, one-way rules for people, lane marking, recorded in the site survey (HR-09) | information for use | H-01 | none |
| IFU-03 payload, height and restraint markings on the top plate (HR-08) | information for use | H-06 | none |
| IFU-04 station marking, the hand-over rule and the lift keep-clear zone (CFG-002; CA-02, CA-06) | information for use | H-13, H-14, H-15 | none |

![Figure 6-1: hazard-to-measure matrix: the twelve hazards down the side and the measures across, grouped as design measures, operating-environment limits, safety functions and information for use, with a dot where the measure reduces the hazard and the adopted required Performance Level of each hazard written beside its row](figures/fig-c03-6-1-hazard-measures.svg)

*Figure 6-1.* Which measure acts on which hazard, in the ISO 12100 order from left to right. Every hazard has at least one dot outside the information-for-use group; the hazards rated d have a safety function. Generated by [`figures/fig_c03.py`](figures/fig_c03.py) from the §6 table; CI fails if it is stale.

## 7. Safety functions

The functions identified here are specified in [WP-C-04](WP-C-04-safety-functions-and-plr.md) (demand, safe
state, response time, stop category, category, modes and tasks) and carried as requirements in WP-S-02. The
PLr is the highest adopted in §5 among the rows the function addresses.

| ID | Safety function | PLr | From §5 | Hazards | Scenarios and misuses | Implements today |
|---|---|---|---|---|---|---|
| SF-01 | Emergency stop | d | H-01 Z2, H-02, H-10 | H-01, H-02, H-04, H-05, H-10 | IS-06, IS-11, MU-01 | nothing (button switches nothing) |
| SF-02 | Protective stop on personnel detection | d | H-01 Z2 and Z3, H-05 resume | H-01, H-05, H-11 | IS-01…IS-05, IS-09, IS-10, MU-03, MU-04, MU-07 | nothing safety-rated (GAP-14, GAP-22) |
| SF-03 | Safely-limited speed | d | H-01 Z2 and Z3; depended on by H-02, H-03, H-12 | H-01, H-03, H-12 | IS-01, IS-02, IS-04, IS-05, MU-10 | nothing: the 0.71 m/s ceiling is a command clamp in the same firmware |
| SF-04 | Stop on loss of command, communication or control | c | H-11, H-02 | H-02, H-11 | MU-09 | partly: 200 ms watchdog and agent-loss stop, same core, no hardware watchdog (GAP-03) |
| SF-05 | Prevention of unexpected start-up | d | H-05 restart | H-05, H-02 | IS-10, MU-11, MU-14 | nothing: motion resumes as soon as commands return |
| SF-06 | Stop on drive fault | c | H-03 | H-03, H-01 | IS-08, IS-12 | nothing: driver ERR unwired; no plausibility checks (GAP-04, GAP-05) |
| SF-07 | Powered-debug inhibit | b | H-04 on the ground | H-04, H-02, H-12 | MU-08 | compile-time define, on in the deployed build (GAP-07, GAP-08) |
| SF-08 | Warning before motion | b | H-05 resume (residual with SF-02) | H-05, H-10 | IS-10, MU-14 | nothing: no sounder or stack light |
| SF-09 | Enabling control for teleoperation | c | H-01 teleoperation | H-01, H-10 | IS-06, MU-02 | nothing: no deadman; teleop bypasses the smoother and the monitor |
| SF-10 | Base motion inhibit while an arm is outside the stowed or carry pose (CFG-002) | d | H-13 base moves with an arm extended | H-13, H-15 | IS-15, MU-16 | nothing: upstream `LIFT` motion rule, no interlock in any repository |
| SF-11 | Arm safe stop and collaborative force limiting (CFG-002) | d | H-13 arm contact | H-13 | IS-13, MU-15 | nothing: no arm safety function named upstream; the OpenArm limits are not published |
| SF-12 | Lift and gripper holding on stop and power loss; lift interlock (CFG-002) | d | H-14 load drop; H-15 lift crushing | H-14, H-15 | IS-14, MU-16 | nothing: the DOLD holding evidence is an upstream release gate not yet passed |

Notes:

- SF-01, SF-02 and SF-03 at PL d match ISO 3691-4's expectation for driverless trucks in zones with people
  (to be checked) and upstream's own 2.0 procurement (Pilz PNOZ s3, dual-channel E-stops, two contactors with
  linked auxiliaries). DQ-005 committed the fork to PL d with people sharing the space.
- SF-05 rises from c (v0.2) to d: the restart case rates S2 F1 P2. The monitored manual reset of the safety relay
  (WP-H-02 E2, PL e capable) is the implementation either way, so the change costs nothing on the bench build but
  moves the claim G1.5 and the requirements SR-05.x to d.
- SF-10, SF-11 and SF-12 are new in v0.4 and exist only on CFG-002; they come from WP-C-06 CA-01…CA-07 and
  HR-10…HR-12. Their PLr d values follow the graph; the type-C values of ISO 10218-2 for collaborative functions
  (to be checked) are expected to agree.
- SF-08 and SF-09 are new in v0.3, from WP-C-06 HR-06 and HR-04. SF-08 is a warning device, not a stop; its PLr b
  is the residual after SF-02. SF-09 is the hold-to-run control teleoperation lacks; WP-S-02 needs SR-08.x and
  SR-09.x for them (WP-S-02 OI-6).
- The dependencies written in §5 (H-02, H-03, H-12 on SF-03; H-05 and H-11 on SF-02) are requirements on those
  functions: SF-03 must bound every path to the motors, including teleoperation and docking, and SF-02 must be
  independent of the navigation sensing. Both are already in WP-S-02 (SR-03.02, SR-02.06).
- The fork's first firmware change (change record `07-supporting/impact/change-2026-10-20-fw-hardening.md`)
  drafts parts of SF-04 (hardware watchdog, command validation), SF-06 (stall detector) and SF-07 (debug paths
  off in the reference build). It is not compiled on the target toolchain, not bench-tested and not reviewed, so
  the "implements today" column stays as written until the bench test is recorded.

## 8. Residual risk and conditions

Until SF-01 exists, no operation with wheels on the ground is inside this assessment unless an operator holds a
means to cut 24 V (AOU-01) and nobody else is within reach of the robot (AOU-02). Until SF-02 exists, autonomous
operation around people (Z2) is outside the assessment whatever the software envelope does. Docking and
undocking (Z3) are outside the assessment until GAP-15 and GAP-35 are closed. The public floor (Z5) is outside
the operating environment at every baseline of the Gate A unit: its rating is e and no bench-build function is
designed for it (DQ-019). Teleoperation near people is outside the assessment until SF-09 exists. On CFG-001 no
on-ground operation at all is inside the assessment since DQ-011 C; everything on CFG-002 is outside it until its
design is public and the arm's force limits are measured (AOU-10).

## 9. Hazard log cross-references

| Hazard | Gap-assessment findings | Scenarios and misuses (WP-C-06) | Requirements derived (WP-C-06 §7) | Decisions |
|---|---|---|---|---|
| H-01 | GAP-01, GAP-02, GAP-13, GAP-14, GAP-15, GAP-16, GAP-22, GAP-35 | IS-01…IS-06, IS-09, IS-12, MU-02, MU-03, MU-04, MU-07 | HR-01, HR-02, HR-03, HR-04, HR-09 | DQ-005, DQ-007, DQ-017, DQ-018, DQ-019 |
| H-02 | GAP-01, GAP-06, GAP-07, GAP-08, GAP-27, GAP-36 | IS-07, IS-10, IS-11, MU-01, MU-08, MU-09, MU-10 | HR-05 | DQ-006 |
| H-03 | GAP-04, GAP-05, GAP-17, GAP-24 | IS-08, IS-12, MU-05 | — | DQ-008 |
| H-04 | GAP-08, GAP-09 | MU-08 | — | |
| H-05 | GAP-09, GAP-10, GAP-37 | IS-10, MU-11, MU-14 | HR-06, HR-07 | |
| H-06 | GAP-23, GAP-38 | IS-08, MU-05, MU-06, MU-13 | HR-08 | |
| H-07 | GAP-19, GAP-24 | — | — | DQ-011 |
| H-08 | GAP-20 | IS-07, MU-12 | — | |
| H-09 | GAP-20, GAP-21 | MU-12 | — | |
| H-10 | GAP-28, GAP-12, GAP-38 | IS-06, IS-11, MU-01, MU-02, MU-14 | HR-05, HR-07 | |
| H-11 | GAP-03, GAP-16, GAP-37 | — | — | |
| H-12 | GAP-27, GAP-29 | MU-09, MU-10 | — | DQ-003, DQ-013 |
| H-13 | gap assessment §8 (no arm safety function) | IS-13, IS-15, MU-15, MU-16 | HR-10, HR-11 | DQ-004, DQ-020, DQ-021 |
| H-14 | gap assessment §8 (`LIFT` release gates) | IS-14, IS-15, MU-16 | HR-12 | DQ-004, DQ-020 |
| H-15 | GAP-23; gap assessment §8 (F2S rerun pending) | IS-14, IS-15, MU-16 | HR-12 | DQ-004, DQ-020 |

Cyber-induced hazards are analysed in WP-C-07 ([threat and risk assessment](WP-C-07-cybersecurity-threat-and-risk-assessment.md)); H-12 is the hazard its scenarios map back to, and the security level target behind the PLr c rating is decision DQ-013.

## 10. Open items

| ID | Item | Blocks |
|---|---|---|
| OI-1 | Measure mass, stopping distance and payload limit (WP-C-01 OI-1…OI-3) and re-rate S for H-01, H-06 | §5 confirmation |
| OI-2 | ~~Lead decision DQ-005~~ decided 2026-10-20: PL d, people share the space; SF-02 is required | closed |
| OI-3 | Field data on wheel dropout frequency (upstream issue) to settle F for H-03 | SF-06 PLr |
| OI-4 | ~~Dock-lane speed and people in the lane~~ DQ-017 and DQ-018 answered A on 2026-10-20 (applied in WP-C-02 v0.3); the lane is a people-class *none* zone in WP-C-02 | SF-02, SF-03 field sizes |
| OI-5 | Reviewer with Gate A operating experience to confirm or change every rating, including the re-ratings of §5.2 | approval |
| OI-6 | Lead decision DQ-019: keep the public floor (Z5) excluded for the Gate A unit, or open a PL e / force-limited argument for it | scope of SF-02 |
| OI-7 | Confirm the ISO 3691-4 PLr table against a licensed copy and record the type-C values in WP-C-04 §4; **unscheduled** (DQ-016 option C, 2026-10-20: no standards until an assessor is engaged) | WP-C-04 §4 |
| OI-8 | ~~Apply DQ-004 B~~ done in v0.4 (OS-16…OS-18, H-13…H-15, SF-10…SF-12); the CFG-002 rows are re-rated when the design is public and the arm limits are measured (WP-C-01 OI-6, OI-7) | v0.5 |
| OI-9 | ~~Lead decision DQ-021~~ decided 2026-10-20 (option A): safety-rated monitored stop; the arm-contact row stands at d | closed |
