# Baseline Gap Assessment

| Field | Value |
|---|---|
| Work product | Baseline gap assessment (supporting document, not a registered work product) |
| Standard reference | ISO 12100:2010; ISO 3691-4:2023; ISO 13849-1:2023 and 13849-2:2012; EN 60204-1:2018; ISO 13850:2015; IEC 62443-4-1/-4-2; Regulation (EU) 2023/1230 |
| Version | 0.1: initial assessment (2026-10-20) |
| Status | Draft |
| Author | Assurance team (initial review, assisted by static code and document review) |
| Reviewer(s) | TBD |
| Baseline | `openamr-platform-sw@8a7a5b1` (2026-10-19), `openamr-platform-hw@6c32fba` (2026-10-16), `openamr-platform-fw@f96014d` (2026-10-12), `openamrobot-release@b9f4a9d` (v0.0.1 manifest), `openAMRobot/.github@9109d3e` (decisions register, 2026-10-19), `openamrobot-docs@95c6140` |

## 1. Scope and method

This was a static review of the upstream repositories at the baseline above. No code was built or executed and no
robot was operated. Shallow clones were used, so history was not audited.

- **Areas reviewed:**
  1. the motion-stop layer: the Teensy firmware (`openamr-platform-fw`), the motor drivers and the power and
     E-stop wiring (`openamr-platform-hw`);
  2. the onboard application stack: the ROS 2 Jazzy packages and their Nav2 configuration (`openamr-platform-sw`);
  3. the hardware record: power, sensing, mechanical, BOM;
  4. governance, release and configuration management (`openAMRobot/.github`, `openamrobot-release`,
     `openamrobot-docs`).
- **Configuration:** findings are stated for upstream's **Gate A unit**, the robot that has been wired, flashed and
  driven: v0.0.1 differential-drive base, Raspberry Pi 5, Teensy 4.0, ZD BLDC motors with ZBLD.C20-120L2R drivers,
  AS5040 encoders, MPU6500 IMU, RPLIDAR A1, two 12 V lead-acid batteries. OpenAMRobot 2.0 is covered in §8 as
  decisions, not as assessed design.
- **Not reviewed:** `openamrobot-ui`, `openamrobot-interfaces`, `openamrobot-comm`, `openamrobot-manifest`,
  `openamr-upperbody-*`, `openamrobot-manipulation`, `openamrobot-embodied-ai`. The upstream `linorobot2_hardware`
  library the firmware overlays (motor, encoder, kinematics classes) is not in the firmware repository; one class
  was read at the pinned commit (`aaf9d59`) to settle the brake question (GAP-02).
- **Verification:** the most severe findings (marked ✔) were re-checked directly in the source by the author.
- **Numbering:** IDs run GAP-01…GAP-40 and are grouped by area, not in numeric order (GAP-35…GAP-40 were added to §4 after the software survey). IDs are never reused.
- **Standards text:** the standards are copyrighted and not reproduced. Clause references are to the editions in
  the header and must be checked against a licensed copy before an audit.

**Provenance.** The fork carries no changes yet. Every finding below is a finding about upstream OpenAMRobot as
inherited. Upstream's own documents already state many of them (`docs/safety/00_safety_overview.md` §4 in the
software repository, "Known hardware limitations" in the hardware README, `KNOWN_LIMITATIONS.md` in the release).
Where upstream says a gap is "deliberate and tracked", that is recorded here as a strength (§9) and the gap stays
a gap.

## 2. Summary

