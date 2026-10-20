# WP-C-01 Item Definition and Limits of the Machinery

| Field | Value |
|---|---|
| Work product | WP-C-01 Item definition and limits of the machinery |
| Standard reference | ISO 12100:2010 §5.3 (determination of the limits of the machinery), §5.4 (hazard identification inputs); ISO 3691-4:2023 §3, §4 (terms, operating zones); ISO 13849-1:2023 §4.5; Regulation (EU) 2023/1230 Annex III §1.1.2, Annex IV Part A (technical documentation) |
| Version | 0.2 (2026-10-20): DQ-002 and DQ-005 applied. 0.1: initial draft from the gap assessment and the upstream record |
| Status | Draft |
| PL / scope | PL d target for the stop functions (DQ-005, decided 2026-10-20); reference configuration Gate A unit (DQ-002, decided 2026-10-20); mobile base only (DQ-004, recommended option A, open) |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1) |
| Approver | Project lead |
| Baseline | BL-001 (`baselines.yaml`): upstream Gate A unit as inherited |

> [!WARNING]
> Draft prepared for engineering review. Values marked **(unknown)** are not stated anywhere in the upstream
> record and must be measured or decided before the risk assessment (WP-C-03) can be rated. Nothing here has
> been verified on the robot.

## 1. Item identification

| Field | Value |
|---|---|
| Item | OpenAMRobot mobile base, Gate A unit: the differential-drive platform that upstream has wired, flashed and driven, with its onboard ROS 2 Jazzy stack and Teensy 4.0 motion firmware |
| Fork | `jherrodthomas/openamr-platform-{sw,hw,fw}` from `openAMRobot/*` at BL-001 |
| Product class | Driverless industrial truck, automated guided, without load-handling device (ISO 3691-4 scope), intended to become a mobile manipulator (OpenAMRobot 2.0, out of scope for this item, see §9) |
| Upstream designation | "Gate A unit (existing robot, v0.0.1)"; the 2.0 design (Jetson, STM32H723, hub motors, safety chain) is "Gate B" and later |
| Manufacturer of record | Botshare LTD, Limassol, Cyprus, for upstream; the fork assigns no manufacturer and places no product on the market |

### 1.1 Reference configuration

| Element | Value | Source |
|---|---|---|
| Chassis | Steel (EN 1.0114) panel chassis, plastic cover, two drive wheels and swivel castors (Blickle LPA-VSTH 35K; count not stated) | `hw: manufacturing/bom/mechanical-bom.md:39-40`, `BOM_specs_MMP.xlsx` |
| Drive | 2 × ZD Z4BLD60-24GN-30S BLDC, 60 W, 24 V, 1:25 gearbox, 120 rpm at the wheel; 2 × ZBLD.C20-120L2R drivers in open-loop power-stage mode | `hw: components-bom.md:29-35, 70`; `motors-drivers.md:54` |
| Wheels | ⌀ 0.200 m drive wheels (Blickle GEVN 200/30H7), track 0.46 m measured (CAD says 0.4075 m, wrong) | `hw: components-bom.md:50-52`; `fw: config/lino_base_config.h:78-79` |
| Encoders | 2 × AS5040 magnetic quadrature, 1024 counts per wheel revolution, 3.3 V | `hw: electrical/sensors/encoders.md` |
| Low-level controller | Teensy 4.0 (i.MX RT1062) running the linorobot2 overlay firmware, micro-ROS over USB serial at 115200 baud | `fw: README.md`; `config/lino_base_config.h:211` |
| Compute | Raspberry Pi 5, 8 GB, Ubuntu Server 24.04, ROS 2 Jazzy, no active cooler | `hw: README.md:44` |
| Sensors | RPLIDAR A1 2D LiDAR (USB; model "not formally confirmed"), Raspberry Pi Camera Module 3 NoIR (CSI), MPU6500 IMU (no magnetometer) | `hw: README.md:46-50`; `lidar.md:98` |
| Power | 2 × 12 V 7 Ah AGM lead-acid in series (24 V 7 Ah); generic 24→5 V buck for the Pi; AC/DC converter of unknown model fed from 230 V mains in parallel with the battery; no fuse, no disconnect, no BMS | `hw: power.md:32-37, 50-60`; `components-bom.md:22-24` |
| Emergency stop | None in the documented design (a mushroom button is fitted to the panel; what it switches is undocumented) | gap assessment GAP-01 |
| Software | `openamrobot_bringup`, `_drivers`, `_perception`, `_nav2` (Nav2: AMCL, smac planner, DWB + RotationShim, velocity_smoother, collision_monitor), `_docking` (AprilTag sequencer), `_description`, `_gazebo`; `openamrobot_control` is a placeholder | `sw: ros2/src/` |
| Operator interface | Browser UI (`openamrobot-ui`, separate repository) over rosbridge; keyboard teleop; the on-screen E-STOP is a software request | `sw: docs/real_robot/06_operator_ui.md` |

