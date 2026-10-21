# WP-S-02 Safety Requirements Specification (SRS) for the Safety Functions

| Field | Value |
|---|---|
| Work product | WP-S-02 Safety requirements specification: functional and integrity requirements of SF-01…SF-12 (ISO 13849-1 §5.1 "safety requirements specification") |
| Standard reference | ISO 13849-1:2023 §5 (safety functions, SRS), §4.5 (PLr), §6 (categories), §7 (software); ISO 13850:2015 §4; EN 60204-1:2018 §9.2.2, §9.2.3.4, §9.4; ISO 3691-4:2023 §4, Annex A; ISO 10218-2:2025 §5; ISO 13855:2024; ISO 13856-3; IEC 61496-3; IEC 62443-4-2 (CR 1, CR 3) |
| Version | 0.3 (2026-10-20): DQ-008 A, DQ-013 A, DQ-015 A, DQ-017 A and DQ-018 A applied (SR-06.02, SR-90.04, SR-01.03, SR-03.02 and SR-09.03, SR-02.04); rewritten from WP-C-04 v0.2: SF-08…SF-12 broken into requirements (SR-08…SR-12); the firmware is channel 1 of SF-03, SF-04, SF-06 and SF-09 (DQ-014 B), so SR-00.07, SR-00.08 and the "Implemented by" column name the channel; decided values written in (DQ-006 ceilings, DQ-007 scanner and bumper, DQ-021 monitored stop); a configuration column (CFG-001, CFG-002); the security block renumbered SR-90.xx so SR-10 is the base-inhibit function; Figures 17-1 and 18-1. 0.2: SF-05 raised to PLr d. 0.1: initial draft from WP-C-03 v0.2 |
| Status | Draft |
| PL / scope | PL d (SF-01, SF-02, SF-03, SF-05, SF-10, SF-11, SF-12), PL c (SF-04, SF-06, SF-09), PL b (SF-07, SF-08); CFG-001 Gate A unit (bench only, DQ-011 C) and CFG-002 2.0 mobile manipulator (unverified); the base with the arms and lift (DQ-004 B) |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1) |
| Approver | Project lead (self-approval as a recorded interim limitation, DQ-012) |
| Baseline | BL-001 |

> [!WARNING]
> Draft. The requirements are derived from WP-C-04 v0.2 and WP-C-03 v0.4. Numeric values marked **(TBC)**
> wait on the measurements of WP-C-01 §10 and WP-V-02. None of the requirements is implemented on either
> configuration; the "Implemented by" column names the design intent of WP-S-03 v0.3, not existing hardware or
> software. Every CFG-002 row rests on upstream's plan set. Clause references are to be checked against licensed
> copies (DQ-016: unscheduled).

## 1. Conventions

- `SR-<SF>.<nn>`: a requirement of safety function `SF-<SF>`; `SR-00.nn` applies to every function; `SR-90.nn` are
  the security requirements that support the functions. Shall-statements; one requirement, one testable property.
  IDs are never reused: the security block moved from `SR-10` to `SR-90` in v0.3 so that `SR-10` is SF-10.
- Attributes: **Type** (F functional, I integrity, T timing, D diagnostic, S security), **PLr** (from WP-C-04 §4),
  **Verif.** (A analysis, I inspection, T test, D demonstration; the method WP-S-09 and WP-V-01 use),
  **Implemented by** (the WP-S-03 element, naming the channel for two-channel functions), **Config** (CFG-001, CFG-002
  or both), **Trace** (hazards of WP-C-03 §4).
- Two-channel functions (DQ-014 B): SF-03, SF-04, SF-06 and SF-09 have **channel 1**, the base-controller firmware
  (the Teensy overlay on CFG-001, the STM32H723 firmware on CFG-002), and **channel 2**, the hardwired monitor
  (speed monitor, driver fault inputs, hardware watchdog, enabling signal) into the safety relay K0. A requirement
  that names one channel is met by that channel alone; SR-00.07 binds the two.
- Timing values are the response from the demand at the sensor or button to the start of power removal or the
  controlled stop, measured at the driver input. Stopping distance is end-to-end, demand to standstill.
- "Independent of software" means: no microcontroller, no ROS 2 node, no network and no configuration file is in
  the path, and a failure of any of them cannot prevent the function. It applies to the chain-only functions
  SF-01, SF-02, SF-05, SF-10 and SF-12 and to channel 2 of the two-channel functions.

