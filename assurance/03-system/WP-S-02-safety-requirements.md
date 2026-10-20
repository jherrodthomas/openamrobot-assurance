# WP-S-02 Safety Requirements Specification (SRS) for the Safety Functions

| Field | Value |
|---|---|
| Work product | WP-S-02 Safety requirements specification: functional and integrity requirements of SF-01…SF-07 (ISO 13849-1 §5.1 "safety requirements specification") |
| Standard reference | ISO 13849-1:2023 §5 (safety functions, SRS), §4.5 (PLr), §6 (categories), §7 (software); ISO 13850:2015 §4; EN 60204-1:2018 §9.2.2, §9.2.3.4, §9.4; ISO 3691-4:2023 §4, Annex A; IEC 62443-4-2 (CR 1, CR 3) |
| Version | 0.2 (2026-10-20): SF-05 raised to PLr d per WP-C-03 v0.3 and WP-C-04; SF-08 and SF-09 noted as pending (OI-6). 0.1: initial draft from WP-C-03 v0.2 |
| Status | Draft |
| PL / scope | PL d (SF-01, SF-02, SF-03, SF-05), PL c (SF-04, SF-06), PL b (SF-07); SF-08…SF-12 of WP-C-04 v0.2 not yet broken into requirements (OI-6); since DQ-014 B the "Implemented by" of SR-03, SR-04 and SR-06 is the firmware channel plus the hardwired monitor (WP-S-03 §3.5); Gate A unit (CFG-001); mobile base only |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1) |
| Approver | Project lead |
| Baseline | BL-001 |

> [!WARNING]
> Draft. The requirements are derived from WP-C-03 v0.2 and the gap assessment. Numeric values marked **(TBC)**
> wait on the measurements in WP-C-01 §10. None of the requirements is implemented on the Gate A unit; the
> "Implemented by" column names the design intent of WP-S-03, not existing hardware.

## 1. Conventions

- `SR-<SF>.<nn>`: a requirement of safety function `SF-<SF>`. Shall-statements; one requirement, one testable property.
- Attributes: PLr (from WP-C-03 §7), **Type** (F functional, I integrity, T timing, D diagnostic, S security), **Verification** (A analysis, I inspection, T test, D demonstration; the method WP-S-09 and WP-V-01 use), **Implemented by** (WP-S-03 element), **Trace** (hazards of WP-C-03 §4).
- Timing values are the response from the demand at the sensor or button to the start of power removal or the
  controlled stop, measured at the driver input. Stopping distance is end-to-end, demand to standstill.
- "Independent of software" means: no microcontroller, no ROS 2 node, no network and no configuration file is in
  the path, and a failure of any of them cannot prevent the function.

## 2. Requirements common to every safety function

| ID | Requirement | Type | PLr | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|---|
| SR-00.01 | Every safety function shall be implemented by a safety-related part of the control system (SRP/CS) whose achieved PL is at least its PLr, demonstrated per ISO 13849-1 §4.5 (category, MTTFd, DCavg, CCF) and validated per ISO 13849-2 | I | d | A, T | WP-S-03, WP-H-03 | all |
| SR-00.02 | A safety function shall take priority over every other command to the same actuator, including the diagnostic and calibration paths | F | d | T | WP-S-03 §4 (arbitration) | H-02, H-04 |
| SR-00.03 | A safety function shall fail to the safe state (traction power removed, brake applied where fitted) on loss of its own supply, a broken wire, a short to supply or ground in its channel, or loss of the monitoring device | I | d | A, T | WP-S-03 §3 | H-02 |
| SR-00.04 | The state of every safety function (demanded, tripped, reset required, fault) shall be indicated at the robot and reported to the operator interface; the indication shall not be the only means of reset | F | c | I, T | WP-S-03 §6 | H-05, H-10 |
| SR-00.05 | Safety-related parameters (speed limits, field sizes, timeouts, thresholds) shall be stored in a form that cannot be changed from the network at runtime; a change requires a build or a locked configuration step and is recorded under WP-P-02 | S, I | d | I | WP-S-03 §5 | H-12, H-02 |
| SR-00.06 | Safety-related embedded software shall meet ISO 13849-1 §7 (SRESW) for its PL: specification, structured design, coding rules, verification by review and test, configuration management | I | d | I, T | WP-W-* | all |