## 2. Intended use and functions

### 2.1 Intended use (ISO 12100 §5.3.2)

- **Use:** indoor transport of a payload on the top mounting plate between operator-defined goal poses in a mapped
  area, with autonomous navigation, obstacle avoidance and automatic docking to a charging/parking dock. Upstream
  positions the platform for "logistics and warehouse robotics" at SMEs and for research.
- **Users:** builders (assemble and wire from the open-source record), integrators (commission on a site),
  operators (send goals, monitor, stop), bystanders (share the floor). Upstream's own user page addresses "anyone
  who works near the robot, whether or not they operate it".
- **Level of training:** none assumed by upstream beyond its documentation; the fork assumes a trained operator
  present during every run until WP-C-03 says otherwise (AOU-01).
- **Modes of use foreseen by the record:** manual bench test (wheels off the ground), keyboard teleoperation,
  autonomous navigation to a goal, autonomous docking and undocking, mapping (SLAM), simulation.

### 2.2 Functions

| ID | Function | Implemented by | Notes |
|---|---|---|---|
| F-01 | Accept a velocity command and drive the wheels in closed loop | Teensy firmware: feedforward + PID per wheel at 50 Hz | Last stage before the motors |
| F-02 | Stop the wheels when commands cease | Firmware 200 ms `/cmd_vel` watchdog → PWM 0 (coast) | Functional, not a safety function (upstream register) |
| F-03 | Estimate wheel odometry and publish IMU data | Firmware; EKF on the Pi | |
| F-04 | Localise on a map and plan a path to a goal | AMCL, smac planner | |
| F-05 | Follow the path, avoiding mapped and seen obstacles | DWB controller with footprint critic; local costmap from the LiDAR | Objects below the scan plane are not seen |
| F-06 | Clamp commanded velocity and acceleration | velocity_smoother (open loop) | 0.20 m/s, 0.5 rad/s, ±1.0 / −2.5 m/s² |
| F-07 | Slow before a projected footprint collision | collision_monitor, one `approach` polygon on the live scan | Deactivated during docking |
| F-08 | Recover when stuck (spin, back up, drive on heading, wait) | Nav2 behavior_server, routed through F-06 and F-07 since #35 | Back-up on a rear-blind robot |
| F-09 | Dock to and undock from an AprilTag dock | `dock_trigger` sequencer publishing `/cmd_vel` directly | Bypasses F-06 and F-07; undock is a blind reverse |
| F-10 | Accept goals, teleoperation and a stop request from the operator UI | rosbridge, Flask UI | Unauthenticated |
| F-11 | Build a map | slam_toolbox | |

### 2.3 Functions the item does not provide (and the record says so)

Emergency stop, protective stop on personnel detection, safely-limited speed monitored independently of the
command path, holding brake, battery protection, authenticated command path. See the gap assessment.