| Area | Assessment |
|---|---|
| Safety architecture | The pattern is right: a large ROS 2 stack (Nav2, docking, later a learned policy) in front of a small firmware layer on a separate microcontroller that is the last thing before the motors. But the firmware layer is **not a safety layer**: its only stop is a 200 ms software timeout on the same core that generates the PWM, it has no hardware watchdog, no E-stop input, no fault input and no brake output, and the drivers' brake and fault pins are unwired. Upstream's own register says so: "watchdogs … are functional, never safety evidence" |
| Stop functions | **No safety function reaches any Performance Level.** No emergency stop (ISO 13850) exists in the documented wiring, no protective stop, no safe speed. The fastest stop on a Gate A unit is to cut the 24 V battery by hand, and no disconnect is fitted |
| Personnel detection | None safety-rated. The 2D LiDAR is "functional sensing only, not a safety device" (upstream's words); its plane is at 222 mm (S3) or ~180 mm (A1), there are no bumpers, no safety scanner, and nothing below the plane is seen |
| Electrical | No battery fuse, no battery disconnect, battery and mains in parallel with no source selector, 24 V bus "permanently live and unprotected" (upstream diagram) |
| Risk assessment, requirements, analyses | Absent. The documentation site has a risk-assessment page that is an empty template. No hazard list, no safety functions, no PLr, no FMEA, no stopping-distance or stability data. Robot mass is not stated anywhere |
| Software verification | The ROS 2 repository has two CI test workflows (driver bring-up and navigation status), but the 2,765-line docking motion sequencer has no tests at all and no simulation, launch or hardware-in-the-loop safety-behaviour test exists; the firmware has none: `tests/` is a placeholder, nothing compiles the firmware in CI, no static analysis, no coverage |
| Process capability | Governance is unusually strong for a project this age (decision register with CI consistency scans, two-human approval on safety paths, engineering quality standard with readiness levels, release manifest). Technical safety process is at the level of "PR checkbox: safety implications reviewed" |
| Cybersecurity | Anyone on ROS domain 0 (multicast discovery, guest Wi-Fi) can move the robot, trigger docking or undocking, deactivate the collision monitor or change PID gains at runtime over unauthenticated topics and services; no SROS2, no command arbitration; the browser UI's stop is a software request over the network |
| 2.0 design | A real safety chain is decided (two certified E-stops, Pilz PNOZ s3 safety relay, two contactors with linked auxiliaries, hub motors with brakes engaged on E-stop, BMS, 110 A main fuse and lockable disconnect). None of it is in a public repository; the design documents are "plan-set documents, not held in any repository" |

## 3. Motion-stop layer (firmware, drivers, stop chain)

### 3.1 Reference configuration as traced in code

| Item | Value | Source |
|---|---|---|
| Controller | Teensy 4.0 (i.MX RT1062), micro-ROS over USB serial at 115200 to the Pi 5 | `fw: config/lino_base_config.h:211`; `fw: boards/teensy_4_0/linorobot2_overlay/README.md:26` |
| Firmware base | linorobot2_hardware `aaf9d59` (branch jazzy), three files overlaid by manual copy | `fw: NOTICE.md:31-37`, `fw: README.md:74-76` |
| Control loop | 50 Hz executor timer (`control_timeout = 20` ms), spun from `loop()` with a blocking 100 ms agent ping every 200 ms | `fw: src/firmware.ino:450-458, 280, 284` |
| Command watchdog | no `/cmd_vel` for ≥ 200 ms → `fullStop()` and PID reset | `fw: src/firmware.ino:611, 630-640` |
| `fullStop()` | zero the twist, call `brake()` on each motor | `fw: src/firmware.ino:583-593` |
| `brake()` (upstream Generic2 class) | `analogWrite(pwm, 0)`; IN_A/IN_B driven only when `USE_SHORT_BRAKE` is defined, which it is not | linorobot2_hardware `aaf9d59` `firmware/lib/motor/default_motor.h`; `fw: config/lino_base_config.h:230` |
| Motor drivers | 2 × ZBLD.C20-120L2R in open-loop power-stage mode (SW1 OFF), speed from Teensy PWM on `VAR/AI2`, direction on `FWD/DI1`, `REV/DI2` | `hw: electrical/motor_control/motors-drivers.md:37, 54-55` |
| Driver brake and fault pins | `BRK/DI5`, `ERR/DO1`, `CLR/DI4` unused: "no fault read-back" | `hw: electrical/wiring/wiring-pinout.md:67` |
| Speed limit | firmware `MOTOR_MAX_RPM 80 × MAX_RPM_RATIO 0.85` = 68 rpm ≈ 0.71 m/s; mechanical no-load 120 rpm ≈ 1.26 m/s | `fw: config/lino_base_config.h:69-70`; `hw: manufacturing/bom/components-bom.md:53-54` |
| PWM authority | `constrain(pwm, PWM_MIN, PWM_MAX)` with 10-bit PWM: closed loop can reach 100 % duty | `fw: src/firmware.ino:655-656`; `config/lino_base_config.h:80, 126-127` |
| Hardware watchdog | `WDT_TIMEOUT` commented out; the only WDT hook is ESP32-specific | `fw: config/lino_base_config.h:231`; `src/firmware.ino:298-300` |
| E-stop, STO, brake output, fault input | none in the pin map; the only `digitalRead` is the LED pin | `fw: config/lino_base_config.h:95-128`; `src/firmware.ino:318` |
| Agent loss | ping fails → `fullStop()`, destroy entities, wait | `fw: src/firmware.ino:287-292` |
| Powered debug | `#define ENABLE_POWERED_DEBUG` hard-coded on in the deployed build; `/debug/openloop` honoured for 300 ms, clamped to 0.7·PWM_MAX before `motor2_gain` | `fw: src/firmware.ino:117, 326-334, 606-610, 624` |

### 3.2 Findings

| ID | Finding | Evidence | Standard | Severity |
|---|---|---|---|---|
| GAP-01 ✔ | **No emergency-stop function exists in the documented design.** A mushroom button is visible in photos and its panel hole is kept in the CAD, but nothing documents what it switches; the verified power architecture runs battery and mains straight to the drivers with no switch in the path; the "schematic" for the E-stop is an external image in a GitHub discussion; upstream's own TODO asks "whether a physical E-stop exists". No safety relay, contactor, dual channel or monitored reset exists on the Gate A unit | `hw: electrical/power_distribution/power.md:32-37, 56-57, 139`; `wiring/wiring-pinout.md:128-132`; `safety/safety.md:11`; `sw: docs/safety/00_safety_overview.md` §4 | 13850 §4; 60204-1 §9.2.3.4; 3691-4 §4 (emergency stop); 13849-1 §5 | High |
| GAP-02 ✔ | **The only stop is a coast.** The 200 ms watchdog calls `brake()`, which sets PWM to 0; `USE_SHORT_BRAKE` is off and the driver `BRK/DI5` input is unwired, so the wheels free-run to a halt. There is no holding brake. Stopping distance under the watchdog is not measured anywhere; the Nav2 deceleration limit of −2.5 m/s² assumes closed-loop braking that the stop path does not perform | `fw: src/firmware.ino:583-593`; `config/lino_base_config.h:230`; `hw: wiring/wiring-pinout.md:67`; upstream `default_motor.h` at `aaf9d59` | 3691-4 §4 (braking); 13849-2 §5 (validation of stop) | High |
| GAP-03 ✔ | **Stop depends on the same core and the same software that drives the motors.** The watchdog is a `millis()` comparison inside an executor timer that only runs while the micro-ROS agent is connected; a hung or stalled MCU leaves the last PWM latched. No independent hardware watchdog is enabled (`WDT_TIMEOUT` commented out; the only code path is `esp_task_wdt_reset()`, which does not exist on Teensy) | `fw: src/firmware.ino:284, 298-300, 611`; `config/lino_base_config.h:231` | 13849-1 §6 (Category B vs 2/3: no monitoring); 61508-2 §7.4 | High |
| GAP-04 ✔ | **No motor-driver fault feedback.** `ERR/DO1` is unwired, so when one driver latches a fault (over-current, locked rotor, under-voltage; cleared only by a 24 V power cycle) the Teensy keeps commanding both wheels and the robot pivots on the live wheel. Upstream reports an unresolved intermittent left-wheel dropout | `hw: motor_control/motor-driver-fault-codes.md:8-10, 59`; `wiring/wiring-pinout.md:67, 106-109` | 13849-1 §6 (fault detection); 12100 §5.4 | High |
| GAP-05 ✔ | **No plausibility checks on actuation.** No encoder-loss, stall, sign-error, over-current or voltage check in the firmware. A dead encoder reads 0 rpm, feedforward plus PID saturate, and the clamp allows 100 % duty. Encoder direction is verified only by a manual post-flash checklist. Battery monitoring is "not implemented" | `fw: src/firmware.ino:600-602, 646-656`; `README.md:93-94`; overlay `README.md:25` | 13849-1 §6; 3691-4 §4 (speed control) | High |
| GAP-06 ✔ | **`/cmd_vel` has no validity or freshness semantics.** No NaN or range check (`twist_msg` goes straight into kinematics), no timestamp, sequence or source check; any repeated message, however stale its content, refreshes the watchdog. The firmware applies no acceleration limit of its own | `fw: src/firmware.ino:316-321, 644` | 13849-1 §7 (SRESW), Annex J; 61508-3 §7.4 | High |
| GAP-07 ✔ | **Runtime parameter injection changes motor behaviour without any gate.** `/debug/tune` sets both PIDs' Kp/Ki/Kd unconditionally (NaN, zero and negative accepted), `motor2_gain` and `kff` with no upper bound; `/debug/enc_cal` loads a 72-value correction table with only a length check, applied to both the velocity loop and odometry. Neither topic is gated by `ENABLE_POWERED_DEBUG`, and the active values cannot be read back | `fw: src/firmware.ino:337-358, 527-534, 716-724` | 13849-1 §7.4 (parameterisation); 62443-4-2 CR 3.1 | High |
| GAP-08 ✔ | **The raw-PWM diagnostic path is enabled in the deployed build** and is evaluated before the watchdog. Its 0.7·PWM_MAX clamp is applied before `motor2_gain`, so the right wheel can reach full PWM if the gain exceeds ≈1.43. The gate is a hard-coded `#define`, not a build flag as the docs say, and there is no runtime arming. The per-boot encoder calibration ritual requires this path, so a "production" image cannot run upstream's own deployed ripple fix | `fw: src/firmware.ino:113-117, 606-629`; `docs/safety/motion-safety.md:25`; `tools/encoder-calibration/align_enc_cal.py:1-10` | 13849-1 §7; 12100 §6.3 (reasonably foreseeable misuse) | Medium |
| GAP-09 | **Per-boot calibration is safety-relevant and enforced by nothing.** The encoder ripple table lives in RAM; after any reset it reverts to passthrough with no telemetry flag, the PID chases a ±40 % ripple (±6 rpm limit cycle) and odometry drifts. An anti-phase table doubles the ripple and is accepted silently | `fw: docs/architecture/encoder-calibration.md:5-6, 64-89`; `src/firmware.ino:144-148, 211` | 13849-1 §7; 12100 §5.4 | Medium |
| GAP-10 | **The firmware cannot identify itself.** No version or build-ID topic, no reset-cause or boot counter; the node name is upstream's generic `linorobot_base_node`. The host cannot detect a silent reboot that drops tuning and calibration. The build is not reproducible from the repository: `platformio.ini` and the toolchain pins are absent, two different build commands are documented, and the overlay is applied by manual copy | `fw: config/lino_base_config.h:214`; `README.md:58, 75-76`; `docs/flashing/build-and-flash.md:16` | 13849-1 §10; 61508-1 §6.2 (CM); ASPICE SUP.8 | Medium |
| GAP-11 | **Firmware has no verification evidence.** `tests/` holds a `.gitkeep`; CI calls only the org's reusable "repository quality" workflow, pinned to `@main`, with no firmware build; no static analysis, lint, MISRA or coverage. Dated tuning measurements exist in prose only, with no raw data | `fw: tests/.gitkeep`; `.github/workflows/repository-quality.yml:13`; `docs/architecture/control-loop.md:146-158` | 13849-1 §7.2, Annex J; 13849-2 §5 | High |
| GAP-12 | **Documentation disagrees with code on safety behaviour.** `PWM_MIN` evaluates to −1025 (missing parentheses) while the docs say −1023; a magnetometer init failure halts the firmware while the safety doc calls it "informational"; the hardware safety note tells the operator to keep "a hand on the 24 V cut-off" that the same repository says is not fitted | `fw: config/lino_base_config.h:126-127` vs `docs/architecture/control-loop.md:125`; `src/firmware.ino:238-249` vs `docs/safety/motion-safety.md:38-40`; `hw: safety/safety.md:7` vs `README.md:118` | 13849-1 §10 (information for use); 12100 §6.4 | Low |

## 4. Onboard application stack (ROS 2, Nav2 chain)

### 4.1 Velocity chain as configured

| Stage | Setting | Source |
|---|---|---|
| Controller (DWB) | `max_vel_x 0.20`, `min_vel_x −0.05`, `max_vel_theta 0.5`, `acc_lim_x 1.0`, `acc_lim_theta 3.0`, `decel_lim_x −2.5`, `decel_lim_theta −3.0` | `sw: ros2/src/openamrobot_nav2/config/nav2_params.yaml:116-131` |
| Footprint | eight-point polygon, 0.415 m ahead to 0.390 m behind, ±0.29 m; `inflation_radius 0.15` (local), 0.35 (global) | `nav2_params.yaml:172, 177, 241` |
| Obstacle layer | `obstacle_min_range 0.0`, `raytrace_min_range 0.10`, scan from `/scan_filtered` | `nav2_params.yaml:194-197` |
| velocity_smoother | `feedback OPEN_LOOP`, limits equal to the controller's, `velocity_timeout 1.0` | `nav2_params.yaml:340-348` |
| collision_monitor | one `approach` polygon on the published footprint, `time_before_collision 0.8`, `min_points 6`, scan `min_height 0.15`, `min_range 0.15`, `source_timeout 1.0`, `stop_pub_timeout 2.0` | `nav2_params.yaml:357-376` |
| Recovery behaviours | behavior_server remapped to `cmd_vel_nav` since #35 (2026-10-19), so spin, backup, drive_on_heading and assisted_teleop now pass the smoother and monitor; `backup` enabled | `sw: ros2/src/openamrobot_nav2/launch/navigation_launch.py:174-179`; `nav2_params.yaml:303-307` |
| Docking | sequencer publishes `/cmd_vel` directly (`cmd_vel_topic: /cmd_vel`), deactivates the collision monitor by lifecycle transition after Phase 1, runs with `obstacle_check_enabled: false`; undock reverses 0.7 m at 0.10 m/s on odometry | `sw: ros2/src/openamrobot_docking/config/dock_trigger.yaml:170, 260, 22-23`; `scripts/dock_trigger.py:1015` |
| Scan filter (real robot) | rear sector [−45°, 49°] removed at all ranges; side returns closer than 0.40 m removed in [−108°, −73°] and [73°, 96°] | `sw: ros2/src/openamrobot_perception/config/scan_body_filter_real.yaml:28-32` |
| Command arbitration | none: no twist_mux; `/cmd_vel` has at least five publishers (controller chain, dock_trigger, teleop, operator UI via rosbridge, diagnostics scripts) | search of `ros2/src`; `docs/real_robot/06_operator_ui.md:20-22` |

### 4.2 Findings

| ID | Finding | Evidence | Standard | Severity |
|---|---|---|---|---|
| GAP-13 ✔ | **The software envelope is best-effort and upstream says so.** Every layer above the firmware (footprint critic, smoother, collision monitor) "depends on a healthy, correctly-configured software stack"; the smoother is open-loop and "cannot detect that a wheel actually stalled". None of it can carry a safety claim, and upstream's register forbids calling it one (`TELEMETRY-NOT-SAFETY-EVIDENCE`) | `sw: docs/safety/00_safety_overview.md` §1–§2, §4; `.github: decisions.yaml` TELEMETRY-NOT-SAFETY-EVIDENCE | 3691-4 §4; 13849-1 §4.5 | High |
| GAP-14 ✔ | **Objects below the scan plane are invisible to every layer.** Upstream states obstacles shorter than ~18 cm are missed by the costmap and the collision monitor; the S3 plane is at 222 mm. No hardware (bumper, down-tilted sensor) exists on the Gate A unit; the 2.0 near-field sensors are "not a safety device" | `sw: docs/safety/00_safety_overview.md` §4; `hw: electrical/sensors/lidar.md:20`; `near-field.md:8-9` | 3691-4 §4 (personnel detection), Annex A; 12100 §5.4 | High |
| GAP-15 ✔ | **Docking removes every reactive protection, from the pre-dock drive to contact.** After Phase 1 the sequencer deactivates the collision monitor by lifecycle transition, publishes `/cmd_vel` directly (its config comment still claims Nav2 "does NOT run a velocity_smoother", which is false), runs with `obstacle_check_enabled: false`, drives about 2 m to the pre-dock point and, when no tag is visible, goes "BLIND — no steering correction, just keep advancing straight" on dead-reckoned depth. The docking research table says "all 3 tags lost > 1 s → Halt"; the code does the opposite. The user documentation turns this into a rule: "Do not stand in it. Do not reach into it." | `sw: ros2/src/openamrobot_docking/scripts/dock_trigger.py:1015, 1041-1099, 1257-1260`; `config/dock_trigger.yaml:165-170, 260`; `docs/14_docking_research.md:802, 829`; `docs: docs/use/monitoring/safety.md` | 3691-4 §4; 12100 §6.2 (inherently safe design before information for use) | High |
| GAP-35 ✔ | **Undock is a blind 0.7 m reverse** at 0.10 m/s on odometry with no rear check; the rear sector is masked out of the real-robot scan entirely, so no layer sees behind the robot; it runs even when the robot is not docked ("Not docked — running undock maneuver anyway") and is triggered by any publisher on `/undock_robot` or by a `/goal_pose` while docked. Nav2's `backup` recovery is enabled on the same rear-blind robot; the status profile declares `rear_coverage: UNAVAILABLE` while a parameter comment claims "collision_monitor guards the rear ~0.365 m" | `sw: ros2/src/openamrobot_docking/scripts/dock_trigger.py:946-951, 964-976, 1800-1838`; `config/dock_trigger.yaml:22-23`; `openamrobot_perception/config/scan_body_filter_real.yaml:28-32`; `openamrobot_nav2/config/nav2_params.yaml:116, 303-307`; `navigation_status_profile.yaml:61` | 3691-4 §4 (personnel detection in the direction of travel); 12100 §5.4 | High |
| GAP-36 ✔ | **No command arbitration.** There is no twist_mux; the controller chain, the docking sequencer, keyboard teleop ("floods `/cmd_vel`, overrides Nav2"), the operator UI through rosbridge and the diagnostics scripts all publish the final `/cmd_vel`. The sequencer's `_publish_cmd_vel` applies no clamp and its `drive_speed` and `final_push_speed` parameters are read each loop with no range descriptor; the diagnostics scripts take unbounded PWM and speed arguments from the command line | `sw: ros2/src/openamrobot_docking/scripts/dock_trigger.py:1370, 1641, 2339-2343`; `docs/navigation/04_real_robot_tuning.md:116-121`; `docs/real_robot/06_operator_ui.md:20-22`; `tools/diagnostics/openloop_test.py:24` | 13849-1 §5.2 (safety function priority); 3691-4 §4 | High |
| GAP-37 | **Failure handling is report-only.** If the collision monitor fails to re-activate after docking the node logs at ERROR and publishes `collision_monitor_down`, then the `finally` block overwrites the status with `docked`/`failed` and the heartbeat reports idle; goals are still forwarded to Nav2. The navigation status node detects stale sensors but "never sends goals or velocity commands" and nothing consumes its output; the Nav2 lifecycle `bond_timeout` is 60 s; the micro-ROS agent process has no respawn | `sw: ros2/src/openamrobot_docking/scripts/dock_trigger.py:896-904, 939, 964-969`; `openamrobot_nav2/openamrobot_nav2/navigation_status_node.py:6`; `launch/navigation_launch.py:237`; `openamrobot_drivers/launch/drivers.launch.py:86-89` | 13849-1 §6 (reaction to detected faults); 61508-2 §7.4 | Medium |
| GAP-38 | **Safety documentation diverges from the configuration.** The limits document quotes `max_accel [0.5, 0, 0.5]` and DWB `acc_lim_* 0.5`; the file has `[1.0, 0, 3.0]` and `−3.0` (raised for a stiction deadlock, against the docking lesson that tipping was handled with "gentle accel limits"). `SECURITY.md` and the changelog say `FootprintApproach.enabled: false`; it is `True`. The collision-monitor page cites `docking_server` collision detection, but `docking_server` is never launched. The README roadmap marks the docking obstacle guard "Done"; it is off by default | `sw: docs/safety/02_limits_and_watchdog.md:18-21` vs `nav2_params.yaml:124-131, 343-344`; `SECURITY.md:41`; `nav2_params.yaml:370, 380-422`; `launch/navigation_launch.py:43-52`; `README.md:386`; `openamrobot_docking/docs/12_lessons_learned.md:181-192` | 13849-1 §10; 12100 §6.4 | Medium |
| GAP-39 | **The motion-critical code has no tests.** `openamrobot_docking` (2,765-line sequencer plus a C++ node) has no `test/` directory and no CI workflow triggers on its paths; the two CI workflows cover launch-file introspection and the status node's rules; there is no simulation, launch-testing or hardware-in-the-loop test of stopping, monitor engagement or sensor-timeout behaviour; copyright tests are skipped; upstream's `STATE.md` records "quality/test is skipped on main" | `sw: .github/workflows/nav-status-tests.yml:68-73`; `drivers-bringup-tests.yml:83-120`; `docs/getting_started/TESTING_GUIDE.md:168`; `STATE.md:33-36` | 13849-1 §7.2; 13849-2 §5 | High |
| GAP-40 | **Simulation and real robot differ in the parameters that matter.** The Gazebo model allows 1.0 m/s and 2.0 rad/s with a 0.400 m track against 0.46 m measured; one `nav2_params.yaml` serves both; the sequencer hard-codes a 0.35 m camera offset against a 0.415 m static transform; the top-level bringup defaults to real hardware with docking on. Upstream's `STATE.md`: "Not verified — real-robot motion, docking and sensor bring-up" | `sw: ros2/src/openamrobot_description/urdf/gazebo_control.xacro:9-22`; `openamrobot_bringup/launch/bringup.launch.py:4-6, 196, 208`; `real_bringup.launch.py:85, 93`; `dock_trigger.py:1272`; `STATE.md:10, 40` | 13849-2 §5; 3691-4 Annex A | Medium |
| GAP-16 | **The collision monitor tolerates a stale scan for 1 s and ignores returns inside 0.15 m.** With `source_timeout 1.0` the robot continues on the last valid scan for up to a second at 0.20 m/s (0.2 m); `min_range 0.15` masks exactly the zone a person's foot occupies at contact. The A1 LiDAR "sometimes stops publishing on its own, cause not yet pinned" | `sw: nav2_params.yaml:358, 375-376`; `hw: electrical/sensors/lidar.md:95-96` | 3691-4 §4; 13849-1 §6 | Medium |
| GAP-17 | **Operating limits rest on an operational battery rule.** Below ~22 V under load the drivers under-volt, the robot "fails to follow the plan and hits obstacles the navigation was avoiding"; the mitigation is "meter the pack before a test", which upstream calls "an operational mitigation, not an engineered safeguard". No battery voltage is read by firmware or software | `sw: docs/safety/02_limits_and_watchdog.md` §4; `docs/safety/00_safety_overview.md` §4 | 12100 §6.2; 3691-4 §4 | Medium |
| GAP-18 | **Real-robot bring-up is in progress; the validated path is the simulation.** The repository status is "experimental, tuned end-to-end in the docking simulation; real-robot bringup is in progress under placeholder packages". Findings on the Nav2 chain apply to the configuration as committed, which has run on the Gate A unit but has no recorded acceptance test | `sw: README.md` (Status); `ros2/src/` package list | 13849-2 §5; 3691-4 Annex A | Medium |

## 5. Hardware record (power, sensing, mechanical)

| ID | Finding | Evidence | Standard | Severity |
|---|---|---|---|---|
| GAP-19 ✔ | **No battery fuse and no battery disconnect.** The 24 V bus is "permanently live and unprotected against short-circuit"; a lead-acid pair can source hundreds of amps into a fault. Two documents nevertheless describe the driver supply as "fused" | `hw: electrical/wiring/diagrams/wiring-harness.svg:57, 62, 230-231`; `power_distribution/power.md:50-57`; `wiring/wiring-pinout.md:94`; `motor_control/motors-drivers.md:42` | 60204-1 §7.2 (overcurrent), §5.3 (supply disconnecting device) | High |
| GAP-20 ✔ | **Battery and mains run in parallel with no source selector**; upstream warns of back-feed and uncontrolled charging. The charger and AC/DC converter models are unknown; the 230 V side has no documented RCD, enclosure, earth or input fuse as built | `hw: power.md:58-60, 79-94, 139`; `manufacturing/bom/components-bom.md:24` | 60204-1 §6 (protection against electric shock), §7 | High |
| GAP-21 | **Logic power is not independent of compute.** The Teensy is powered over USB from the Pi 5; a Pi brown-out (observed on bring-up spikes, no active cooler, ~83 °C) removes the Teensy while the drivers stay at 24 V. Driver behaviour with floating DI/AI inputs is undocumented | `hw: power.md:44, 113-131`; `README.md:120-123` | 13849-1 §6 (behaviour on power loss); 60204-1 §7.5 | Medium |
| GAP-22 ✔ | **No safety-rated detection of persons.** The LiDAR is "functional sensing only, not a safety device"; there is no safety laser scanner with OSSD outputs, no bumper, no protective field or speed-and-separation concept, and no blind-zone analysis. A1 range starts at 0.15 m; the A1 model itself is "not formally confirmed" | `hw: electrical/sensors/lidar.md:10-11, 54, 98`; `near-field.md:8-9` | 3691-4 §4, Annex A; 13849-1 §5 | High |
| GAP-23 | **No mechanical safety data.** Mass, payload, centre of gravity, tip-over margin, slope limit, pinch and crush points, ingress protection and stopping distance are stated nowhere (the 45 kg figure is a worked example in the motor-sizing note, and its torque arithmetic disagrees with the rated torque). The Rev B battery pack is "placed only and not fixed"; CAD track (0.4075 m) is not the as-built track (0.46 m) | `hw: datasheets/motor-sizing-calculations.md:209, 507`; `components-bom.md:33, 50-52`; `CHANGELOG.md:61` | 12100 §5.3 (limits of the machinery); 3691-4 §4 (stability, braking) | High |
| GAP-24 | **No regenerative-braking path.** Fault codes 7–9 cite "regenerative braking spikes (decel) with no bleed"; no braking resistor or bus clamp is documented. A hard deceleration can latch a driver fault (see GAP-04) | `hw: motor_control/motor-driver-fault-codes.md:42` | 60204-1 §7; 3691-4 §4 | Medium |
| GAP-25 | **The BOM does not describe the robot.** The label-verified electrical BOM lists no fuse, E-stop, contactor, wire gauge or connector; the "preliminary" BOM and the spreadsheet list an E-stop and inline fuse that are not fitted; the spreadsheet is dated 2025 and names superseded parts. Key datasheets (ZBLD.C20 manual, S3, MB7060, TF-Luna, AC/DC, charger) are missing | `hw: manufacturing/bom/components-bom.md:11-24, 86, 91-95`; `mechanical-bom.md:142-143`; `BOM_specs_MMP.xlsx` | 13849-1 §10; Machinery Reg. Annex VII (technical file) | Medium |
| GAP-26 | **Licence statements conflict** (CERN-OHL-P in `LICENSE`, "MIT for docs" in `NOTICE.md` and `CONTRIBUTING.md`, CC BY 4.0 in `LICENSING.md`); CAD declared "placeholder" while present; LFS declared unusable while the mechanical README says the files are in LFS. Not a safety finding, but it blocks a clean provenance record for the fork | `hw: LICENSE:1`; `LICENSING.md:7-9`; `NOTICE.md:18-20`; `CONTRIBUTING.md:7-13`; `.gitattributes:2` | 13849-1 §10; Machinery Reg. Annex VII | Low |

## 6. Cybersecurity

| ID | Finding | Evidence | Standard | Severity |
|---|---|---|---|---|
| GAP-27 ✔ | **Any participant on ROS domain 0 can move the robot or retune it.** `/cmd_vel`, `/dock_trigger`, `/undock_robot`, `/goal_pose`, `/debug/openloop`, `/debug/tune` and `/debug/enc_cal` are plain subscriptions with no authentication, and the `/collision_monitor/change_state` lifecycle service can be called by anyone; no SROS2, keystore or enclave exists in any repository; discovery is multicast on `ROS_DOMAIN_ID` 0 over a guest Wi-Fi; the operator UI exposes Flask (5050), rosbridge (9090) and a video server (8080) with no authentication described | `fw: src/firmware.ino:416-442`; `docs/bringup/micro-ros-bringup.md:23-24`; `sw: docs/real_robot/02_networking_and_dds.md:20-24`; `docs/real_robot/06_operator_ui.md:16-22` | 62443-4-2 CR 1.1, CR 2.1, CR 3.1; 3691-4 §4 (control system) | High |
| GAP-28 | **The on-screen E-STOP is a software request over a network.** Upstream's user page says it plainly ("The red E-STOP on the screen is not an emergency stop … pressing it may do nothing at all"). Until GAP-01 is closed there is no other stop | `docs: docs/use/monitoring/safety.md` ("The one thing to remember") | 13850 §4; 62443-4-2 CR 3.8 | High |
| GAP-29 | **Supply chain is unpinned.** Every repository's CI calls a reusable workflow at `openAMRobot/.github@main`; the manifest tracks `main` ("a development workspace, not a reproducible release", upstream's words); the Docker base image `ros:jazzy-ros-base` and every apt and rosdep package are unpinned and the container runs as root with host networking; the micro-ROS agent and camera stacks are built from unrecorded versions; the firmware toolchain is unpinned | `.github: ENGINEERING_QUALITY_STANDARD.md` §2; `fw: .github/workflows/repository-quality.yml:13`; `sw: Dockerfile:1, 7-49`; `docker-compose.yml:24-25`; `docs/real_robot/01_bringup.md:44-59` | 62443-4-1 SM-9, SM-10; 61508-1 §6.2 | Medium |

