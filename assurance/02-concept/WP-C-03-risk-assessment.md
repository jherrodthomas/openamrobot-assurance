# WP-C-03 Risk Assessment and Required Performance Levels

| Field | Value |
|---|---|
| Work product | WP-C-03 Risk assessment (ISO 12100) and determination of the required Performance Level per safety function (ISO 13849-1) |
| Standard reference | ISO 12100:2010 §5.4–§5.6, Annex B; ISO 13849-1:2023 §5, Annex A (risk graph); ISO 3691-4:2023 §4, Annex A; ISO 13850:2015; EN 60204-1:2018 §9.2.2 (stop categories); Regulation (EU) 2023/1230 Annex III §1.1.2 |
| Version | 0.2 (2026-10-20): DQ-005 applied, PLr d confirmed as the target. 0.1: initial draft |
| Status | Draft |
| PL / scope | Highest PLr: **d** (SF-01, SF-02, SF-03), decided by the lead 2026-10-20 (DQ-005 option A: people share the space); reference configuration Gate A unit (DQ-002); mobile base only |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1); the ratings need a reviewer who has operated the robot |
| Approver | Project lead |
| Baseline | BL-001; item as defined in [WP-C-01](WP-C-01-item-definition.md) |

> [!WARNING]
> Draft. Severity and probability ratings below are engineering judgement from the record, not from measurement:
> the robot's mass, stopping distance and payload are unknown (WP-C-01 §10). The lead has set PL d as the target
> for the stop functions (DQ-005, 2026-10-20); the ratings still need a reviewer who has driven the Gate A unit.
> Nothing here lowers a rating to fit the existing hardware.

## 1. Scope and inputs

- **Item:** the Gate A mobile base of WP-C-01, in modes M1–M6, within the limits of WP-C-01 §4.
- **Inputs:** WP-C-01; the gap assessment (GAP-01…GAP-40); upstream's hazard-relevant statements (`docs/safety/`,
  hardware "Known limitations", `use/monitoring/safety.md`, `decisions.yaml`); ISO 3691-4 Annex A hazard list;
  ISO 12100 Annex B.
- **Out of scope:** arms, lift, learned policy (second item, DQ-004); mains-side electrical installation beyond
  the robot's inlet (covered as H-08 only where the robot carries the converter).

## 2. Method

1. **Tasks and situations** (§3): the phases of use and the people exposed, from WP-C-01 §2 and §5.
2. **Hazard identification** (§4): ISO 12100 Annex B hazard origins crossed with the situations; each hazard
   `H-nn` names the hazardous event and the hazard zone.
3. **Risk estimation** (§5): ISO 13849-1 Annex A risk graph for each hazard that a control function must
   address: severity S1 (slight, normally reversible) or S2 (serious, normally irreversible, or death); frequency
   or exposure F1 (seldom to less often, or short) or F2 (frequent to continuous, or long); possibility of
   avoiding P1 (possible under specific conditions) or P2 (scarcely possible). The graph gives PLr a–e.
4. **Risk evaluation** (§6): adequate risk reduction per ISO 12100 §6: inherently safe design first, then
   safeguarding and complementary measures (the safety functions `SF-nn` with their PLr), then information for use.
5. **Safety functions** (§7): each `SF-nn` with PLr, stop category, response-time target, and what implements it
   today (nothing, in most cases).
6. The hazard IDs, safety-function IDs and assumptions of use are the trace anchors for every later work product.

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

## 3. Tasks and situations