## 3. Item boundary

### 3.1 Inside the item

Chassis, drive train, encoders, Teensy firmware, Pi 5 and its ROS 2 stack, LiDAR, camera, IMU, the 24 V battery and
the onboard power distribution, the E-stop button hardware as fitted, the dock's AprilTag bundle.

### 3.2 Outside the item

The site (floor, slopes, doors, lighting, people, other vehicles), the Wi-Fi network and the operator's computer or
phone, the browser UI (assessed only at its interface), the mains supply and charger installation, the payload
and its restraint, the OpenAMRobot 2.0 upper body (arms, lift), the fleet server.

### 3.3 Interfaces

| Interface | Direction | Content | Integrity today |
|---|---|---|---|
| `/cmd_vel` (DDS → serial → firmware) | in | `geometry_msgs/Twist`, no header | No authentication, no sequence, no validity check; any publisher |
| `/debug/openloop`, `/debug/tune`, `/debug/enc_cal` | in | raw PWM, PID gains, encoder table | Same; `openloop` gated by a compile-time define that is on |
| `/odom/unfiltered`, `/imu/data_raw`, `/debug/*` | out | odometry, IMU, telemetry | Best effort |
| `/scan` → `/scan_filtered` | in | LiDAR, body-filtered | 1 s source timeout in the monitor; rear sector removed |
| `/goal_pose`, `/dock_trigger`, `/undock_robot`, lifecycle services | in | goals, dock commands, node state | Any DDS participant on domain 0 |
| Teensy PWM / FWD / REV → ZBLD drivers | out | 3 kHz PWM speed setpoint, direction | Driver BRK and ERR pins unwired |
| 24 V bus | power | battery ∥ mains to drivers and buck | No fuse, no disconnect |
| USB 5 V (Pi → Teensy) | power | logic supply for the firmware | Pi brown-out removes the controller while drivers stay live |

## 4. Limits of the machinery (ISO 12100 §5.3)

### 4.1 Use limits

| Limit | Value | Status | Source |
|---|---|---|---|
| Maximum commanded speed (navigation) | 0.20 m/s forward, 0.05 m/s reverse, 0.5 rad/s | configured | `sw: nav2_params.yaml:116-120` |
| Maximum commanded speed (docking) | `drive_speed`, `final_push_speed` parameters, unbounded; undock 0.10 m/s | configured | `sw: dock_trigger.yaml:22-23`; `dock_trigger.py:1370, 1641` |
| Firmware speed ceiling | 68 rpm ≈ 0.71 m/s (software clamp in kinematics) | configured | `fw: config/lino_base_config.h:69-70` |
| Mechanical maximum | 120 rpm ≈ 1.26 m/s no-load | by design | `hw: components-bom.md:54` |
| Minimum reliable speed | 0.04 m/s linear, 0.15 rad/s angular (stick-slip floor; below it motion is unpredictable) | measured 2026-07-02 | `fw: docs/safety/motion-safety.md` |
| Acceleration / deceleration | +1.0 / −2.5 m/s² linear, +3.0 / −3.0 rad/s² angular (commanded) | configured | `sw: nav2_params.yaml:124-131` |
| Stopping distance from 0.20 m/s | **(unknown)**; coast after PWM 0, never measured | — | GAP-02 |
| Payload | **(unknown)**; motor sizing example uses 45 kg total | — | `hw: datasheets/motor-sizing-calculations.md:209` |
| Robot mass | **(unknown)**; to be weighed | — | GAP-23 |
| Centre of gravity, tipping margin | **(unknown)** | — | GAP-23 |
| Slope | **(unknown)**; sizing example assumes 10°; castors stop on small steps | — | `motor-sizing-calculations.md:209`; `docs: mass-and-stability.md` |
| Floor | flat indoor floors; thresholds and cable covers at crawl speed (2.0 statement, applied here as an assumption) | assumed | `docs: reference/openamrobot-2/mass-and-stability.md` |
| Battery | ≥ 25 V at rest before any navigation test; below ~22 V under load the drivers under-volt and the robot fails to follow | operational rule | `sw: docs/safety/02_limits_and_watchdog.md` §4 |
| Endurance | 24 V 7 Ah; runtime **(unknown)** | — | |