## 7. Process and configuration management

| ID | Finding | Evidence | Standard | Severity |
|---|---|---|---|---|
| GAP-30 ✔ | **No risk assessment, hazard list, safety functions or PLr exist.** The documentation site's Risk Assessment, Emergency Stop, Battery Safety, Safety-for-builders and E-stop-config pages are unfilled templates ("Under development … Do not treat unfinished guidance as validated"). Upstream places the risk assessment on the user: "perform a documented risk assessment for the complete configured system" | `docs: docs/foundations/safety/risk-assessment.md`, `emergency-stop.md`, `configure/safety-limits/estop-config.md`; `docs/safety/index.md`; `release: KNOWN_LIMITATIONS.md` | 12100 §5; 3691-4 §4; 13849-1 §4.5, §5; Machinery Reg. Annex III §1.1.2 | High |
| GAP-31 | **Safety review is a checkbox.** Safety-relevant PRs require a "safety-impact statement" and two human approvals under CODEOWNERS, which is good, but there is no verification review, no independence level, no confirmation measure and no acceptance criterion behind the statement; CODEOWNERS has no owner for `/safety/` or `/electrical/` in the hardware repository | `.github: ENGINEERING_QUALITY_STANDARD.md` §7; `GOVERNANCE.md` (Platform-lead-authored PRs); `hw: .github/CODEOWNERS:1-4`; `.github/PULL_REQUEST_TEMPLATE.md:19` | 13849-1 §4.6, §10; 61508-1 §8 (functional safety assessment) | Medium |
| GAP-32 | **The release is not a configuration baseline.** v0.0.1 was built from `*-main.zip` archives; the manifest "does not resolve immutable component commits"; every README still reads "OpenAMRobot vX.X.X"; the firmware repository has no tags and the deployed binary differs from the repository (2026-10-12 comment edits over the 2026-06-29 deployed files) | `release: release-config.json`, `RELEASE_PROCESS.md`; `.github: ENGINEERING_QUALITY_STANDARD.md` §2; `fw: boards/teensy_4_0/linorobot2_overlay/README.md:120-123` | 61508-1 §6.2.3; 13849-1 §10; ASPICE SUP.8 | Medium |
| GAP-33 | **The safety-relevant design decisions are not in any repository.** The 2.0 safety chain, power distribution and gate criteria are cited to "P-03 Decision Addendum rev19.x" and "E-01 Safety and Power Distribution Baseline rev1.3", each "a plan-set document, not held in any repository; CI never reads it". The public register scans text for consistency with them but cannot verify them | `.github: decisions.yaml:78-101, 143-151, 774-867` | 13849-1 §10; Machinery Reg. Annex VII; 61508-1 §6.2 | High |
| GAP-34 | **Process capability (estimated):** MAN.3, SUP.8, SUP.10 at CL1 on governance evidence; SYS.1–SYS.3, SWE.1–SWE.3, HWE.1–HWE.2 at CL0 (no requirements, architecture or analyses); SWE.4–SWE.6 at CL0 for firmware and for the docking package, CL1 for the navigation and driver packages (two CI test workflows); VAL.1 at CL0 (no recorded acceptance tests). Upstream's own "truthful inventory" audit of 4 September 2026 reaches the same picture | `.github: ENGINEERING_QUALITY_STANDARD.md` §2, §4; `sw: .github/workflows/` | ASPICE PAM 4.0; 61508-1 §6 | Medium |

