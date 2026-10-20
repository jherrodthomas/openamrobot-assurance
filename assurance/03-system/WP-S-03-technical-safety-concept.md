# WP-S-03 Technical Safety Concept: the Stop Chain and the Safety-Related Control Architecture

| Field | Value |
|---|---|
| Work product | WP-S-03 Technical safety concept: architecture of the safety-related parts of the control system that implement SF-01…SF-07 |
| Standard reference | ISO 13849-1:2023 §6 (designated architectures, categories), §6.1.3 (Category 2), §6.1.4 (Category 3), Annex I (examples); ISO 13849-2:2012 Annex D; EN 60204-1:2018 §9.2, §9.4; ISO 3691-4:2023 §4; IEC 60947-5-5 |
| Version | 0.3 (2026-10-20): DQ-014 B applied: the base-controller firmware is channel 1 of SF-03, SF-04, SF-06 and SF-09, the hardwired monitor channel 2 (§2, §3.5); CFG-002 is the hardware reference (DQ-020 A) and §7 lists its chain elements and the arm and lift functions SF-10…SF-12 (§3.8). Previous: 0.2 (2026-10-20): DQ-007 applied in §3.4. 0.1: initial draft |
| Status | Draft |
| PL / scope | PL d; Gate A unit (CFG-001) bench build, with the mapping to upstream's OpenAMRobot 2.0 safety chain |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1, electrical) |
| Approver | Project lead |
| Baseline | BL-001; requirements WP-S-02 v0.1 |

> [!WARNING]
> Draft design intent. Nothing in this document is built. Part numbers for the Gate A bench build are proposals
> to be confirmed by the electrical reviewer; the 2.0 parts are quoted from upstream's register and are not
> verified. MTTFd, DCavg and CCF are not yet calculated (WP-H-03).

## 1. The argument in one paragraph

The Gate A unit has the right shape and the wrong last stage: a large ROS 2 stack feeds a small microcontroller,
but that microcontroller is the only thing between a command and the motors, and it cannot stop the robot
against itself. The concept adds a **hardwired stop chain** below the microcontroller (safety relay, contactors,
driver brake inputs) that removes traction power on an emergency stop, a protective-field violation, an overspeed
or a drive fault, and that must be reset deliberately. The microcontroller keeps its functional watchdog and gains
a hardware watchdog, command validation and a fault detector, which are functional measures that reduce demands on
the chain; they carry no PL claim on their own. Personnel detection and speed monitoring are done by safety-rated
devices wired into the chain, never by the ROS 2 stack. This was the doer/checker split of the assurance strategy (WP-M-01 §6) with
the checker in copper. On 2026-10-20 the lead decided (DQ-014, option B) that the firmware is **inside** the
safety-related control system for the speed and loss-of-control functions: SF-03, SF-04, SF-06 and SF-09 are
two-channel functions whose channel 1 is the base-controller firmware and whose channel 2 is the hardwired monitor
(§3.5), while SF-01, SF-02, SF-05, SF-10 and SF-12 stay on the chain alone. The firmware therefore carries a PL
claim and the ISO 13849-1 §7 lifecycle (WP-W-02…WP-W-08); its hardening is the first increment of that evidence.

The chain has no network input: every element that can stop the robot is wired, so no input of the safety chain is reachable from the network; the cybersecurity architecture ([WP-S-07](WP-S-07-cybersecurity-architecture.md)) keeps it a zone of its own. The
firmware channel of SF-03, SF-04, SF-06 and SF-09 does take its command from the network; a corrupted or
malicious command is bounded by the firmware's validation and caught by the hardware channel, and WP-S-07 treats
the firmware's command input as an input to a safety-related part (WP-C-08, DQ-013).

## 2. Allocation of safety functions to elements