## 2. Requirements common to every safety function

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-00.01 | Every safety function shall be implemented by a safety-related part of the control system (SRP/CS) whose achieved PL is at least its PLr, demonstrated per ISO 13849-1 §4.5 (category, MTTFd, DCavg, CCF) and validated per ISO 13849-2 | I | d | A, T | WP-S-03, WP-H-03, WP-H-04 | both | H-01, H-02, H-13 |
| SR-00.02 | A safety function shall take priority over every other command to the same actuator, including the diagnostic and calibration paths, the manipulation server and the policy runtime | F | d | T | WP-S-03 §4 (arbitration); chain priority by power removal | both | H-02, H-04, H-13 |
| SR-00.03 | A chain-only function, and channel 2 of a two-channel function, shall fail to the safe state (actuator power removed, brake applied where fitted, load held) on loss of its own supply, a broken wire, a short to supply or ground in its channel, or loss of the monitoring device | I | d | A, T | WP-S-03 §3 | both | H-02, H-14 |
| SR-00.04 | The state of every safety function (demanded, tripped, reset required, fault) shall be indicated at the robot and reported to the operator interface; the indication shall not be the only means of reset | F | c | I, T | WP-S-03 §6; SF-08 stack light | both | H-05, H-10 |
| SR-00.05 | Safety-related parameters (speed limits per zone, the carry limit, field sets, timeouts, thresholds, the station workspace, the warning time) shall be stored in a form that cannot be changed from the network at runtime; a change requires a build or a locked configuration step and is recorded under WP-P-02 | S, I | d | I | WP-S-03 §5; WP-W-09 | both | H-12, H-02 |
| SR-00.06 | Channel 1 of SF-03, SF-04, SF-06 and SF-09 is safety-related embedded software at PL d and shall meet ISO 13849-1 §7 (SRESW): specification (WP-W-02), structured design (WP-W-03), coding rules and static analysis (WP-W-01, WP-W-05), verification by review and test with coverage (WP-W-06, WP-W-07), validation on the target (WP-W-08), configuration management with a reproducible build (WP-P-01) | I | d | I, T | WP-W-01…WP-W-08 | both | H-01, H-03, H-11 |
| SR-00.07 | For a two-channel function, channel 2 shall detect a failure of channel 1 (loss of its heartbeat, a disagreement between the speeds the two channels report beyond the following-error limit, a missed demand) and reach the safe state within the function's response time without channel 1; the two channels shall use different sensors and different technology, scored for common cause in WP-H-04 | I, D | d | A, T | WP-S-03 §3.5 | both | H-01, H-03, H-02 |
| SR-00.08 | A requirement marked CFG-002 applies only to the 2.0 mobile manipulator and shall be re-verified against that design when it is public; a requirement marked CFG-001 applies to the Gate A unit on the bench only (DQ-011 C) | I | — | I | WP-C-01 §1 | both | H-13 |

## 3. SF-01 Emergency stop (PLr d, Category 3, stop category 0, chain only)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-01.01 | The robot shall have at least two emergency-stop devices per ISO 13850: red mushroom head on yellow background, positive-opening contacts (IEC 60947-5-5), latching, reset only by deliberate action at the device; on CFG-002 the base-front device and the chest button of the OpenArm kit (upstream `SAFETY-PROCUREMENT`) | F | d | I | WP-S-03 §3.1; E1 Schneider XB4BS8445 + ZBE-102 | both | H-01, H-02, H-04 |
| SR-01.02 | Emergency-stop devices shall be reachable without stepping into the path of the robot from the operator position and from each long side of the robot; the operator shall hold a pendant emergency stop during teleoperation and testing, wired into the same chain | F | d | I, D | WP-S-03 §3.1 | both | H-01, H-10 |
| SR-01.03 | Actuating any emergency-stop device shall remove power from both traction drivers within 200 ms (stop category 0, DQ-015 A) and, where a brake is fitted, apply the brake | F, T | d | T | WP-S-03 §3.2 (safety relay K0, contactors K1/K2) | both | H-01, H-02 |
| SR-01.04 | The emergency-stop function shall be hardwired and independent of software (§1 definition); no state of the compute module, the base controller, the agent, the network or the browser shall delay or prevent it | I | d | A, T | WP-S-03 §3.2 | both | H-02, H-10, H-11 |
| SR-01.05 | The function shall be dual channel (two contacts per device, two channels to the safety relay, two series contactors or two independent power-removal paths), with cross-monitoring so that a single fault is detected at or before the next demand (Category 3) | I, D | d | A, T | WP-S-03 §3.2 | both | H-02 |
| SR-01.06 | The safety relay shall have a monitored manual reset: motion is enabled again only after every emergency-stop device is released **and** the reset input is actuated and released; a reset held permanently or shorted shall not enable motion | F | d | T | WP-S-03 §3.3 | both | H-05 |
| SR-01.07 | The contactor (or power-removal path) feedback shall be monitored in the reset loop (external device monitoring); a welded or stuck contact shall prevent reset | D | d | T | WP-S-03 §3.2 | both | H-02, H-05 |
| SR-01.08 | The emergency-stop state shall be read by the firmware as a diagnostic input and reported (SR-00.04) without the firmware being in the stop path | D | c | T | WP-S-03 §6; firmware `/firmware/status` | both | H-10 |
| SR-01.09 | The on-screen stop of the operator interface shall be labelled as a software stop request, not as an emergency stop, and shall not be red-mushroom styled | F | — | I | `openamrobot-ui` (out of item; AoU) | both | H-10 |
| SR-01.10 | On CFG-002 the emergency stop shall remove actuator power from both arms and the lift as well as from traction (upstream `ESTOP-SCOPE`); the lift and the grippers shall hold their load through it (SF-12); the compute module and the logic rails may stay powered | F | d | T | WP-S-03 §7 (K1/K2 on the actuator power) | CFG-002 | H-13, H-14 |