## 8. OpenAMRobot 2.0: decided, not verifiable

The upstream register (`openAMRobot/.github/decisions.yaml`, 36 entries) records a 2.0 design that would close
GAP-01, GAP-02, GAP-04 and GAP-19 in principle:

| Decision | What it records | Source entry |
|---|---|---|
| Safety-chain procurement | exactly two E-stops (Schneider XB4BS8445 with ZBE-102, chest button from the OpenArm kit), dual channel into a Pilz PNOZ s3 (750103) with monitored manual reset; K1, K2 Gigavac GX11CAC contactors in series with mechanically linked NC auxiliaries in the reset loop | `SAFETY-PROCUREMENT` (2026-10-18) |
| E-stop scope | cuts actuator power only (traction, arms, lift); Jetson and logic rails stay up; brake release fed from the actuator side so an E-stop engages the brakes | `ESTOP-SCOPE` (2026-10-15) |
| Drivetrain | two ZLTECH ZLLG80ASM250-L-B hub motors with brakes, one ZLAC8015D driver on CAN1; brake ratings "pending supplier evidence" | `DRIVETRAIN` |
| Main protection | F0 110 A Class T fuse, lockable battery disconnect, branch fuses per the B-02 schedule | `MAIN-PROTECTION` |
| Battery | 8S1P EVE LF105 LiFePO4 with Daly BMS on CAN2; the STM32 "stops motion and locks" on a BMS fault | `BATTERY-PLACEMENT`, `BMS-FAULTS` |
| Safety-chain I/O | Y32 through one ISO1212, E-stop spare NO and RESET NC as diagnostic inputs, charger fault input | `SAFETY-CHAIN-IO` |
| Speed | 1.5 m/s is "a command ceiling, an analytical limit"; operating speed to follow from "the stability model and stopping tests" | `SPEED-CEILING` |
| Sensing | RPLIDAR S3 "functional sensing, not a safety device"; 4 × MB7060, 2 × TF-Luna, Gemini 336L | `NAV-LIDAR`, `BASE-CONTROLLER-IO` |
| Principle | "Firmware status, watchdogs, collision monitoring and BMS telemetry are functional; E-stop, brake and actuator power removal are hardwired and independent of software" | `TELEMETRY-NOT-SAFETY-EVIDENCE` |
| Milestones | v2.0.0-rc.1 on 20 November 2026; v2.0.0 on 18 December 2026; STM32 go/no-go 6 November | `RELEASE-MILESTONES`, `BASE-CONTROLLER-GATES` |