| Element | Role | SF-01 | SF-02 | SF-03 | SF-04 | SF-05 | SF-06 | SF-07 |
|---|---|---|---|---|---|---|---|---|
| E1 Emergency-stop devices (2×, dual contact) | input | ● | | | | | | |
| E2 Safety relay K0 (dual-channel, monitored reset, 2 enabling outputs) | logic | ● | ● | ● | ● | ● | ● | |
| E3 Traction power removal: contactors K1, K2 in series on the driver 24 V, with mirror contacts into the K0 reset loop | output | ● | ● | ● | ● | | ● | |
| E4 Driver brake / enable inputs (`BRK/DI5`) driven from a K0 output, as the second shut-off path | output | ● | ● | ● | | | ● | |
| E5 Safety-rated personnel detection (safety laser scanner with OSSD pair, or safety bumpers) | input | | ● | | | | | |
| E6 Speed monitor (safety speed-monitoring relay or safety PLC reading the driver `SPD/DO2` pulse outputs or a second encoder channel) | logic | | | ● | | | ● | |
| E7 Reset button and stop/reset lamp | input/indication | ● | ● | ● | | ● | | |
| E8 Base-controller firmware (Teensy on CFG-001, STM32H723 on CFG-002): channel 1 of the two-channel functions, SRESW at PL d | channel 1 | diag. input | | ● (encoder speed, ceiling, zone limit) | ● (watchdog, validation) | reset cause | ● (stall, following error, fault input) | ● |
| E9 Pi 5 / ROS 2 stack (functional, QM) | functional | none | none | none | ● (smoother timeout) | indication | | |
| E10 Battery monitor (voltage into E6 or E8) | input | | | | | | ● | |
| E11 Fuse F0 and lockable disconnect | complementary (DM-04) | | | | | | | |

Rule (DQ-014 B): E9 is never in the stop path; it may **demand** a stop through K0 but its failure cannot prevent
one. E8 is channel 1 of SF-03, SF-04, SF-06 and SF-09 and never their only channel: channel 2 (E6, the driver fault
inputs, the hardware watchdog and the enabling signal into K0) detects the failure of E8 and stops the robot without
it. SF-01, SF-02, SF-05, SF-10 and SF-12 do not depend on E8 at all.

The functions SF-08…SF-12 of WP-C-04 v0.2 are allocated as follows: SF-08 (warning) to E7 driven by the chain
state and the motion request; SF-09 (enabling control) to E8 as channel 1 and the enabling signal into K0 as
channel 2; SF-10 (base inhibit while an arm is unstowed), SF-11 (arm safe stop) and SF-12 (lift and gripper holding,
lift interlock) to the CFG-002 elements of §3.8 and §7.

## 3. Architecture

### 3.1 Emergency-stop devices (SR-01.01, SR-01.02)

Two devices on the Gate A unit: the existing front-panel mushroom replaced by a certified device with two NC
contacts (IEC 60947-5-5, positive opening), and a second device on the rear or on the top plate. Both wired in
series per channel into K0's two input channels (channel 1: contact 1 of each device; channel 2: contact 2),
so any device opens both channels. Cabling per EN 60204-1 (short to supply detected by K0 cross-monitoring).

### 3.2 Safety relay and power removal (SR-01.03…SR-01.07): Category 3

Designated architecture of ISO 13849-1 Category 3: two channels from input to output, cross-monitored, with a
single fault not leading to loss of the function.

```
E-stop 1 ──┬── ch1 ──┐                      ┌── K1 coil ──┐
E-stop 2 ──┘         │   K0 safety relay    │             ├─ driver 24 V (both drivers)
Scanner OSSD1 ──────►│  (dual input, cross- ├─ out 13/14 ─┤   K1 ─── K2 ─── V+ drivers
Scanner OSSD2 ──────►│   monitored, manual  │             │
Speed monitor OK ───►│   monitored reset)   ├─ out 23/24 ─┴── K2 coil
                     │                      │
Reset button ───────►│  S34 reset ◄─────────┼── K1 NC mirror ── K2 NC mirror (EDM loop)
                     │                      ├─ out 33/34 ── driver BRK/DI5 (both) [second path]
Teensy WDT/fault ───►│  (optional demand)   └─ aux ─────────► Teensy diagnostic input, lamp
```

- K0: a two-channel safety relay with monitored manual reset and external-device monitoring (EDM). Upstream's 2.0
  choice is a Pilz PNOZ s3 (750103); the same class suits the bench build.