## 4. SF-02 Protective stop on personnel detection (PLr d, Category 3, stop category 1 then 0, chain only)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-02.01 | The robot shall detect a person in its direction of travel with a safety laser scanner at the front (type 3 per IEC 61496-3, two OSSD outputs, PL d) and a safety-rated bumper at the rear (pressure-sensitive edge with monitoring unit, ISO 13856-3, PL d), both wired into the chain (DQ-007), and shall stop before contact | F | d | T | WP-S-03 §3.4; WP-H-02 E5a, E5b | both | H-01 |
| SR-02.02 | The protective field in the direction of travel shall be at least `L = v·t_r + d_b + K·(t_r + t_b) + Z + C` of WP-C-06 §3 for the active speed limit, with K = 1.6 m/s, t_r the measured reaction time, d_b and t_b the measured coasting or braked stop, Z the scanner tolerance and C the intrusion allowance; a field set shall exist per speed limit of SF-03; the 1.0 m starting value is a placeholder until WP-V-02 | F | d | A, T | WP-S-03 §3.4; WP-S-04; WP-V-02 | both | H-01 |
| SR-02.03 | Detection shall cover objects from the floor to at least 0.3 m **(TBC)** in the direction of travel; a 2D scan plane alone at 0.18 m or 0.22 m does not satisfy this without a bumper or a second plane (WP-C-06 HR-02) | F | d | A, T | WP-S-03 §3.4 | both | H-01 |
| SR-02.04 | Reverse motion (undock only: the Nav2 back-up recovery is removed, DQ-018 A) shall be covered by the rear bumper and limited to the reverse crawl limit of 0.05 m/s (SR-03.02); no reverse above the crawl limit without rear detection | F | d | T | WP-S-03 §3.4; speed monitor direction rule | both | H-01 |
| SR-02.05 | A field violation shall produce a controlled stop (deceleration within the stability limit of WP-C-01 §4.1, stop category 1) followed by power removal if standstill is not reached within 1 s **(TBC)** | F, T | d | T | WP-S-03 §3.4 | both | H-01, H-06 |
| SR-02.06 | Loss, error state or stale data of the detection device shall trigger the stop within the device's response time; the OSSD state and the bumper monitor's safety outputs, not a data stream over the network, shall be the stop signal; the function shall be independent of the navigation LiDAR | I, D | d | T | WP-S-03 §3.4 | both | H-11 |
| SR-02.07 | The protective function shall not be deactivated by software for any manoeuvre; where a dock approach needs a reduced field, the reduced field shall be a field-switching function of the safety device at PL d, selected by a safe input, with the dock approach limited to the crawl speed | F | d | A, T | WP-S-03 §3.4; docking redesign (GAP-15) | both | H-01 |
| SR-02.08 | After a protective stop, motion shall resume only when the field is clear, after the warning of SF-08 and, for a stop that removed power, after the reset of SR-01.06 | F | c | T | WP-S-03 §3.3 | both | H-05 |
| SR-02.09 | The lateral margin of the field shall exceed the footprint by Z plus the lateral sway of the robot **(TBC)** on each side; the navigation filter's side masks shall not apply to the safety scanner (WP-C-06 IS-03) | F | d | A, T | WP-S-03 §3.4 | both | H-01 |
| SR-02.10 | On CFG-002 a carry field set shall cover the carry footprint of the arms and the sweep of a turn at the carry limit (WP-C-06 CA-07, IS-15), selected while SF-10 reports the carry pose | F | d | A, T | WP-S-03 §3.8 | CFG-002 | H-13, H-01 |