What is **not** decided or not visible: the required PL of any function, the category and DC of the chain, how the
PNOZ output reaches the ZLAC8015D (STO input or contactor only), personnel detection (no safety scanner or bumper is
named anywhere), the stopping-distance and stability tests the speed decision depends on, and any arm or lift
safety function. The firmware repository's own 2.0 I/O page (2026-10-12) predates the safety-chain I/O decision
(2026-10-18) and lists no safety I/O. Every item in the table is a claim to verify once the design reaches a
repository, not evidence.

## 9. Existing strengths to build on

- **The architecture is the right shape.** A separate microcontroller is the last stage before the motors, and
  upstream intends the stop chain to bypass it in hardware (`ESTOP-SCOPE`, `TELEMETRY-NOT-SAFETY-EVIDENCE`). The
  fork's safety argument can be the same doer/checker argument as LionDriver's, with the hardwired chain as the
  checker of last resort.
- **Upstream is honest about its gaps.** `docs/safety/00_safety_overview.md` §4, the hardware "Known hardware
  limitations", `motion-safety.md`, `KNOWN_LIMITATIONS.md` and the user safety page each state the absence of an
  E-stop and the limits of the software layers in plain words. Nothing in this assessment contradicts an upstream
  claim of safety; upstream makes none.
- **A decision register with machine checks.** `decisions.yaml` records values, limits, exclusions and
  distinctions with sources, supersession, review dates and regex consistency scans run across every repository.
  That is the same idea as this project's register and the LionDriver trace checks; it should be cited, not
  duplicated.