- K1, K2: two contactors rated for the traction supply in series (two independent interruptions). On Gate A the
  traction current is small (2 × 7.5 A drivers, 7 Ah battery); on 2.0 upstream specifies Gigavac GX11CAC with
  mechanically linked NC auxiliaries. Mirror contacts of K1 and K2 are wired in series into the K0 reset loop, so a
  welded contactor prevents reset (SR-01.07).
- Second shut-off path: a K0 output drives the ZBLD drivers' `BRK/DI5` inputs (hardware brake/inhibit on the
  driver). Even if K1/K2 both weld, the drivers are inhibited. Whether `BRK/DI5` is a dynamic brake or a coast
  inhibit is to be read from the ZBLD.C20 manual (not in the repository; WP-H-02 OI).
- The stop is category 0 (immediate power removal). With no holding brake on the Gate A drive the robot coasts;
  the stopping distance under category 0 must be measured (WP-C-01 OI-2) and bounds the SF-02 field (SR-02.02).
  On 2.0 the hub-motor brakes engage on power removal (upstream `ESTOP-SCOPE`), making it a braked stop.
- Response: K0 drop-out ≤ 30 ms class devices plus contactor opening ≤ 50 ms, inside the 200 ms of SR-01.03.

### 3.3 Reset and indication (SR-01.06, SR-05.01…SR-05.04)

One reset button (upstream 2.0: Schneider XB4BW36B5 with lamp) into K0's monitored reset input: K0 enables only
on the falling edge of the reset after all demands are clear. The lamp shows "reset required". The reset state
is also read by the Teensy as a diagnostic input and published in `/firmware/status`; the UI shows it but
cannot clear it.

### 3.4 Personnel detection (SR-02.01…SR-02.08): Category 3

- **Decided (DQ-007, 2026-10-20):** a safety laser scanner (type 3, IEC 61496-3) with two OSSD outputs into a K0
  input pair, mounted low at the front with its plane at ≤ 0.2 m and field sets switched by speed (through safe
  inputs tied to the speed monitor or to zone selection), **plus a safety-rated bumper at the rear** (pressure-sensitive
  edge with a monitoring unit, PL d) for the reverse case (SR-02.04). Upstream's RPLIDAR S3 stays the navigation
  sensor; it is not a safety device. Parts, wiring and budget: [WP-H-02](../04-hardware/WP-H-02-electrical-and-safety-chain-design.md).
- Reverse is limited to the crawl speed where the bumper is the only detection (contact before stop).
- Field sizing: `L_field ≥ v_max × (t_scanner + t_K0 + t_contactor) + d_stop(v_max) + margin`, with `d_stop` the
  measured category 0 coasting distance (or braked distance on 2.0). At 0.20 m/s and an assumed coast of
  **(TBC)** this gives **(TBC)**; nothing is claimed until measured.
- Docking: the scanner's field is reduced to a dock-lane field set at the crawl limit through a safe field-switch
  input, never through a ROS 2 lifecycle transition (GAP-15). The dock itself is outside the field or masked by
  the scanner's own configuration, verified in validation.
- Reverse: without rear detection, reverse is inhibited above the crawl limit by the speed monitor's direction
  input, and the back-up recovery is disabled in the Nav2 configuration (GAP-35).

### 3.5 Speed monitoring, loss of control and drive faults (SR-03.01…SR-03.05, SR-04.01…SR-04.06, SR-06.01…SR-06.05): Category 3, two channels

Decided architecture (DQ-014 B): a two-channel structure in the sense of ISO 13849-1 Category 3, with diverse
channels.

- **Channel 1, the base-controller firmware (E8):** reads the wheel encoders, compares the measured speed with the
  active zone limit (a safety parameter, SR-00.05), validates and ceilings every command (SR-03.04, SR-04.02),
  runs the command watchdog (SR-04.01), the stall, following-error and encoder-plausibility detectors (SR-06.02…
  SR-06.04) and the enabling-signal check (SF-09); on any demand it sets PWM 0 and asserts the demand line into K0
  (E8 output through a 24 V relay). It is safety-related embedded software at PL d (ISO 13849-1 §7): reproducible
  build, coding rules, static analysis, unit and integration tests with coverage, a software safety analysis and
  independent review (WP-W-01…WP-W-08).