## 5. SF-03 Safely-limited speed (PLr d, Category 3, stop category 1 then 0, two channels)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-03.01 | Channel 1 (firmware) shall measure each wheel's speed from the wheel encoders at the control rate and compare it with the active limit; channel 2 (speed monitor) shall measure each wheel's speed from a source independent of channel 1's encoders (the driver `SPD/DO2` pulse outputs on CFG-001, the hub-motor encoders on CFG-002) and compare it with the same limit | I | d | A, T | WP-S-03 §3.5 | both | H-01, H-03 |
| SR-03.02 | The monitored speed shall not exceed the limit of the active zone: 0.20 m/s linear and 0.5 rad/s in the navigation zone; with a person in the zone, 0.3 m/s while a safety-rated detection means is active and 0 m/s (standstill) without one (DQ-017 A); 0.05 m/s in reverse (DQ-018 A) and the crawl limit 0.05 m/s **(TBC)** in the dock lane; the limits are safety parameters (SR-00.05) selected through a safe input, never from the network | F | d | T | WP-S-03 §3.5 | both | H-01 |
| SR-03.03 | A violation sustained for more than 100 ms on either channel shall trigger a controlled stop and, if standstill is not reached within 1 s **(TBC)**, power removal; the trip shall latch until reset (SR-01.06) | F, T | d | T | WP-S-03 §3.5 | both | H-01, H-03 |
| SR-03.04 | Channel 1 shall refuse any velocity command above a fixed ceiling at the command input: 0.25 m/s and 0.6 rad/s (DQ-006, option A); a bench image may override the defines and shall report it (SR-07.02) | F | d | T | firmware `twistCallback` (fork change fe673fb) | both | H-12, H-01 |
| SR-03.05 | A difference between the speeds the two channels report beyond 30 % for 500 ms **(TBC)** shall be treated as a drive fault (SF-06) and shall trip channel 2 (SR-00.07) | D | d | T | WP-S-03 §3.5 | both | H-03 |
| SR-03.06 | On CFG-002 the carry limit 0.3 m/s **(TBC)** shall be the active limit whenever SF-10 reports the carry pose, and 0 whenever an arm is outside the stowed or carry pose | F | d | T | WP-S-03 §3.5, §3.8 | CFG-002 | H-13, H-15 |

## 6. SF-04 Stop on loss of command, communication or control (PLr c, Category 2, stop category 0, two channels)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-04.01 | If no valid velocity command is received for 200 ms, channel 1 shall set the drives to zero and, where a brake is fitted, apply the brake | F, T | c | T | firmware watchdog (exists) | both | H-02, H-11 |
| SR-04.02 | A velocity command shall be valid only if every field is finite and within the ceilings of SR-03.04; an invalid command shall count as no command and shall not feed the watchdog | F | c | T | firmware `twistCallback` (fork change) | both | H-02 |
| SR-04.03 | A command shall carry a monotonically increasing sequence number or a timestamp from the host; a repeated or out-of-order command shall count as no command **(open: needs an interface change, `TwistStamped` or a wrapped message)** | F | c | T | WP-S-03 §5; ROS 2 interface change | both | H-02 |
| SR-04.04 | Channel 2 shall run a hardware watchdog on channel 1's heartbeat with a timeout of at most 1 s; a missed heartbeat shall trip K0 and the trip shall latch; channel 1 shall report its reset cause after a watchdog reset | I, D | c | T | WP-S-03 §3.5; firmware WDOG1 (fork change) | both | H-11 |
| SR-04.05 | Loss of the agent or compute link, of the detection device (per SR-02.06) or of the safety controller heartbeat shall stop the robot within the respective timeout; the stop shall latch when it results from a fault (not from a normal end of session) | F | c | T | firmware agent-loss stop (exists); WP-S-03 §3.5 | both | H-11 |
| SR-04.06 | The host shall not re-feed a stale command: the velocity smoother shall publish zero after its timeout (exists, 1 s) and no node shall republish a command older than 200 ms | F | c | I, T | `openamr-platform-sw` nav2 chain, docking sequencer | both | H-02 |

## 7. SF-05 Prevention of unexpected start-up (PLr d, Category 3, chain only)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-05.01 | After SF-01, SF-02 (with power removal), SF-03, SF-04 on a fault, SF-06, SF-10 or a power cycle, the robot shall not move until a deliberate reset at the robot (SR-01.06); the first motion after reset shall need a fresh velocity command | F | d | T | WP-S-03 §3.3 | both | H-05 |
| SR-05.02 | A reset shall not be possible while a stop demand is present, and shall not itself cause motion | F | d | T | WP-S-03 §3.3 | both | H-05 |
| SR-05.03 | A pending or latched stop shall be indicated at the robot (lamp, stack light) and on the operator interface | F | d | I | WP-S-03 §6; SF-08 | both | H-05, H-10 |
| SR-05.04 | A reboot of the base controller shall report its reset cause and shall not re-enable motion by itself (exists in part: status topic; the enable path is WP-S-03 §3.3) | D | d | T | firmware status (fork change); WP-S-03 §3.3 | both | H-05 |

## 8. SF-06 Stop on drive fault (PLr c, Category 2, stop category 0, two channels)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-06.01 | The fault output of each motor driver (`ERR/DO1` on CFG-001; the ZLAC8015D fault state on CFG-002) shall be read by channel 2; a driver fault shall stop both drives within 100 ms and latch | F, D | c | T | WP-S-03 §3.5; channel 2 input | both | H-03 |
| SR-06.02 | Channel 1 shall treat a drive commanded above 60 % of maximum PWM whose measured speed stays below 2 rpm for 1 s as stalled or encoder-dead (DQ-008 A; the thresholds are tuned by the bench test of WP-W-08 and recorded under WP-W-09): both drives stop and the fault latches | D | c | T | firmware stall detector (fork change) | both | H-03 |
| SR-06.03 | A following error (SR-03.05) shall stop both drives and latch | D | c | T | WP-S-03 §3.5 | both | H-03 |
| SR-06.04 | Encoder direction and count plausibility shall be checked by channel 1 at every start-up by a short, bounded test move with the enable path armed **(open: needs the enable path; today a manual checklist)** | D | c | T, D | WP-S-03 §3.5 | both | H-03 |
| SR-06.05 | Battery voltage shall be measured by channel 2 (an undervoltage relay on CFG-001; the BMS hard-fault contact on CFG-002); below 23 V **(TBC)** at rest or 22 V **(TBC)** under load on CFG-001, or on a BMS hard fault on CFG-002, the robot shall stop and refuse autonomous operation | D | c | T | WP-S-03 §3.6; E10; upstream `BMS-FAULTS` | both | H-03, H-09 |