## 3. SF-01 Emergency stop (PLr d, Category 3, stop category 0)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|---|
| SR-01.01 | The robot shall have at least one emergency-stop device per ISO 13850: red mushroom head on yellow background, positive-opening contacts (IEC 60947-5-5), latching, reset only by deliberate action at the device | F | d | I | WP-S-03 §3.1; E-stop device per upstream SAFETY-PROCUREMENT (Schneider XB4BS8445 + ZBE-102) | H-01, H-02, H-04 |
| SR-01.02 | Emergency-stop devices shall be reachable without stepping into the path of the robot from the operator position and from each long side of the robot; the Gate A unit shall carry one on the front panel and one on the rear or top plate **(TBC: positions)** | F | d | I, D | WP-S-03 §3.1 | H-01, H-10 |
| SR-01.03 | Actuating any emergency-stop device shall remove power from both traction drivers within 200 ms (stop category 0) and, where a brake is fitted, apply the brake | F, T | d | T | WP-S-03 §3.2 (safety relay K0, contactors K1/K2) | H-01, H-02 |
| SR-01.04 | The emergency-stop function shall be hardwired and independent of software (§1 definition); no state of the Pi, the Teensy, the micro-ROS agent, the network or the browser shall delay or prevent it | I | d | A, T | WP-S-03 §3.2 | H-02, H-10, H-11 |
| SR-01.05 | The function shall be dual channel (two contacts per device, two channels to the safety relay, two series contactors or two independent power-removal paths), with cross-monitoring so that a single fault is detected at or before the next demand (Category 3) | I, D | d | A, T | WP-S-03 §3.2 | H-02 |
| SR-01.06 | The safety relay shall have a monitored manual reset: motion is enabled again only after every emergency-stop device is released **and** the reset input is actuated and released; a reset held permanently or shorted shall not enable motion | F | d | T | WP-S-03 §3.3 | H-05 |
| SR-01.07 | The contactor (or power-removal path) feedback shall be monitored in the reset loop (external device monitoring); a welded or stuck contact shall prevent reset | D | d | T | WP-S-03 §3.2 | H-02, H-05 |
| SR-01.08 | The emergency-stop state shall be read by the firmware as a diagnostic input and reported (SR-00.04) without the firmware being in the stop path | D | c | T | WP-S-03 §6; firmware `/firmware/status` | H-10 |
| SR-01.09 | The on-screen stop of the operator interface shall be labelled as a software stop request, not as an emergency stop, and shall not be red-mushroom styled | F | — | I | `openamrobot-ui` (out of item; AoU) | H-10 |