- **Channel 2, the hardwired monitor (E6 and the chain):** the speed monitor reads the driver pulse outputs
  (`SPD/DO2` on CFG-001, the hub-motor encoders on CFG-002), independent of channel 1's encoders, and holds a K0
  input enabled while in range and in the permitted direction; the driver fault outputs (`ERR/DO1`), the
  undervoltage relay (E10) and the enabling signal go to the monitor or to K0 directly; a hardware watchdog window
  of channel 1's heartbeat is a K0 condition. Over-speed, a fault or a lost heartbeat drops the input: K0 trips.
- **Cross-monitoring:** channel 2 compares its speed with the speed channel 1 reports on its diagnostic output and
  trips on a disagreement beyond the following-error limit (SR-03.05); channel 1 reads the chain state and reports
  a channel 2 trip it did not itself demand. Diagnostic coverage is claimed from this comparison and from the
  hardware watchdog (WP-H-03, WP-W-04).
- **Diversity:** different sensors (wheel encoders versus driver pulse outputs or motor encoders), different
  technology (software versus a certified relay), different suppliers; common-cause scoring in WP-H-04.
- The ROS 2 stack stays functional: the smoother timeout and the Nav2 limits are copies below the safety limits.

### 3.6 Battery monitoring (SR-06.05)

A voltage divider into the Teensy ADC (`BATTERY_PIN`, foreseen upstream but not implemented) for reporting, and a
voltage-monitoring relay with a hysteresis threshold into the K0 demand path for the stop. The BMS of 2.0 takes
this role (upstream `BMS-FAULTS`).

### 3.7 Powered-debug arming (SR-07.03)

A key switch read by the Teensy as the arming input for bench images; on the reference image the input is ignored
because the paths do not exist. The key switch position is reported in `/firmware/status`.

### 3.8 Arms and lift (CFG-002; SF-10, SF-11, SF-12)

- **SF-10 base inhibit while an arm is unstowed:** a "stowed or carry pose" signal per arm (a safe output of the
  arm controller, or a mechanical pose switch per arm, dual channel) is a condition of the traction enable in the
  safety controller; channel 1 cross-checks it against the joint states. No pose signal, no traction.
- **SF-11 arm safe stop:** the mode is DQ-021. In every mode an external safety controller (the PNOZmulti or
  Flexi-class device WP-H-02 proposes as option 2) takes the station's detection device (a scanner field around
  the station, or a safety mat) and, for power-and-force limiting, the arm's measured force or torque, and cuts
  the arms' actuator power through the chain (the K1/K2 path of `ESTOP-SCOPE` covers the arms) or asserts the
  arms' safe torque off if the OpenArm 2.0 controllers provide one, which is not published.
- **SF-12 lift and gripper holding, lift interlock:** holding is by design (DM-07: a brake or self-locking lift
  drive, a spring-closed or self-locking gripper) and proven by test (WP-V-05); the interlock is a condition of the
  lift enable in the safety controller on base standstill (channel 2 of SF-03), the arm pose signals (SF-10) and
  the keep-clear zone (a mat or a scanner field).

None of this exists in any repository; the OpenArm 2.0 safety functions and the DOLD holding evidence are the two
interface questions to put to upstream first.

## 4. Command arbitration (SR-00.02)

The safety chain has priority by construction: it removes power. Within the functional stack, a `twist_mux` with
the stop request at highest priority, then the docking sequencer, then teleoperation, then navigation, replaces the
free-for-all `/cmd_vel` (GAP-36). The mux is QM; its failure cannot defeat the chain.

## 5. Safety parameters (SR-00.05)

| Parameter | Lives in | Set by | Changed by |
|---|---|---|---|
| Speed limits per zone, direction rule | speed monitor configuration (device-locked) | commissioning | locked configuration step, WP-P-02 record |
| Protective field sets | scanner configuration (password-protected, checksum) | commissioning | same |
| Timeouts of K0 (reset mode, cross-fault detection) | relay DIP or rotary switch | commissioning | same |
| Firmware ceilings, stall thresholds, watchdog timeout | compile-time constants | build | pull request with change record |
| Nav2 limits, docking speeds | `nav2_params.yaml`, `dock_trigger.yaml` (QM) | pull request | same; these are below the safety limits and cannot exceed them |