## 9. SF-07 Powered-debug inhibit (PLr b, Category 1, firmware)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-07.01 | The reference (production) firmware image shall contain no path that drives the motors from raw PWM or changes control gains from the network | F | b | I, T | firmware `ENABLE_POWERED_DEBUG` off (fork change) | both | H-04, H-02, H-12 |
| SR-07.02 | A bench image that contains such paths, or that overrides the ceilings of SR-03.04, shall be identifiable at runtime (`/firmware/status dbg=1`) and shall bound every input it accepts (gains, right-wheel scale, feedforward, dither, calibration ratios) | F | b | T | firmware (fork change) | both | H-04 |
| SR-07.03 | Powered debug on a bench image shall additionally require a physical arming input (key switch or jumper read by the firmware) and shall time out after 10 min **(TBC)** without re-arming **(open)** | F | b | T | WP-S-03 §3.7 | both | H-04 |
| SR-07.04 | The per-boot encoder alignment procedure shall be possible without the raw-PWM path, or the raw-PWM path shall be limited during alignment to 25 % **(TBC)** PWM with wheels-off-ground confirmed by the operator **(open)** | F | b | T | firmware; `tools/encoder-calibration` | both | H-04 |

## 10. SF-08 Warning before motion (PLr b, Category 1, warning device)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-08.01 | Before the wheels turn after a reset, after a protective stop or slow-down whose field has cleared, after a wait on a person, before an undock reverse and at the start of teleoperation, the robot shall give an audible and a visual warning for at least 2 s **(TBC)** (WP-C-06 HR-06) | F, T | b | T | WP-S-03 §6; E7 sounder and stack light | both | H-05, H-10 |
| SR-08.02 | On CFG-002 the warning of SR-08.01 shall also precede the first arm motion at a station and every lift motion | F | b | T | WP-S-03 §3.8 | CFG-002 | H-13, H-15 |
| SR-08.03 | The robot's state shall be visible from every side: green running, amber slowed or waiting on a person, red stopped or fault, flashing red reset required (WP-C-06 HR-07); the UI shall show the same four states | F | b | I, D | E7 stack light; UI | both | H-05, H-10 |
| SR-08.04 | The warning shall be driven from the chain state and the motion request, not from the ROS 2 stack alone; a failed sounder or lamp shall be reported; the warning shall never delay a stop | I | b | T | WP-S-03 §6 | both | H-05 |

## 11. SF-09 Enabling control for teleoperation (PLr c, Category 2, stop category 0, two channels)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-09.01 | In teleoperation and mapping (M2, M5) channel 1 shall accept a velocity command only while the hold-to-run control of the teleoperation device is held (WP-C-06 HR-04); release shall set the drives to zero within 200 ms | F, T | c | T | firmware; teleoperation node | both | H-01, H-10 |
| SR-09.02 | Channel 2 shall take the enabling signal as a condition of K0's enable while teleoperation mode is selected; loss of the signal, of the device's link or of its battery shall count as a release | I | c | T | WP-S-03 §3.5 | both | H-01 |
| SR-09.03 | Teleoperation speed shall be capped at the zone limit (0.20 m/s); with a person in the zone it shall stay under the 0.3 m/s ceiling only while a safety-rated detection means is active, and shall be 0 m/s without one (DQ-017 A) | F | c | T | firmware ceiling per mode; SF-03 limit set | both | H-01 |
| SR-09.04 | The enabling device shall toggle at least once per session so that a stuck or shorted signal is detected by channel 2's watchdog channel | D | c | T | WP-S-03 §3.5 | both | H-01 |
| SR-09.05 | The pendant emergency stop of SR-01.02 shall be on the same device or in the same hand as the enabling control; the operator tablet of CFG-002 shall have no actuation path (upstream `hardware-architecture.md`) | F | c | I | WP-H-02 (teleoperation device); CFG-002 tablet | both | H-10 |