### 4.2 Space limits

| Limit | Value | Source |
|---|---|---|
| Footprint (navigation polygon) | 0.805 m long (0.415 m ahead of `base_link`, 0.390 m behind) × 0.58 m wide, chamfered corners | `sw: nav2_params.yaml:172` |
| Height | **(unknown)** for the base; 2.0 complete robot ≤ 1700 mm at full lift | `docs: mass-and-stability.md` |
| Sensing plane | LiDAR 0.18 m above the floor (A1, Gate A unit mounted rotated 180°); S3 at 0.222 m for 2.0 | `sw: docs/navigation/01_architecture.md:122`; `hw: lidar.md:20` |
| Sensing coverage | forward and sides; rear sector [−45°, 49°] in the LiDAR frame removed; side returns < 0.40 m removed in two sectors | `sw: scan_body_filter_real.yaml:28-32` |
| Operating area | a mapped indoor area the operator has walked; the dock approach lane and the 0.7 m behind a docked robot are blind zones | `docs: use/monitoring/safety.md` |
| Reach of the operator | the physical stop (none) and the on-screen stop (software) | GAP-01, GAP-28 |

### 4.3 Time limits

| Limit | Value | Source |
|---|---|---|
| Command watchdog | 200 ms without `/cmd_vel` → PWM 0 | `fw: src/firmware.ino:611` |
| Velocity smoother timeout | 1.0 s without input → ramp to zero | `sw: nav2_params.yaml:348` |
| Collision monitor source timeout | 1.0 s stale scan tolerated | `nav2_params.yaml:358` |
| Agent ping | every 200 ms; loss → full stop | `fw: src/firmware.ino:280-289` |
| Lifecycle bond timeout | 60 s | `sw: navigation_launch.py:237` |
| Service life, maintenance intervals | **(unknown)**; upstream docs list daily/weekly/monthly checks as templates | `docs: maintain/routine/` |

### 4.4 Other limits

Indoor use only (IP rating unknown, motors IP20). Temperature range **(unknown)**; the Pi throttles at ~83 °C
without a cooler. Lighting: AprilTag docking needs the tags visible to the camera. Noise and EMC: not assessed.

## 5. Operating modes and states

| Mode | Who commands motion | Protective layers active | Notes |
|---|---|---|---|
| M0 Off / bench | nobody; 24 V off | none needed | Wheels off the ground for all first tests (upstream rule) |
| M1 Powered debug | `/debug/openloop`, calibration scripts | 300 ms staleness, 0.7·PWM clamp | Robot must be on blocks; path enabled in the deployed build |
| M2 Teleoperation | keyboard or UI | firmware watchdog only (teleop bypasses F-06, F-07) | No deadman |
| M3 Autonomous navigation | Nav2 controller and recoveries | F-05, F-06, F-07, watchdog | |
| M4 Docking / undocking | `dock_trigger` | watchdog only (F-07 deactivated, guard off) | Blind final approach and reverse |
| M5 Mapping | teleop while SLAM runs | as M2 | |
| M6 Fault / stopped | — | watchdog has fired or the agent is lost; PWM 0, no latch, no indication beyond an LED | Resumes as soon as commands return |

Transitions between M2, M3 and M4 are not arbitrated: whoever publishes last wins (GAP-36).

## 6. Legal requirements and standards

