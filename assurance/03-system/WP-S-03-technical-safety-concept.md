# WP-S-03 Technical Safety Concept: the Stop Chain and the Safety-Related Control Architecture

| Field | Value |
|---|---|
| Work product | WP-S-03 Technical safety concept: architecture of the safety-related parts of the control system that implement SF-01…SF-07 |
| Standard reference | ISO 13849-1:2023 §6 (designated architectures, categories), §6.1.3 (Category 2), §6.1.4 (Category 3), Annex I (examples); ISO 13849-2:2012 Annex D; EN 60204-1:2018 §9.2, §9.4; ISO 3691-4:2023 §4; IEC 60947-5-5 |
| Version | 0.1 (2026-10-20): initial draft |
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
devices wired into the chain, never by the ROS 2 stack. This is the same doer/checker split as LionDriver's, with
the checker in copper rather than in a second processor.

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
| E8 Teensy firmware (functional, QM) | functional | diag. input | | ceiling only | ● (watchdog, validation) | reset cause | ● (stall, fault input) | ● |
| E9 Pi 5 / ROS 2 stack (functional, QM) | functional | none | none | none | ● (smoother timeout) | indication | | |
| E10 Battery monitor (voltage into E6 or E8) | input | | | | | | ● | |
| E11 Fuse F0 and lockable disconnect | complementary (DM-04) | | | | | | | |

Rule: E8 and E9 are never in the stop path. They may **demand** a stop through K0 (a watchdog output, a fault
output), but their failure cannot prevent one.

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

- Preferred device: a safety laser scanner (type 3, IEC 61496-3) with two OSSD outputs into a K0 input pair, mounted
  low at the front with its plane at ≤ 0.2 m and field sets switched by speed (through safe inputs tied to the speed
  monitor or to zone selection). Upstream's RPLIDAR S3 stays the navigation sensor; it is not a safety device.
- Alternative for the bench build: safety-rated bumpers (pressure-sensitive edges with a monitoring unit, PL d)
  on the front and rear, which cover the low-object gap (SR-02.03) and the reverse case (SR-02.04) at the cost of
  contact before stop; acceptable only with the crawl speed limit in the zones where they are the sole detection.
- Field sizing: `L_field ≥ v_max × (t_scanner + t_K0 + t_contactor) + d_stop(v_max) + margin`, with `d_stop` the
  measured category 0 coasting distance (or braked distance on 2.0). At 0.20 m/s and an assumed coast of
  **(TBC)** this gives **(TBC)**; nothing is claimed until measured.
- Docking: the scanner's field is reduced to a dock-lane field set at the crawl limit through a safe field-switch
  input, never through a ROS 2 lifecycle transition (GAP-15). The dock itself is outside the field or masked by
  the scanner's own configuration, verified in validation.
- Reverse: without rear detection, reverse is inhibited above the crawl limit by the speed monitor's direction
  input, and the back-up recovery is disabled in the Nav2 configuration (GAP-35).

### 3.5 Speed monitoring and drive faults (SR-03.01…SR-03.05, SR-06.01…SR-06.04): Category 2 or 3

- The ZBLD drivers provide a speed pulse output (`SPD/DO2`) per wheel that is independent of the Teensy's encoder
  reading. A safety speed-monitoring relay or a small safety PLC reads both pulse trains (and the direction from
  the driver's `FWD/REV` lines), compares against the active limit, and holds a K0 input enabled while in range.
  Over-speed for > 100 ms drops the input: K0 trips. Category 2 is reached with the test performed by the monitor
  itself (pulse-train plausibility); Category 3 if two independent speed sources are compared (driver pulse plus
  encoder channel through the Teensy's diagnostic output).
- The driver fault outputs (`ERR/DO1`, both drivers) go to the monitor (or to K0 directly): a latched driver fault
  trips the chain (SR-06.01). The Teensy additionally reads them for reporting.
- The Teensy's stall detector and watchdog outputs (fork change) can be wired as an additional demand into K0
  through a transistor output; they remain functional measures.

### 3.6 Battery monitoring (SR-06.05)

A voltage divider into the Teensy ADC (`BATTERY_PIN`, foreseen upstream but not implemented) for reporting, and a
voltage-monitoring relay with a hysteresis threshold into the K0 demand path for the stop. The BMS of 2.0 takes
this role (upstream `BMS-FAULTS`).

### 3.7 Powered-debug arming (SR-07.03)

A key switch read by the Teensy as the arming input for bench images; on the reference image the input is ignored
because the paths do not exist. The key switch position is reported in `/firmware/status`.

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

## 7. Mapping to OpenAMRobot 2.0

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

The 2.0 chain as decided covers SF-01 and part of SF-05 and SF-06. SF-02 and SF-03 have no element in the 2.0
register; they are the first thing to raise with upstream.

## 8. Open items

| ID | Item | Blocks |
|---|---|---|
| OI-1 | Read the ZBLD.C20 manual: semantics of `BRK/DI5` (brake vs inhibit), `SPD/DO2` pulse specification, `ERR/DO1` polarity | §3.2, §3.5 |
| OI-2 | Choose E5 for the bench build (scanner vs bumpers) and E6 (speed relay vs safety PLC); budget decision for the lead | §3.4, §3.5 |
| OI-3 | Measure category 0 coasting distance at 0.20 m/s, loaded and unloaded | §3.4 field sizing |
| OI-4 | Reliability data (MTTFd, B10d) for K0, K1/K2, E-stop devices, scanner; DCavg and CCF scoring | WP-H-03 |
| OI-5 | Confirm K0 output count and current for three paths (K1 coil, K2 coil, BRK/DI5 of two drivers) | §3.2 |