## 12. SF-10 Base motion inhibit while an arm is unstowed (PLr d, Category 3, stop category 0, chain only; CFG-002)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-10.01 | Each arm shall provide a dual-channel safe "stowed or carry pose" signal (a safe output of the arm controller or a mechanical pose switch per arm); absence or invalidity of the signal shall count as unstowed | I | d | A, T | WP-S-03 §3.8; arm pose signals (E12) | CFG-002 | H-13 |
| SR-10.02 | Traction power shall be enabled only while both pose signals are present; a base velocity command or measured base motion without them shall remove traction power within 200 ms and engage the brakes, latched until the pose signals return and, where power was removed, after the reset of SR-01.06 | F, T | d | T | WP-S-03 §3.8; K0 condition | CFG-002 | H-13, H-15 |
| SR-10.03 | The carry pose shall be a defined pose with the load inside the gripper's rated hold and below the payload limit (WP-C-06 CA-07); while it is reported, the active speed limit shall be the carry limit (SR-03.06) and the carry field set shall be selected (SR-02.10) | F | d | A, T | WP-S-03 §3.8 | CFG-002 | H-13, H-15 |
| SR-10.04 | Channel 1 shall cross-check the pose signals against the arms' joint states and report a disagreement (SR-00.04); the cross-check is diagnostic and shall not enable traction on its own | D | d | T | STM32 firmware | CFG-002 | H-13 |

## 13. SF-11 Arm safe stop on entry to the station workspace (PLr d, Category 3, stop category 1 then 0 for the arm; CFG-002)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-11.01 | Each station shall have a marked workspace monitored by a safety-rated detection device (a safety laser scanner field around the station or a safety mat, PL d); a person entering it while an arm moves shall stop every arm as a safety-rated monitored stop (DQ-021 A) | F | d | T | WP-S-03 §3.8; station device (E15), external safety controller (E13) | CFG-002 | H-13 |
| SR-11.02 | The workspace boundary shall be at least the arm's reach plus the distance a person walks at K = 1.6 m/s during the arm's response and stopping time (ISO 13855), with the arm's reach and stopping distance measured **(TBC: WP-C-01 OI-6, WP-V-03; planning value for the reach 0.6 m shoulder to fingertip, read from the OpenArm 2.0 description package's joint offsets, `assurance/sim/blender`)** | F | d | A, T | WP-S-04 | CFG-002 | H-13 |
| SR-11.03 | The stop shall start within 200 ms **(TBC)** of the demand and shall remove the arms' actuator power (safe torque off, or power removal through the chain) with the joint brakes and the grippers holding; the arm shall resume only on a deliberate action with the workspace clear and after the warning of SR-08.02 | F, T | d | T | WP-S-03 §3.8 | CFG-002 | H-13, H-14 |
| SR-11.04 | A hand-over shall be requested only with the arm stopped; the gripper shall open only on a deliberate operator action with the arm at rest (WP-C-06 CA-06); a hand-over request while the arm moves shall stop the arm | F | d | T | manipulation server with the chain condition | CFG-002 | H-13 |
| SR-11.05 | No power-and-force limiting and no speed-and-separation monitoring is claimed: no arm shall move with a person inside the workspace (WP-C-06 CA-02); AOU-10 holds until the station device exists | I | d | A | WP-C-06 §4 | CFG-002 | H-13 |
| SR-11.06 | Loss or fault of the station device shall stop the arms; the manipulation server and the policy runtime (F-16) shall be outside the function and unable to override it (IX-03) | I, D | d | T | WP-S-03 §3.8 | CFG-002 | H-13 |

## 14. SF-12 Lift and gripper holding on stop and power loss; lift interlock (PLr d, Category 3; CFG-002)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-12.01 | The lift shall hold its position without power, from the instant of power removal, with no drift beyond 5 mm **(TBC)** under the peak load at full extension (a brake or a self-locking drive, DM-07; upstream's DOLD holding release gate) | F | d | T | WP-S-03 §3.8; E14 | CFG-002 | H-14, H-15 |
| SR-12.02 | Each gripper shall hold its load without power (spring-closed or self-locking, DM-07) at the peak payload of 6.0 kg including the end effector; the payload limit shall be marked | F | d | T | gripper design (OpenArm, to be confirmed) | CFG-002 | H-14 |
| SR-12.03 | A lift motion command shall be refused unless the base is at standstill (channel 2 of SF-03), both arms report the stowed or carry pose (SR-10.01) and the keep-clear zone under the carriage and beside the column is clear (a safety mat or a scanner field) | F | d | T | WP-S-03 §3.8; lift enable condition | CFG-002 | H-15 |
| SR-12.04 | Lift motion shall be preceded by the warning of SR-08.02 and shall stop on an emergency stop (SR-01.10) and on entry to the keep-clear zone within 200 ms **(TBC)** | F, T | d | T | WP-S-03 §3.8 | CFG-002 | H-15 |
| SR-12.05 | The holding functions of SR-12.01 and SR-12.02 shall be proven by test: power loss and emergency stop under the peak load at full extension, repeated 10 times **(TBC)**, with drift measured over 1 h **(TBC)** | I | d | T | WP-V-05 | CFG-002 | H-14 |
| SR-12.06 | A gripper over-payload or a holding failure shall be reported (SR-00.04); it is a load drop (H-14) and shall stop the arms and the lift | D | d | T | WP-S-03 §3.8 | CFG-002 | H-14 |