| Instrument | Applies because | Status in the record |
|---|---|---|
| Regulation (EU) 2023/1230 (Machinery), from 20 January 2027; Directive 2006/42/EC until then | a self-propelled machine placed on the EU market (upstream sells kits from Cyprus) | no conformity file, no declaration; the fork places nothing on the market |
| ISO 3691-4:2023 | driverless industrial truck in zones shared with people | not cited anywhere upstream |
| ISO 13849-1:2023 / -2:2012 | safety-related parts of the control system | not cited; no PL claimed |
| EN 60204-1:2018, ISO 13850:2015 | electrical equipment, emergency stop | E-stop parts cited to IEC 60947-5-5 only |
| ISO 12100:2010 | risk assessment | upstream asks the user to do it |
| IEC 62443-4-1/-4-2 | networked industrial control | not cited |
| Regulation (EU) 2024/1689 (AI Act) Annex I | when the learned policy (2.0 embodied-AI runtime) becomes a safety component | out of scope for this item |
| ANSI/A3 R15.08-1 | if deployed in the US (DQ-003) | not cited |

## 7. Known hazards and experience from similar items

- Upstream field notes: an unresolved intermittent left-wheel dropout (loose power or motor connector); the LiDAR
  "sometimes stops publishing on its own"; the Pi freezing on a bring-up current spike; a right wheel that "ran
  away" at 8× speed from a driver potentiometer setting before the open-loop configuration was adopted; docking
  aborts from self-view false positives that led to the guard being switched off.
- Industry experience for AMRs of this class (ISO 3691-4 Annex A hazards): collision with a person in the path or
  reversing, crushing against fixed structures, tipping on ramps or with a high payload, run-away on loss of
  control, unexpected start-up after a stop, electrical fire from an unfused traction battery.

## 8. Assumptions of use and external measures

| ID | Assumption | Holds today? | Where it is used |
|---|---|---|---|
| AOU-01 | A trained operator is present, watching the robot (not the screen), with the means to cut 24 V by hand, for every powered run | partly: upstream instructs it; no hardware disconnect exists | every hazard in WP-C-03 until SF-01 exists |
| AOU-02 | The operating area is clear of people during autonomous navigation, docking and undocking | procedural only | H-01, H-02 |
| AOU-03 | Wheels are off the ground whenever a powered debug path or calibration runs | procedural only; no interlock | H-04 |
| AOU-04 | The battery is ≥ 25 V at rest before a run | procedural only; no measurement | H-03 |
| AOU-05 | The Wi-Fi network carrying DDS is private and reaches only trusted hosts | not stated; a guest SSID is named in the docs | H-05 |
| AOU-06 | The floor is flat, dry, indoor, free of steps above the castor limit | assumed | H-06 |
| AOU-07 | The payload is restrained and within a mass and height limit **(to be set)** | no limit stated | H-06 |

## 9. Out of scope for this item

OpenAMRobot 2.0 (Jetson, STM32H723 base controller, ZLTECH hub motors with brakes, ZLAC8015D driver, Pilz PNOZ s3
safety chain, LiFePO4 pack with BMS, Orbbec camera, ultrasonic and cliff sensors), the OpenArm 2.0 dual arms, the
lift, the embodied-AI policy runtime and the fleet server. Decisions about them are tracked in the gap assessment
§8; they become a second item when their design is public (DQ-002, DQ-004).

## 10. Open items

| ID | Item | Needed by |
|---|---|---|
| OI-1 | Weigh the Gate A unit; measure height; record castor count and positions | WP-C-03 risk estimation (tipping, crushing) |
| OI-2 | Measure stopping distance from 0.20 m/s on the watchdog coast and on a commanded −2.5 m/s² stop, loaded and unloaded | WP-C-03, SF-02 field sizing |
| OI-3 | Set a payload limit and a payload height limit | AOU-07 |
| OI-4 | Resolve what the panel E-stop button switches on the as-built unit | GAP-01, SF-01 |
| OI-5 | Decide the regulatory frame (DQ-003) and the item scope (DQ-004); DQ-002 (Gate A unit) and DQ-005 (PL d) were decided 2026-10-20 | header fields of this document |
