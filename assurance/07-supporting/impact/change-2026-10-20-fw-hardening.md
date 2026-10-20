# Change record: firmware hardening of the Teensy overlay (assurance fork)

| Field | Value |
|---|---|
| Record | change-2026-10-20-fw-hardening |
| Change type | Fork change to safety-relevant code (motion firmware), the first on `openamr-platform-fw` |
| Repository and branch | `jherrodthomas/openamr-platform-fw`, branch `claude/wonderful-einstein-kr3bsf`, on top of upstream `f96014d` (BL-001) |
| Files | `boards/teensy_4_0/linorobot2_overlay/src/firmware.ino`, `config/lino_base_config.h`, `docs/safety/motion-safety.md` |
| Status | Draft: AI-authored (I0), **not compiled on the target toolchain at the time of writing (see §5), not run on hardware, not independently reviewed** |
| Author | Assurance team (AI-assisted) |
| Reviewer(s) | TBD (I1; must include someone who can flash and bench-test the Gate A unit) |
| Gap findings addressed | GAP-03, GAP-05, GAP-06, GAP-07, GAP-08 (partly), GAP-10 (partly), GAP-12 (`PWM_MIN`) |
| Safety functions touched | SF-04 (stop on loss of command), SF-06 (stop on drive fault, draft), SF-07 (powered-debug inhibit); SF-03 only as a command-input ceiling, **not** an independent speed monitor |

## 1. What changes

| # | Change | Behaviour before | Behaviour after | Finding |
|---|---|---|---|---|
| 1 | **Hardware watchdog.** i.MX RT1062 WDOG1 enabled in `setup()` with a 1.0 s timeout (`WT = 1`), serviced from the 50 Hz control-timer callback while the agent is connected and from `loop()` otherwise | no hardware watchdog; a hung core or wedged executor left the last PWM latched | a stall of the control loop or the main loop longer than 1 s resets the MCU; the Motor constructors put PWM at 0 at boot; the reset cause is reported | GAP-03 |
| 2 | **Reset cause and version.** `SRC_SRSR` is read at boot and cleared; a `std_msgs/String` on `/firmware/status` at 1 Hz carries version, reset cause, watchdog timeout, powered-debug flag, motion-fault bits, calibration-loaded flag, rejected and clamped command counters, uptime | no version, no reset cause, no way to see a silent reboot or a missing calibration table | the host can detect a watchdog reset, a lost table and rejected commands | GAP-09, GAP-10 |
| 3 | **`/cmd_vel` validation.** Non-finite `linear.x`, `linear.y` or `angular.z` → the command becomes zero and the watchdog is **not** fed (the base stops within 200 ms); the magnitude of `linear.x` clamped to `CMD_VEL_MAX_LINEAR_MPS` (0.71 m/s) and the magnitude of `angular.z` to `CMD_VEL_MAX_ANGULAR_RPS` (3.1 rad/s); `linear.y` forced to 0 | NaN went straight into kinematics; no bound before the rpm clamp | a malformed command is a stop; ceilings equal today's effective limits so there is no behaviour change for valid commands (DQ-006 asks whether to lower them) | GAP-06 |
| 4 | **Powered debug OFF by default.** `ENABLE_POWERED_DEBUG` commented out: `/debug/openloop` cannot drive the motors and `/debug/tune` is rejected (counted) in the reference build; a bench image defines it | on in the deployed build | production image cannot be driven or retuned from the debug topics | GAP-07, GAP-08 |
| 5 | **`/debug/tune` bounded** (bench image only): all six fields must be finite; Kp, Ki, Kd in [0, 50]; right-wheel gain in [0.5, 2.0]; feedforward ≤ 50; dither ≤ 200; otherwise the whole message is rejected and counted | any value accepted, including NaN, zero and negative gains, unbounded right-wheel gain (which defeated the open-loop clamp) | | GAP-07 |
| 6 | **`/debug/enc_cal` validated whole-table.** All 72 ratios must be finite and in [0.5, 2.0]; otherwise nothing is loaded and the rejection is counted | only a length check; a wrong table silently changed the velocity loop and odometry | | GAP-07, GAP-09 |
| 7 | **Stall / encoder-loss stop (SF-06 draft).** In closed loop, a wheel commanded above 60 % of `PWM_MAX` whose measured speed stays below 2 rpm for 1 s latches a motion fault; both wheels are stopped and the PIDs reset; the latch clears after `/cmd_vel` has commanded zero (with the watchdog fed) for 1 s | PID saturated indefinitely on a dead encoder or jammed wheel; the other wheel kept driving | | GAP-04 (partly), GAP-05 |
| 8 | **`PWM_MAX` / `PWM_MIN` parenthesised.** `PWM_MIN` was `-pow(2, PWM_BITS) - 1` = −1025; now −1023 | asymmetric clamp by 2 counts in reverse | symmetric | GAP-12 |