## 6. Indication and diagnostics (SR-00.04)

Lamp at the reset button (reset required / running), a stack light or LED bar visible from all sides (stopped,
running, fault), K0 auxiliary contacts and the reset state into Teensy digital inputs, all published in
`/firmware/status` and shown in the UI. The UI shows state; it never changes it.

## 7. CFG-002 elements (the 2.0 mobile manipulator, the hardware reference since DQ-020 A)

| Element | 2.0 per upstream register | Verified? |
|---|---|---|
| E1 | two E-stops: base front Schneider XB4BS8445 + ZBE-102, chest button from the OpenArm kit (`SAFETY-PROCUREMENT`) | no (plan set, not in a repository) |
| E2 | Pilz PNOZ s3 24 V DC with monitored manual reset | no |
| E3 | K1, K2 Gigavac GX11CAC in series, linked NC auxiliaries in the PNOZ reset loop; E-stop cuts actuator power only (`ESTOP-SCOPE`) | no |
| E4 | hub-motor brakes released from the actuator side, so power removal engages them; ZLAC8015D driver (STO input: unknown) | no |
| E5 | **none named**; MB7060 ultrasonic and TF-Luna "not a safety device"; RPLIDAR S3 "functional sensing" | gap |
| E6 | **none named** | gap |
| E7 | one RESET button XB4BW36B5 with lamp (`RESET-BUTTON`) | no |
| E10 | Daly BMS on CAN2, hard-fault disconnect (`BMS-FAULTS`) | no |
| E11 | F0 110 A Class T, lockable disconnect (`MAIN-PROTECTION`) | no |
| E8 (channel 1) | STM32H723ZG base controller firmware (Gate B), go/no-go 6 November 2026; the Teensy build is the fallback | no (not public) |
| E12 arm pose signals (SF-10) | **none named** | gap |
| E13 arm safety controller and safe torque off (SF-11) | **none named**; the OpenArm 2.0 safety functions are not published | gap |
| E14 lift holding and interlock (SF-12) | DOLD Hexalift V4; "written DOLD holding on E-stop and power loss" is a release gate (`LIFT`) | no |
| E15 station detection for the arms (SF-11) | **none named** | gap |

The 2.0 chain as decided covers SF-01 and part of SF-05 and SF-06. SF-02, SF-03, SF-10, SF-11 and SF-12 have no
element in the 2.0 register; they are the first things to raise with upstream, with the OpenArm 2.0 safety
functions and the lift holding evidence.

## 8. Open items

| ID | Item | Blocks |
|---|---|---|
| OI-1 | Read the ZBLD.C20 manual: semantics of `BRK/DI5` (brake vs inhibit), `SPD/DO2` pulse specification, `ERR/DO1` polarity | §3.2, §3.5 |
| OI-2 | ~~Choose E5~~ decided 2026-10-20 (DQ-007: scanner plus rear bumper). E6 (speed relay vs safety PLC) is proposed in WP-H-02 §3 | §3.5 |
| OI-3 | Measure category 0 coasting distance at 0.20 m/s, loaded and unloaded | §3.4 field sizing |
| OI-4 | Reliability data (MTTFd, B10d) for K0, K1/K2, E-stop devices, scanner; DCavg and CCF scoring | WP-H-03 |
| OI-5 | Confirm K0 output count and current for three paths (K1 coil, K2 coil, BRK/DI5 of two drivers) | §3.2 |
| OI-6 | The firmware channel (DQ-014 B): define the diagnostic output channel 2 compares against, the heartbeat window and the demand relay; start the ISO 13849-1 §7 lifecycle in WP-W-01…WP-W-08 | §3.5, WP-M-01 OI-4 |
| OI-7 | Put to upstream: the OpenArm 2.0 safety functions (safe torque off, force limiting, pose outputs) and the DOLD holding evidence | §3.8, §7 |