## 15. Security requirements supporting the safety functions (IEC 62443-4-2, target DQ-013)

| ID | Requirement | Type | PLr | Verif. | Implemented by | Config | Trace |
|---|---|---|---|---|---|---|---|
| SR-90.01 | Velocity, docking, manipulation, lift, lifecycle and parameter interfaces shall be reachable only by authenticated participants (SROS2 enclaves with access control, or an isolated robot network with no external participant) | S | — | I, T | WP-C-08 / WP-S-07 (cybersecurity concept) | both | H-12 |
| SR-90.02 | The operator interface shall authenticate operators and shall not expose rosbridge or the video server to networks other than the operator's | S | — | I, T | `openamrobot-ui` (AoU) | both | H-12 |
| SR-90.03 | The chain-only functions SF-01, SF-02, SF-05, SF-10 and SF-12, and channel 2 of SF-03, SF-04, SF-06 and SF-09, shall not depend on any network interface (follows from SR-01.04, SR-02.06, SR-03.01, SR-00.03) | S | — | A | WP-S-03 | both | H-12 |
| SR-90.04 | Channel 1 of SF-03, SF-04, SF-06 and SF-09 takes its command from the network: a corrupted, replayed or malicious command shall be bounded by SR-03.04 and SR-04.02 and detected by channel 2 (SR-00.07); the firmware's command input is an input to a safety-related part and shall be covered by WP-S-07 at SL 2 for integrity and restricted data flow (DQ-013 A; WP-C-08 §2) | S, I | — | A, T | WP-S-07; WP-C-08 | both | H-12, H-01 |

## 16. Requirements allocated to the firmware channel