## 4. SF-02 Protective stop on personnel detection (PLr d, Category 3, stop category 1)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|---|
| SR-02.01 | The robot shall detect a person in its direction of travel with a safety-rated detection device (ISO 13849-1 PL d, e.g. a safety laser scanner with OSSD outputs type 3 per IEC 61496-3, or safety-rated bumpers) and shall stop before contact | F | d | T | WP-S-03 §3.4 | H-01 |
| SR-02.02 | The protective field shall cover the full width of the footprint plus a lateral margin **(TBC: ≥ 0.1 m each side)** and a length ahead of the footprint of at least the stopping distance at the current speed limit plus the detection and reaction time distance, plus a margin **(TBC)**; a field set shall exist per speed limit (SF-03) | F | d | A, T | WP-S-03 §3.4; stopping-distance measurement (WP-C-01 OI-2) | H-01 |
| SR-02.03 | Detection shall cover objects from the floor to at least 0.3 m **(TBC)** in the direction of travel; a 2D scan plane alone at 0.18 m or 0.22 m does not satisfy this without a bumper or a second plane | F | d | A, T | WP-S-03 §3.4 | H-01, H-14 (gap) |
| SR-02.04 | Reverse motion (undock; the Nav2 back-up recovery is removed, DQ-018 A) shall be covered by a protective device behind the robot or shall be inhibited: no reverse at a speed above the crawl limit of 0.05 m/s (DQ-018 A, 2026-10-20) without rear detection | F | d | T | WP-S-03 §3.4; software inhibit | H-01 (GAP-35) |
| SR-02.05 | A field violation shall produce a controlled stop (deceleration within the stability limit of WP-C-01 §4.1, stop category 1) followed by power removal if standstill is not reached within **(TBC: 1 s)** | F, T | d | T | WP-S-03 §3.4 | H-01, H-06 |
| SR-02.06 | Loss, error state or stale data of the detection device shall trigger the stop within the device's response time; the OSSD state, not a data stream over the network, shall be the stop signal | I, D | d | T | WP-S-03 §3.4 | H-11 |
| SR-02.07 | The protective function shall not be deactivated by software for any manoeuvre; where a dock approach needs a reduced field, the reduced field shall be a muting or field-switching function of the safety device at PL d, with the dock approach limited to the crawl speed | F | d | A, T | WP-S-03 §3.4; docking redesign (GAP-15) | H-01 |
| SR-02.08 | After a protective stop, motion shall resume only when the field is clear and, for a stop that removed power, after the reset of SR-01.06 | F | c | T | WP-S-03 §3.3 | H-05 |