- **Governance.** Two-human approval on safety paths, DCO and CLA, CODEOWNERS, an engineering quality standard
  with evidence-based readiness levels that explicitly refuse "production-ready" without evidence, and a release
  manifest that lists every component repository.
- **Documented velocity chain.** The Nav2 configuration is commented line by line with the reason for each limit
  and the date of the measurement behind it; the collision monitor and smoother are explained with their failure
  modes. This is already most of a software architecture description for the chain.
- **Measured operating floors.** Stick-slip floors (0.04 m/s, 0.15 rad/s) and the anti-stiction dither are
  characterised on the ground with dates; these feed straight into the machine limits of the risk assessment.
- **ROS 2 CI exists.** Driver bring-up and navigation status tests run on pull requests in the software
  repository, and the #35 fix that routes recovery behaviours through the reactive chain came with a regression
  test; the firmware and hardware repositories can be brought to the same bar.
- **A robot-safety issue template** with risk level and mitigation fields already exists in the software
  repository, and upstream's agent rules forbid agents from touching E-stop, brake, contactor, watchdog or
  motor-enable code without two human approvals.

## 10. Priority actions (feed into the G0/G1 plan)

1. **Decide the frame and the target** (register DQ-002, DQ-003, DQ-005): Gate A unit as reference configuration,
   EU machinery frame, PL d for emergency and protective stop. Everything below assumes those answers.