The following requirements are met by channel 1 and are the input to the software safety requirements of WP-W-02:
SR-03.01 (channel 1 part), SR-03.03, SR-03.04, SR-03.05 (reporting), SR-03.06, SR-04.01, SR-04.02, SR-04.03,
SR-04.04 (heartbeat and reset cause), SR-04.05, SR-05.04, SR-06.02, SR-06.03, SR-06.04, SR-07.01…SR-07.04,
SR-09.01, SR-09.03, SR-10.04, SR-01.08 and SR-00.04 (reporting). Each of them carries SR-00.06 (the SRESW
lifecycle at PL d) and SR-00.07 (detection of the channel's failure by channel 2). The requirements met by the ROS 2
stack (SR-04.06, SR-01.09, SR-90.01, SR-90.02) are functional or security requirements with no PL claim.

## 17. Verification plan summary

| Function | Analysis | Test on the bench build (CFG-001, wheels off the ground) or on CFG-002 | Validation (ISO 13849-2) |
|---|---|---|---|
| SF-01 | circuit review, category 3 argument, MTTFd/DC/CCF | each device, each channel open, welded-contact simulation, reset held; on CFG-002 the arm and lift power paths | fault injection list of ISO 13849-2 Table D.x |
| SF-02 | field sizing from measured stopping distance (WP-S-04) | person-simulating test piece at field edge, each field set including the carry set, reverse into the bumper | repeat at worst-case load and battery (CFG-002) |
| SF-03 | independence and diversity of the two channels; the SRESW evidence of channel 1 | overspeed injection by a forced command above the limit on each channel separately; channel disagreement | with SF-02 |
| SF-04 | timing budget; watchdog window | publisher kill, NaN command, agent kill, loop stall (hardware watchdog), heartbeat loss | with SF-01 reset |
| SF-05 | — | restart after each stop cause; reset held; reset with a demand present | — |
| SF-06 | — | driver fault injection, encoder disconnect, blocked wheel, low battery, channel disagreement | — |
| SF-07 | image inspection | debug topics on the reference image; bounds and arming on the bench image | — |
| SF-08 | — | warning timing before each start cause; visibility from every side | — |
| SF-09 | — | release during motion, link loss, stuck signal, speed cap near a test piece | — |
| SF-10 | pose signal architecture | base command with an arm raised; pose signal broken during a move; carry pose geometry against the carry field | CFG-002 only |
| SF-11 | workspace boundary from reach and stopping distance (WP-S-04) | entry into the workspace at working speed with a test piece; hand-over request during motion; station device loss | CFG-002 only |
| SF-12 | holding by design (DM-07) | power loss and emergency stop under peak load at full extension, repeated; drift over time; lift command with the base moving, an arm raised, the keep-clear zone occupied | CFG-002 only |

![Figure 17-1: stacked horizontal bars, one per safety function and one for the common and security blocks, showing how many requirements each verification method covers: analysis, inspection, test and demonstration; test dominates every bar and the three CFG-002 functions are marked](figures/fig-s02-17-1-verification-methods.svg)

*Figure 17-1.* How many requirements of each block each verification method covers, counted from the Verif. column. Test is the method of record for most of them; the analysis-only rows are the ones whose evidence is a document (the SRESW lifecycle, the field derivation, the independence argument). Generated by [`figures/fig_s02.py`](figures/fig_s02.py) from the requirement tables; CI fails if it is stale.

## 18. Traceability

| Function | Requirements | PLr (WP-C-04 §4) | Hazards (WP-C-03 §4) | Claim (WP-K-01) |
|---|---|---|---|---|
| common | SR-00.01…SR-00.08 | d | all | G1 |
| SF-01 | SR-01.01…SR-01.10 | d | H-01, H-02, H-04, H-05, H-10, H-11, H-13, H-14 | G1.1 |
| SF-02 | SR-02.01…SR-02.10 | d | H-01, H-05, H-06, H-11, H-13 | G1.2 |
| SF-03 | SR-03.01…SR-03.06 | d | H-01, H-03, H-12, H-13, H-15 | G1.3 |
| SF-04 | SR-04.01…SR-04.06 | c | H-02, H-11 | G1.4 |
| SF-05 | SR-05.01…SR-05.04 | d | H-05, H-10 | G1.5 |
| SF-06 | SR-06.01…SR-06.05 | c | H-03, H-09 | G1.6 |
| SF-07 | SR-07.01…SR-07.04 | b | H-02, H-04, H-12 | G1.7 |
| SF-08 | SR-08.01…SR-08.04 | b | H-05, H-10, H-13, H-15 | G1.8 |
| SF-09 | SR-09.01…SR-09.05 | c | H-01, H-10 | G1.9 |
| SF-10 | SR-10.01…SR-10.04 | d | H-13, H-15 | G1.10 |
| SF-11 | SR-11.01…SR-11.06 | d | H-13, H-14 | G1.11 |
| SF-12 | SR-12.01…SR-12.06 | d | H-14, H-15 | G1.12 |
| security | SR-90.01…SR-90.04 | — | H-01, H-12 | G3.1 |

![Figure 18-1: requirement map: one row per safety function with its name and required Performance Level, and along the row one chip per requirement coloured by type, functional, integrity, timing, diagnostic or security, with a dashed border on requirements that exist only on the 2.0 configuration and a small dot on requirements that still carry a value to be confirmed](figures/fig-s02-18-1-requirement-map.svg)

*Figure 18-1.* Every requirement of this document as a chip on its function's row, coloured by type. The dashed chips exist only on CFG-002; the dotted ones still carry a value to be confirmed, which is where the measurement programme of WP-V-02 and WP-V-03 lands. Generated by [`figures/fig_s02.py`](figures/fig_s02.py) from the requirement tables; CI fails if a requirement's hazard is not in WP-C-03 §4 or a function's PLr disagrees with WP-C-04 §2.

## 19. Open items

| ID | Item | Blocks |
|---|---|---|
| OI-1 | Every **(TBC)** value above: stopping distance and field sizes (WP-V-02), the dock-lane crawl and the carry limit, voltage limits, warning time, arming time-out, the arm's reach and stopping distance, the lift drift and test repetitions; the stall thresholds (DQ-008 A), the speed with a person in the zone (DQ-017 A) and the reverse limit (DQ-018 A) are decided | SR-02.02, SR-02.05, SR-03.02, SR-03.06, SR-06.05, SR-08.01, SR-11.02, SR-12.01, SR-12.05 |
| OI-2 | Interface change for SR-04.03 (stamped or sequenced command) | SF-04 Category 2 claim |
| OI-3 | ~~Choice of detection device~~ decided 2026-10-20 (DQ-007): front safety scanner plus rear bumper; see WP-H-02 | closed |
| OI-4 | Safety controller for SF-02, SF-03 and, on CFG-002, SF-10…SF-12 (a safety speed monitor plus the PNOZ s3, or a small safety PLC); upstream 2.0 names a Pilz PNOZ s3 only | WP-S-03 |
| OI-5 | ~~DQ-006 (firmware ceiling values)~~ decided 2026-10-20: 0.25 m/s and 0.6 rad/s, applied in the fork firmware | closed |
| OI-6 | ~~Add SR-08…SR-12 and rewrite the "Implemented by" of SR-03, SR-04, SR-06 for the firmware channel~~ done in v0.3 | closed |
| OI-7 | Derive the software safety requirements of WP-W-02 from §16, and the chain I/O of WP-S-05 from the channel 2 inputs named here | WP-W-02, WP-S-05 |
| OI-8 | Put to upstream: the OpenArm 2.0 pose outputs, safe torque off, reach and stopping distance; the gripper's behaviour on power loss; the DOLD holding evidence (SR-10.01, SR-11.02, SR-11.03, SR-12.01, SR-12.02) | every CFG-002 row |
| OI-9 | ~~The speed near a person (DQ-017) and the reverse rule (DQ-018) once answered~~ both A on 2026-10-20, applied in SR-03.02, SR-09.03, SR-02.04; the fork change for DQ-018 is tracked in the register | closed |