## 2. What does not change

The control law (feedforward, PID, dither, velocity estimator), the 200 ms command watchdog, agent-loss stop, the
rpm clamp in kinematics, odometry, IMU handling, topics and QoS of existing publishers and subscribers, pin map,
drivetrain constants. No new executor handle is needed (publishers do not take one).

## 3. Impact analysis

| Area | Impact |
|---|---|
| Hazards (WP-C-03) | H-02 (uncommanded motion): reduced by 3, 4, 5, 6. H-03 (loss of control): reduced by 7. H-05 (unexpected start-up): the fault latch (7) auto-clears on a zero command; SF-05's deliberate reset is **not** provided and remains open. H-11: a controller hang now ends in a reset instead of a latched PWM (1). H-12: the consequence of an unauthorised `/debug/tune` or `/debug/enc_cal` is bounded; the topics are still unauthenticated |
| Safety functions | SF-04 gains a hardware watchdog (towards Category 2); SF-06 gets a first detector; SF-07 is implemented at build time (bench image still has the paths, bounded). No change to SF-01, SF-02, SF-03 |
| Assumptions of use | AoU-03 (wheels off the ground for debug) now also protects against a bench image flashed by mistake, since the reference build refuses the debug paths |
| Behaviour change for valid commands | none intended: the ceilings equal today's effective limit. The stall detector can trip when the robot pushes against a wall or a wheel is blocked, which is the intended reaction |
| False trips of the stall detector | pushing a heavy payload up a ramp from standstill at high PWM with the wheels not yet turning for 1 s would latch; the thresholds (60 % PWM, 2 rpm, 1 s) are drafts for the bench test to confirm |
| Reset behaviour | a watchdog reset drops the runtime encoder table and any bench tuning, exactly as a power cycle does today; the status message makes it visible |
| Work products to update | WP-C-03 §7 (SF-04, SF-06, SF-07 "implements today"), gap assessment status notes on GAP-03, 05, 06, 07, 08, 10, 12, WP-C-01 §2.2 F-02 |
| Upstream | all changes are inside the overlay files upstream already modifies; a pull request upstream is possible once bench-tested. Upstream's agent rules forbid agents from changing watchdog code without two human approvals; the fork's equivalent is this record and the lead's review |

## 4. Register decisions raised

- DQ-006 (open): lower the firmware command ceilings to the navigation limits (0.20 m/s, 0.5 rad/s), keep them at the
  mechanical clamp (0.71 m/s), or set a zone-dependent limit later with SF-03.
- Stall-detector thresholds: `decider: claude`, recorded as assumed; the bench test can change them.

## 5. Verification

| Step | Status |
|---|---|
| Static re-read of the diff against the i.MX RT1060 reference manual (WDOG1 WCR/WSR, SRC_SRSR) and the Teensy core `imxrt.h` macro names | done by the author (I0) |
| Compile for `teensy40` with PlatformIO against linorobot2_hardware `aaf9d59` and micro-ROS Jazzy | **not done.** The authoring session's network policy blocks the PlatformIO registry (`api.registry.platformio.org`, `dl.registry.platformio.org`), so the Teensy platform could not be installed. The reviewer compiles first; a compile failure returns the change to draft |
| Host unit tests of the validation logic | not yet (no host test harness exists; GAP-11 action 6) |
| Bench test on the Gate A unit, wheels off the ground: watchdog reset by stalling the loop, NaN command stops, clamp, tune rejection in the reference image, stall latch and clear | **not done** |
| Stopping-distance measurement | not done; unaffected by this change |

Until the bench test is recorded, this change is a draft and the firmware status stays "not verified on hardware".