2. **Write the machine limits and the risk assessment** (ISO 12100 §5): mass, payload, speed, slope, operating
   zones, foreseeable misuse; hazard list with the risk graph giving PLr per safety function. This closes GAP-30
   and gives GAP-23 its targets. Weigh the robot.
3. **Specify the safety functions** (SF-01 emergency stop, SF-02 protective stop on personnel detection, SF-03
   safely-limited speed, SF-04 stop on loss of control): required PL, category, response time, stop category
   (EN 60204-1 category 0 or 1), and the demand on the hardware. Map upstream's 2.0 safety-chain decisions onto
   SF-01 and record the open items of §8 as defeaters.
4. **Add a hardwired stop to any Gate A unit the fork tests with**, before any further on-ground test: fuse and
   disconnect (GAP-19), a dual-channel E-stop through a safety relay dropping the driver supply or `BRK/DI5` on
   both drivers (GAP-01, GAP-02), and `ERR/DO1` read by the Teensy (GAP-04). This is bench hardware, not the
   product design; it is what makes the next months of testing defensible.
5. **Harden the firmware layer** in the fork, as LionDriver hardened panda: enable the i.MX RT watchdog
   (GAP-03), validate `/cmd_vel` (finite, bounded, with a sequence or timestamp; GAP-06), remove or arm the debug
   paths at runtime and bound their parameters (GAP-07, GAP-08), add encoder and stall plausibility (GAP-05),
   publish a version, reset cause and calibration-loaded flag (GAP-09, GAP-10). Record each change with an
   impact analysis.