| ID | Situation | People exposed | Modes |
|---|---|---|---|
| OS-01 | Autonomous navigation in a mapped indoor area with people present | bystanders, operator | M3 |
| OS-02 | Autonomous navigation in a separated area, no people inside | operator at the boundary | M3 |
| OS-03 | Docking approach and final push, and undocking reverse | bystanders near the dock, operator | M4 |
| OS-04 | Keyboard or UI teleoperation, operator looking at the screen | operator, bystanders | M2, M5 |
| OS-05 | Bench test and calibration with wheels off the ground | builder, technician | M1 |
| OS-06 | Bench test or calibration with wheels on the ground (foreseeable misuse; upstream's own diagnostics record it) | builder, technician | M1 |
| OS-07 | Charging and battery handling; mains converter connected | technician, bystanders | M0 |
| OS-08 | Wiring, flashing, maintenance with 24 V present | builder, technician | M0 |
| OS-09 | Stopped robot, assumed safe (after watchdog stop, after a fault, after a UI stop) | anyone | M6 |
| OS-10 | Payload carried; ramp, threshold or cable cover crossed | bystanders, operator | M2, M3 |
| OS-11 | Loss of Wi-Fi, agent, LiDAR, or a wheel during OS-01…OS-04 | as the parent situation | any |
| OS-12 | Another person's computer or device on the same network publishes commands (misuse or attack) | anyone | any |

## 4. Hazard identification

| ID | Hazard (ISO 12100 Annex B origin) | Hazardous event | Zone | Situations |
|---|---|---|---|---|
| H-01 | Mechanical: impact, crushing (moving robot vs person) | The robot drives into a person or pins a person against a fixed structure because the person is not detected, is below the scan plane, is behind the robot, or the command path keeps driving | path of travel, within one stopping distance of the footprint | OS-01, OS-03, OS-04, OS-10 |
| H-02 | Mechanical: impact (uncommanded motion) | The robot moves when nobody commanded it, or continues after a stop was requested: watchdog fed by a stale publisher, debug path active, a stuck command, a wrong parameter, an unauthenticated publisher | path of travel; dock lane; around a stopped robot | OS-01…OS-04, OS-09, OS-12 |
| H-03 | Mechanical: loss of control (run-away, swerve) | One wheel stops (driver fault latch, loose connector, under-voltage) while the other is driven, or the PID saturates on a dead encoder, or a driver potentiometer or gain is wrong: the robot pivots or runs away at up to 0.71 m/s | path of travel | OS-01…OS-04, OS-10, OS-11 |
| H-04 | Mechanical: entanglement, crushing (bench) | Powered debug or calibration spins the wheels at up to 70 % PWM while a hand, cable or the floor is in contact | wheels, drive train | OS-05, OS-06 |
| H-05 | Mechanical: unexpected start-up | After a stop (watchdog, UI stop, fault) the robot restarts as soon as commands resume, with nobody having reset it; or a reboot drops the calibration table and the PID limit-cycles | around a stopped robot | OS-09, OS-11 |
| H-06 | Mechanical: instability, tipping | A high or shifting payload, a ramp, a threshold at speed, or the −2.5 m/s² stop tips the robot or throws the payload | around the robot | OS-10 |
| H-07 | Electrical: short circuit, fire | A short on the unfused 24 V bus (hundreds of amps from lead-acid), a chafed motor cable, a regenerative spike with no bleed | inside the chassis; charging area | OS-07, OS-08, any |
| H-08 | Electrical: shock | 230 V mains converter fed in parallel with the battery, converter model unknown, no documented RCD, earth or enclosure as built | charging area, inside the chassis | OS-07, OS-08 |
| H-09 | Thermal / chemical: battery | Over-discharge, back-feed between battery and mains, lead-acid gassing in an enclosed bay, no BMS | battery bay | OS-07, any |
| H-10 | Ergonomic / information: mode confusion | The on-screen E-STOP is believed to be an emergency stop; the map on screen is not the room the robot is in; the operator watches the screen | wherever the operator is | OS-04, OS-01 |
| H-11 | Combination: loss of sensing not acted upon | LiDAR stops publishing (known fault), scan stale for up to 1 s, agent lost: the software keeps the last plan or coasts | path of travel | OS-11 |
| H-12 | Cybersecurity-induced: unauthorised command | Any DDS participant on domain 0 publishes `/cmd_vel`, retunes the PID, loads a wrong encoder table or deactivates the collision monitor | path of travel | OS-12 |

## 5. Risk estimation

Ratings are for the Gate A unit **as inherited** (no safety function exists) under the assumptions of WP-C-01 §8
that hold only procedurally. The PLr is the level the safety function that addresses the hazard must reach.

| Hazard | S | F | P | Rationale | PLr (risk graph) | Addressed by |
|---|---|---|---|---|---|---|
| H-01 collision with a person | S2 | F2 | P2 | People share the floor continuously in OS-01; at 0.20 m/s a person can usually step aside (P1) **but** a person below the scan plane, behind the robot, or pinned cannot, and the dock lane is a blind manoeuvre: P2 for the function as a whole | **d** | SF-01, SF-02, SF-03 |
| H-01 in a separated area (OS-02) | S2 | F1 | P1 | Nobody inside; the operator enters only with the robot stopped | **b** | SF-01, SF-05 (DQ-005 option B) |
| H-02 uncommanded motion | S2 | F2 | P2 | Can occur at any time with no warning; the robot looks stopped | **d** | SF-01, SF-04, SF-05 |
| H-03 loss of control | S2 | F1 | P2 | Driver fault latches and the known wheel dropout are occasional, but the resulting swerve is unannounced | **c** (d if F2 is confirmed by field data) | SF-06, SF-03 |
| H-04 bench entanglement | S1 | F1 | P1 | 60 W motors through a 1:25 gearbox can trap a finger or cable; wheels in the air; a technician is at the robot and can cut 24 V | **a** (b with wheels on the ground) | SF-01, SF-07, information for use |
| H-05 unexpected start-up | S2 | F1 | P2 | Rare but the robot restarts with no reset and no indication | **c** | SF-05, SF-01 |
| H-06 tipping, payload | S2 | F1 | P1 | Unknown margins; a heavy payload is foreseeable; crew can keep clear if trained | **c** | design measures (DM-01…DM-03), AOU-06, AOU-07 |
| H-07 electrical fire | S2 | F1 | P2 | A short is rare; its consequence is uncontrolled | n/a (not a control function) | DM-04 fuse and disconnect |
| H-08 electric shock | S2 | F1 | P1 | Mains present only when charging; competent person | n/a | DM-05 mains installation per EN 60204-1 |
| H-09 battery | S1 | F1 | P1 | AGM is sealed; gassing and back-feed are slow events | n/a | DM-06 source selection, battery monitoring |
| H-10 mode confusion | S2 | F2 | P1 | Enables H-01 and H-02; a trained operator can avoid it | **c** (as a contributor to SF-01's usability) | SF-01 (physical, reachable, marked), information for use |
| H-11 loss of sensing | S2 | F1 | P2 | Known LiDAR dropouts; software coasts on stale data | **c** | SF-04, SF-02 (fail-safe on stale source) |
| H-12 unauthorised command | S2 | F1 | P2 | Depends on the network; a malicious or mistaken publisher is credible on a shared Wi-Fi | **c** (security, IEC 62443 SL 2 target) | CS-01 (WP-C-10), SF-03 bounds the consequence |

### 5.1 Counts

12 hazards; 9 need a control safety function; highest PLr **d** (H-01, H-02); 3 at PLr c; 1 at PLr b in the
separated-area case; 1 at PLr a. 6 design or complementary measures (DM-01…DM-06).

## 6. Risk evaluation and reduction

ISO 12100 §6 order. None of the measures exists on the Gate A unit; the table says what the fork must add.

| Measure | Type | Reduces | Status today |
|---|---|---|---|
| DM-01 payload limit and restraint; payload height limit | inherently safe design (limits) | H-06 | no limit stated |
| DM-02 measured stopping distance and deceleration limit consistent with stability | inherently safe design | H-06, H-01 | not measured |
| DM-03 mass and centre-of-gravity record; tipping test | inherently safe design | H-06 | not done |
| DM-04 fuse on the battery positive, lockable disconnect | complementary (EN 60204-1 §5.3, §7.2) | H-07, H-04, H-08 | none fitted (GAP-19) |
| DM-05 mains side per EN 60204-1: identified converter, RCD, earth, enclosure, inlet | complementary | H-08 | unknown converter (GAP-20) |
| DM-06 one source at a time (selector or charge interlock), battery voltage monitoring | complementary | H-09, H-03 | parallel sources, no monitor |
| SF-01…SF-07 | safeguarding by control functions | §7 | none |
| IFU-01 operator training, zone marking, the rule that the on-screen stop is not an emergency stop | information for use | H-10, residual | upstream user page exists |

## 7. Safety functions

Stop categories per EN 60204-1 §9.2.2: category 0 is immediate removal of power; category 1 is a controlled stop
with power removed when stopped. The Gate A drive has no brake, so category 0 is a coast; category 1 needs the
drivers to decelerate before power is cut.

| ID | Safety function | PLr (proposed) | Category (13849-1) | Stop cat. | Response target | Implements today | Hazards |
|---|---|---|---|---|---|---|---|
| SF-01 | **Emergency stop.** A red mushroom button, reachable from the operator position and from the sides of the robot, removes traction power independently of all software and latches until manually reset | d | 3 (dual channel, monitored) | 0 | ≤ 200 ms to power removal | nothing (button switches nothing) | H-01, H-02, H-04, H-05, H-10 |
| SF-02 | **Protective stop on personnel detection.** When a person enters the protective field ahead of the robot (sized from speed and stopping distance), the robot stops before contact; the field must cover the direction of travel including reverse and the dock lane, and objects down to a child's leg height | d | 3 | 1 then 0 | field sized so that stop completes before contact at 0.20 m/s | nothing safety-rated (2D LiDAR "not a safety device", monitor deactivated in docking) | H-01, H-11 |
| SF-03 | **Safely-limited speed.** The wheel speed never exceeds the limit set for the zone (0.20 m/s navigation today; a lower limit in the dock lane), monitored independently of the command path, with a stop on violation | d | 2 or 3 | 1 | detect within 100 ms | nothing: the 0.71 m/s ceiling is a command clamp in the same firmware, and the docking speeds are unbounded | H-01, H-03, H-12 |
| SF-04 | **Stop on loss of command or communication.** No valid command within the timeout, agent lost, scan stale beyond its timeout, or controller hang → stop | c | 2 | 0 (1 when a brake exists) | 200 ms (command); 1 s (controller hang) | partly: the 200 ms watchdog and agent-loss stop exist but run on the same core with no hardware watchdog (GAP-03); no stale-scan stop | H-02, H-11 |
| SF-05 | **Prevention of unexpected start-up.** After SF-01, SF-04, SF-06 or a power cycle, motion needs a deliberate reset by the operator; a restart is indicated | c | 2 | — | — | nothing: motion resumes as soon as commands return | H-05, H-02 |
| SF-06 | **Stop on drive fault.** A motor-driver fault, a stalled or encoder-dead wheel, or a wheel following error beyond a limit stops both wheels and latches | c | 2 | 0 | ≤ 1 s | nothing: driver ERR unwired; no plausibility checks (GAP-04, GAP-05) | H-03 |
| SF-07 | **Powered-debug inhibit.** Raw-PWM, gain and calibration paths cannot move or retune the motors unless the robot is deliberately armed for bench use, and arming is indicated | b | 1 | — | — | compile-time define, on in the deployed build (GAP-07, GAP-08) | H-04, H-02, H-12 |

Notes:

- SF-01 and SF-02 at PL d match ISO 3691-4's expectation for driverless trucks in zones with people and upstream's
  own 2.0 procurement (Pilz PNOZ s3, dual-channel E-stops, two contactors with linked auxiliaries). DQ-005 decides
  whether the fork commits to PL d or restricts operation to a separated area (then SF-02 is replaced by access
  control at PL b and SF-01 stays).
- SF-03 is what makes the software layers' 0.20 m/s limit trustworthy: without an independent speed monitor, every
  layer above the firmware is best effort (GAP-13) and the firmware's own clamp is on the same core as the command
  path.
- SF-04 as it exists is the one function upstream implemented; it needs a hardware watchdog, command validation
  and a scan-staleness reaction to reach Category 2.
- The fork's first firmware change (change record `07-supporting/impact/change-2026-10-20-fw-hardening.md`)
  drafts parts of SF-04 (hardware watchdog, command validation), SF-06 (stall detector) and SF-07 (debug paths
  off in the reference build). It is not compiled on the target toolchain, not bench-tested and not reviewed, so
  the "implements today" column stays as written until the bench test is recorded.
- Category and DC targets are set here as the minimum the PLr normally needs; the technical safety concept
  (WP-S-03) chooses the architecture and WP-H-03 proves MTTFd, DC and CCF.

## 8. Residual risk and conditions

Until SF-01 exists, no operation with wheels on the ground is inside this assessment unless an operator holds a
means to cut 24 V (AOU-01) and nobody else is within reach of the robot (AOU-02). Until SF-02 exists, autonomous
operation around people is outside the assessment whatever the software envelope does. Docking and undocking are
outside the assessment until GAP-15 and GAP-35 are closed.

## 9. Hazard log cross-references

| Hazard | Gap-assessment findings | Decisions |
|---|---|---|
| H-01 | GAP-01, GAP-02, GAP-13, GAP-14, GAP-15, GAP-16, GAP-22, GAP-35 | DQ-005 |
| H-02 | GAP-01, GAP-06, GAP-07, GAP-08, GAP-27, GAP-36 | |
| H-03 | GAP-04, GAP-05, GAP-17, GAP-24 | |
| H-04 | GAP-08, GAP-09 | |
| H-05 | GAP-09, GAP-10, GAP-37 | |
| H-06 | GAP-23, GAP-38 | |
| H-07 | GAP-19, GAP-24 | |
| H-08 | GAP-20 | |
| H-09 | GAP-20, GAP-21 | |
| H-10 | GAP-28, GAP-12, GAP-38 | |
| H-11 | GAP-03, GAP-16, GAP-37 | |
| H-12 | GAP-27, GAP-29 | DQ-003 |

## 10. Open items

| ID | Item | Blocks |
|---|---|---|
| OI-1 | Measure mass, stopping distance and payload limit (WP-C-01 OI-1…OI-3) and re-rate S for H-01, H-06 | §5 confirmation |
| OI-2 | ~~Lead decision DQ-005~~ decided 2026-10-20: PL d, people share the space; SF-02 is required | closed |
| OI-3 | Field data on wheel dropout frequency (upstream issue) to settle F for H-03 | SF-06 PLr |
| OI-4 | Decide the dock-lane speed limit and whether docking is allowed with people in the lane | SF-02, SF-03 field sizes |
| OI-5 | Reviewer with Gate A operating experience to confirm or change every rating | approval |