## 5. SF-03 Safely-limited speed (PLr d, Category 2 or 3, stop category 1)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|---|
| SR-03.01 | The speed of each drive wheel shall be monitored by a means independent of the command path (a second encoder reading or the driver's speed output read by the safety controller, not the Teensy that produces the PWM) | I | d | A, T | WP-S-03 §3.5 | H-01, H-03 |
| SR-03.02 | The monitored speed shall not exceed the limit of the active zone: 0.20 m/s linear and 0.5 rad/s in the navigation zone; the crawl limit **(TBC: 0.05 m/s)** in the dock lane and in reverse; the limits are safety parameters (SR-00.05) | F | d | T | WP-S-03 §3.5 | H-01 |
| SR-03.03 | A violation sustained for more than 100 ms shall trigger a controlled stop and, if standstill is not reached within **(TBC: 1 s)**, power removal; the trip shall latch until reset (SR-01.06) | F, T | d | T | WP-S-03 §3.5 | H-01, H-03 |
| SR-03.04 | The firmware shall in addition refuse any velocity command above a fixed ceiling at the command input (DQ-006 decided 2026-10-20: 0.25 m/s and 0.6 rad/s, navigation limit plus margin); this is a functional measure and carries no PL claim on its own | F | — | T | firmware `twistCallback` (change-2026-10-20-fw-hardening) | H-12 |
| SR-03.05 | A difference between commanded and monitored wheel speed beyond **(TBC: 30 % for 500 ms)** shall be treated as a drive fault (SF-06) | D | c | T | WP-S-03 §3.5 | H-03 |

## 6. SF-04 Stop on loss of command, communication or control (PLr c, Category 2, stop category 0)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|---|
| SR-04.01 | If no valid velocity command is received for 200 ms, the drives shall be set to zero and, where a brake is fitted, the brake applied | F, T | c | T | firmware watchdog (exists) | H-02, H-11 |
| SR-04.02 | A velocity command shall be valid only if every field is finite and within the ceilings of SR-03.04; an invalid command shall count as no command | F | c | T | firmware `twistCallback` (fork change) | H-02 |
| SR-04.03 | A command shall carry a monotonically increasing sequence number or a timestamp from the host; a repeated or out-of-order command shall count as no command **(open: needs an interface change, `TwistStamped` or a wrapped message)** | F | c | T | WP-S-03 §5; ROS 2 interface change | H-02 |
| SR-04.04 | The microcontroller shall run a hardware watchdog with a timeout of at most 1 s, serviced only from the control loop while commands are being executed; a watchdog reset shall leave the drives unpowered and be reported | I, D | c | T | firmware WDOG1 (fork change) | H-11 |
| SR-04.05 | Loss of the micro-ROS session, of the scan source (per SR-02.06) or of the safety controller heartbeat shall stop the robot within the respective timeout; the stop shall latch when it results from a fault (not from a normal end of session) | F | c | T | firmware agent-loss stop (exists); WP-S-03 §3.5 | H-11 |
| SR-04.06 | The host shall not re-feed a stale command: the velocity smoother shall publish zero after its timeout (exists, 1 s) and no node shall republish a command older than 200 ms | F | c | I, T | `openamr-platform-sw` nav2 chain, docking sequencer | H-02 |

## 7. SF-05 Prevention of unexpected start-up (PLr d, Category 3)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|---|
| SR-05.01 | After SF-01, SF-02 (with power removal), SF-03, SF-06 or a power cycle, the robot shall not move until a deliberate reset at the robot (SR-01.06); the first motion after reset shall need a fresh velocity command | F | d | T | WP-S-03 §3.3 | H-05 |
| SR-05.02 | A reset shall not be possible while a stop demand is present, and shall not itself cause motion | F | d | T | WP-S-03 §3.3 | H-05 |
| SR-05.03 | A pending or latched stop shall be indicated at the robot (lamp) and on the operator interface | F | d | I | WP-S-03 §6 | H-05, H-10 |
| SR-05.04 | A reboot of the microcontroller shall report its reset cause and shall not re-enable motion by itself (exists in part: status topic; the enable path is WP-S-03 §3.3) | D | d | T | firmware status (fork change); WP-S-03 §3.3 | H-05 |

## 8. SF-06 Stop on drive fault (PLr c, Category 2, stop category 0)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|---|
| SR-06.01 | The fault output of each motor driver (`ERR/DO1`) shall be read; a driver fault shall stop both drives within 100 ms and latch | F, D | c | T | WP-S-03 §3.5; Teensy input or safety controller | H-03 |
| SR-06.02 | A drive commanded above **(TBC: 60 %)** of maximum PWM whose measured speed stays below **(TBC: 2 rpm)** for **(TBC: 1 s)** shall be treated as stalled or encoder-dead: both drives stop and the fault latches | D | c | T | firmware stall detector (fork change) | H-03 |
| SR-06.03 | A following error (SR-03.05) shall stop both drives and latch | D | c | T | WP-S-03 §3.5 | H-03 |
| SR-06.04 | Encoder direction and count plausibility shall be checked at every start-up by a short, bounded test move with the enable path armed **(open: needs the enable path; today a manual checklist)** | D | c | T, D | WP-S-03 §3.5 | H-03 |
| SR-06.05 | Battery voltage shall be measured; below **(TBC: 23 V)** at rest or **(TBC: 22 V)** under load the robot shall stop and refuse autonomous operation | D | c | T | WP-S-03 §3.6; battery monitor (not implemented upstream) | H-03, H-09 |

## 9. SF-07 Powered-debug inhibit (PLr b, Category 1)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|---|
| SR-07.01 | The reference (production) firmware image shall contain no path that drives the motors from raw PWM or changes control gains from the network | F | b | I, T | firmware `ENABLE_POWERED_DEBUG` off (fork change) | H-04, H-02, H-12 |
| SR-07.02 | A bench image that contains such paths shall be identifiable at runtime (`/firmware/status dbg=1`) and shall bound every input it accepts (gains, right-wheel scale, feedforward, dither, calibration ratios) | F | b | T | firmware (fork change) | H-04 |
| SR-07.03 | Powered debug on a bench image shall additionally require a physical arming input (key switch or jumper read by the firmware) and shall time out after **(TBC: 10 min)** without re-arming **(open)** | F | b | T | WP-S-03 §3.7 | H-04 |
| SR-07.04 | The per-boot encoder alignment procedure shall be possible without the raw-PWM path, or the raw-PWM path shall be limited during alignment to **(TBC: 25 %)** PWM with wheels-off-ground confirmed by the operator **(open)** | F | b | T | firmware; `tools/encoder-calibration` | H-04 |

## 10. Security requirements supporting the safety functions (IEC 62443-4-2, target SL 2)

| ID | Requirement | Type | Verif. | Implemented by | Trace |
|---|---|---|---|---|---|
| SR-10.01 | Velocity, docking, lifecycle and parameter interfaces shall be reachable only by authenticated participants (SROS2 enclaves with access control, or an isolated robot network with no external participant) | S | I, T | WP-C-10 / WP-S-07 (cybersecurity concept) | H-12 |
| SR-10.02 | The operator interface shall authenticate operators and shall not expose rosbridge or the video server to networks other than the operator's | S | I, T | `openamrobot-ui` (AoU) | H-12 |
| SR-10.03 | The safety functions SF-01…SF-03 shall not depend on any network interface (follows from SR-01.04, SR-02.06, SR-03.01) | S | A | WP-S-03 | H-12 |

## 11. Verification plan summary

| Function | Analysis | Test on the Gate A bench build | Validation (ISO 13849-2) |
|---|---|---|---|
| SF-01 | circuit review, category 3 argument, MTTFd/DC/CCF | each device, each channel open, welded-contact simulation, reset held | fault injection list of ISO 13849-2 Table D.x |
| SF-02 | field sizing from measured stopping distance | person-simulating test piece at field edge, each speed limit, reverse | repeat at worst-case load and battery |
| SF-03 | independence of the monitor | overspeed injection by a forced command above the limit | with SF-02 |
| SF-04 | timing budget | publisher kill, NaN command, agent kill, loop stall (watchdog) | with SF-01 reset |
| SF-05 | — | restart after each stop cause | — |
| SF-06 | — | driver fault injection, encoder disconnect, blocked wheel, low battery | — |
| SF-07 | image inspection | debug topics on the reference image; bounds on the bench image | — |

## 12. Open items

| ID | Item | Blocks |
|---|---|---|
| OI-1 | Every **(TBC)** value above: stopping distance, field sizes, crawl limit, stall thresholds, voltage limits | SR-02.02, SR-02.05, SR-03.02, SR-06.02, SR-06.05 |
| OI-2 | Interface change for SR-04.03 (stamped or sequenced command) | SF-04 Category 2 claim |
| OI-3 | ~~Choice of detection device~~ decided 2026-10-20 (DQ-007): front safety scanner plus rear bumper on the Gate A bench build; see WP-H-02 | closed |
| OI-4 | Safety controller for SF-02/SF-03 (safety relay with speed monitoring, or a small safety PLC) on the Gate A bench build; upstream 2.0 names a Pilz PNOZ s3 only | WP-S-03 |
| OI-5 | ~~DQ-006 (firmware ceiling values)~~ decided 2026-10-20: 0.25 m/s and 0.6 rad/s, applied in the fork firmware | closed |
| OI-6 | Add SR-08.x…SR-12.x (warning before motion, enabling control, base inhibit while an arm is unstowed, arm safe stop, lift and gripper holding) from WP-C-04 §3.8…§3.12; SR-05.x now carries PLr d; rewrite the "Implemented by" of SR-03, SR-04 and SR-06 for the firmware channel (DQ-014 B) | G1.8…G1.12 claims |