6. **Stand up firmware verification** (GAP-11): a PlatformIO build in CI from a pinned `platformio.ini`, unit
   tests for the watchdog, clamps and kinematics on the host, static analysis, and a measured stopping-distance
   test on the Gate A unit (GAP-02).
7. **Put docking and undocking back inside the envelope** (GAP-15, GAP-35, GAP-36): route the sequencer through the smoother and monitor or give it its own bounded guard that cannot be switched off from the network, add a twist_mux with the stop path at highest priority, bound every speed parameter, and make a lost tag a halt as the design table says. Until then, docking and undocking are outside the case.
8. **Close the perception gap in the concept, not the code**: decide whether personnel detection is a safety
   scanner, bumpers, or a separated operating area (DQ-005 option B), and write the consequence into the
   operating-environment limits. Until then, no operation around people is inside the case (GAP-14, GAP-22).
9. **Freeze a baseline**: tag the three platform repositories in the fork at the commits in the header, pin the
   reusable workflow to a SHA, pin the linorobot2 base as a submodule or vendored copy (GAP-29, GAP-32).
10. **Request the plan-set documents** (P-03, E-01, B-02) from upstream or recreate their content in the fork's
   system design, so that every 2.0 claim in §8 has a readable source (GAP-33).
11. **Port the Living Safety Case tooling** from LionDriver and register GAP-01…GAP-40 as the first defeaters
    against the top-level claim.
