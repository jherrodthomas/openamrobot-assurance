# Reference robot

The first configuration the assurance work analyses is upstream's **Gate A unit**: the robot that has been wired,
flashed and driven. It is a starting point, not a limit: the 2.0 design is tracked and joins the claimed scope when
its drawings and code reach a repository, through a documented impact analysis. This page says what the reference
configuration is, why it was chosen, and what the fork adds to it before any test.

> **Nothing about this robot is approved for operation around people.** As inherited it has no emergency stop in
> its documented wiring, no brakes, no battery fuse, no disconnect and no safety-rated personnel detection
> ([gap assessment](../assurance/00-assessment/gap-assessment.md)).

## The Gate A unit at a glance

| Attribute | Value | Source |
|---|---|---|
| Base | v0.0.1 differential-drive base, two ZD BLDC motors with ZBLD.C20-120L2R drivers in open-loop power-stage mode | gap assessment §3.1 |
| Compute | Raspberry Pi 5 (ROS 2 Jazzy, Nav2) and a Teensy 4.0 (firmware on the linorobot2 base), micro-ROS over USB serial | gap assessment §3.1 |
| Sensing | RPLIDAR A1 (functional sensing, not a safety device), AS5040 encoders, MPU6500 IMU | gap assessment §3.1, §5 |
| Power | Two 12 V lead-acid batteries; 24 V bus "permanently live and unprotected"; battery and mains in parallel | GAP-19, GAP-20 |
| Speed | Firmware limit 68 rpm ≈ 0.71 m/s; Nav2 limit 0.20 m/s forward | gap assessment §3.1, §4.1 |
| Stop | A 200 ms software watchdog that sets PWM to zero and lets the wheels coast | GAP-02, GAP-03 |
| Mass, payload, centre of gravity, stopping distance | Not stated anywhere | GAP-23 |
| Track | 0.46 m as built (0.4075 m in CAD) | GAP-23 |

## What the fork adds before any test

The hold point [WP-V-07](../assurance/06-validation/WP-V-07-test-operations.md) requires bench safety hardware on any
unit the fork drives: a battery fuse and lockable disconnect, a dual-channel emergency stop on a pendant through a
safety relay that drops the driver supply, both drivers' fault outputs read by the firmware, a reproducible firmware
build with the watchdog on and the debug path off, a command arbiter, and a marked test area with nobody in it.
Buying that hardware is a decision for the lead (DQ-011). The bench chain is carried forward as the first draft of
the product chain, not thrown away.

## What the reference configuration fixes

[WP-M-01 §3.1](../assurance/01-management/WP-M-01-assurance-strategy.md#31-reference-configuration-the-only-scope-claims-apply-to)
makes the reference configuration the only scope the claims apply to:

| Element | Reference configuration |
|---|---|
| Robot | The Gate A unit plus the bench safety hardware; later the product safety chain of WP-S-03 |
| Function | Autonomous navigation and docking of the mobile base in a defined indoor operating area; teleoperation for test. No arm, no lift (DQ-004) |
| Software | A tagged fork release that pins the three platform repositories, the linorobot2 base, the ROS 2 distribution and the container image |
| Operating environment | Defined in [WP-C-02](../assurance/02-concept/WP-C-02-operating-environment-and-tasks.md): indoor, level floor, defined zones, defined people presence |
| Operator | A trained test operator with a hand on the bench E-stop during development; briefed personnel after release |

## Why the Gate A unit and not the 2.0 design

OpenAMRobot 2.0 (Jetson, STM32H723 base controller, hub motors with brakes, a Pilz PNOZ s3 safety relay, two
certified E-stops, contactors, a 110 A fuse and a lockable disconnect, dual arms and a lift) is decided in
upstream's register and due as a release candidate on 20 November 2026, but none of it is in a public repository.
A safety case can only be built on what can be read and tested. The recommendation (decision DQ-002) is to assess
the Gate A unit now and track the 2.0 decisions as claims to verify; most findings carry over, because the ROS 2
stack and the firmware pattern stay the same. The hardware findings on Gate A will be overtaken and re-stated.

## Adding the 2.0 base, the arms or the lift

1. Record the new configuration with its item boundary and the interface assumptions the base case already states
   for the arms (stop chain hooks, payload, centre of gravity).
2. Write the impact analysis ([WP-M-11](../assurance/01-management/WP-M-11-impact-analysis.md) format): which
   hazards, safety functions, requirements and assumptions hold, which differ, and what evidence each needs.
3. Extend the risk assessment with the ISO 10218-2 and ISO/TS 15066 hazards of the arms and the lift.
4. Verify the 2.0 chain against the claims recorded from upstream's register (GAP-33) once its drawings arrive.
5. Run the generators and open a pull request.
