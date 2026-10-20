# Architecture

<p align="center">
  <img src="assets/openamrobot/architecture.svg" width="100%" alt="Platform architecture in three layers: the ROS 2 functional stack, the hardened Teensy firmware, and the hardwired safety chain, with a cross-cutting assurance column. The chain is the only layer with a Performance Level target.">
</p>

OpenAMRobot inherits the right shape for a safety argument: a large ROS 2 stack (Nav2, docking, teleoperation, an
operator UI, and in future a learned policy) in front of a small firmware layer on a separate microcontroller that is
the last software before the motors. The fork keeps that shape and adds a third layer below it: a hardwired safety
chain that removes actuator power and engages the brakes without any software in the loop.

| Layer | Role | Standard | Claim |
|---|---|---|---|
| ROS 2 functional stack (Raspberry Pi 5) | Decides where to go and how fast; publishes requests | Hardened as defence in depth; cybersecurity under IEC 62443 | No Performance Level. Upstream calls it "best-effort" and the fork agrees |
| Teensy 4.0 firmware | The last software before the motors: validates commands, times out, clamps, reads driver faults | ISO 13849-1 §7 practices, as "could be claimed later" | No Performance Level in the first safety case ([WP-M-01](../assurance/01-management/WP-M-01-assurance-strategy.md) T-04) |
| Hardwired safety chain | Two-channel E-stops and safety-scanner outputs into a safety relay that drops two contactors and engages the brakes | ISO 13849-1 categories, MTTFD, DCavg, CCF; EN 60204-1; ISO 13850 | **PL d target** for the emergency stop and the protective stop (decision DQ-005) |

The argument is a doer-and-checker argument with one more step: the ROS 2 stack proposes, the firmware
checks, and the chain is the checker of last resort that nothing in software can override. The full strategy is
[WP-M-01 §6](../assurance/01-management/WP-M-01-assurance-strategy.md#6-safety-architecture-argument-the-central-strategy);
the architecture work products are [WP-S-03](../assurance/03-system/WP-S-03-srpcs-architecture.md) (the chain),
[WP-W-03](../assurance/05-software/WP-W-03-software-architecture.md) (the software) and
[WP-A-05](../assurance/08-analyses/WP-A-05-independence-of-the-safety-chain.md) (why the chain is independent of the
stack).

**Today none of the chain exists.** The Gate A unit as inherited has no E-stop, no brakes, no fuse and no disconnect;
its only stop is a software watchdog on the same core that drives the motors. The first engineering act of the fork
is the bench safety hardware of [WP-V-07](../assurance/06-validation/WP-V-07-test-operations.md).
