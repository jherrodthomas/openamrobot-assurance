# WP-C-07 Cybersecurity threat and risk assessment

| Field | Value |
|---|---|
| Work product | WP-C-07 Cybersecurity threat and risk assessment |
| Standard reference | IEC 62443: 62443-4-1 SR-1 (product security context), SR-2 (threat model); 62443-3-2 ZCR 1…ZCR 6 (security risk assessment, zones and conduits); 62443-3-3 §4 (security levels); ASPICE: SEC.1 |
| Version | 0.1 (2026-10-23): first content. Threat actors TA-1…TA-5 with the security level each implies; assets A-01…A-16; security zones SZ-1…SZ-5 and conduits CD-1…CD-6 (Figure 4-1); threat scenarios TS-01…TS-20 seeded from GAP-06…GAP-40; risk before treatment, with the safety architecture of WP-S-03, and after the requirements of WP-C-08 (Figure 6-1); the security level target of DQ-013 checked against every scenario; residual risk. 0.0: skeleton |
| Status | Draft |
| PL / scope | Both configurations: CFG-001, the Gate A unit (bench only, DQ-011 C), as inherited at BL-001; CFG-002, the 2.0 mobile manipulator, as upstream has decided it (unverified, WP-C-01 §1.2) |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD: interim cybersecurity review CS-I1, external (WP-M-06 §7; unscheduled while DQ-010 C holds) |
| Approver | Cybersecurity manager (WP-M-08 §5) |
| Baseline | BL-001 |

> [!WARNING]
> Draft. No scenario here has been tried on a robot: there is no penetration test, and the likelihoods are
> engineering judgement from the upstream record and the gap assessment. The safety architecture that lowers the
> impact column (WP-S-03) is a design; nothing of it is built. Clause numbers of the IEC 62443 series, and the
> security level each component requirement belongs to, are from memory and are to be checked against licensed
> copies (DQ-016, answered C: unscheduled until an assessor is engaged). Everything said about CFG-002 rests on
> upstream's plan set.

## 1. Purpose and method

This assessment answers three questions for the robot as one IEC 62443-4-2 component: who can attack it and
through which path, what each attack can do to a person, and whether the security level target the lead set on
2026-10-20 (DQ-013 A, [WP-C-08 §2](WP-C-08-cybersecurity-requirements-and-sl-target.md#2-security-level-target))
covers what is found. Its outputs are the threat scenarios that [WP-C-08](WP-C-08-cybersecurity-requirements-and-sl-target.md)
turns into requirements CSR-nn, the zones and conduits that [WP-S-07](../03-system/WP-S-07-cybersecurity-architecture.md)
designs, and the cyber-induced hazards that [WP-C-03](WP-C-03-risk-assessment.md) rates as H-12.

**The rule of this record.** A cybersecurity measure lowers the likelihood that an attack succeeds; the safety
architecture lowers what a successful attack can do. Neither is credited for the other's job. Every scenario
below is therefore rated three times: before any measure (the robot as inherited), with the safety functions of
[WP-C-04](WP-C-04-safety-functions-and-plr.md) as WP-S-03 designs them but no cybersecurity measure, and after
the requirements of WP-C-08 with that safety architecture in place.

### 1.1 Steps of IEC 62443-3-2 and where each lands

| Step | What it asks | Here |
|---|---|---|
| ZCR 1 | Identify the system under consideration | §2, with the item boundary of [WP-C-01 §3](WP-C-01-item-definition.md#3-item-boundary) |
| ZCR 2 | Initial cybersecurity risk assessment | §6, column "before treatment" |
| ZCR 3 | Partition into zones and conduits | §4 and Figure 4-1 |
| ZCR 4 | Compare the initial risk with the tolerable risk | §6, §1.3 |
| ZCR 5 | Detailed risk assessment: threats, vulnerabilities, consequences, likelihood, security level target, countermeasures, residual risk | §5, §6, §7, §8 |
| ZCR 6 | Document the requirements, assumptions and constraints | [WP-C-08](WP-C-08-cybersecurity-requirements-and-sl-target.md) §4 and §6; §10 here |
| ZCR 7 | Approval by the asset owner | the lead, through the decision register (§8) |

62443-4-1 SR-1 (security context) is §2 and §1.2; SR-2 (threat model: data flows, trust boundaries, entry
points) is §4 and §5.

### 1.2 Threat actors

The security levels are those of IEC 62443-3-3 §4: SL 1 protects against casual or coincidental violation, SL 2
against intentional violation with simple means, low resources and generic skills, SL 3 against sophisticated
means and system-specific skills. The actor sets the level a scenario needs.

| Actor | Who | Means | SL implied |
|---|---|---|---|
| TA-1 | A person on the site network: staff, visitor or contractor on the shared or guest Wi-Fi | a laptop with the public ROS 2 tools, a browser, a Wi-Fi jammer bought online | 2 |
| TA-2 | Nobody intending harm: a developer's simulation, a forgotten teleoperation node, a second robot on the same domain, a misconfigured fleet server | the normal tools, by mistake | 1 |
| TA-3 | A compromised or drifting dependency: base image, package, reusable CI workflow, model hub; the developer is the victim | whatever the dependency carries | 2 |
| TA-4 | A person with physical access to the robot: staff, cleaner, contractor, maintainer | a USB cable, a laptop with the vendor tools, a CAN adapter, a screwdriver | 2 |
| TA-5 | A sophisticated attacker | custom exploits, sensor-spoofing equipment, a targeted supply-chain attack | 3 |

TA-5 is outside the target of DQ-013 A. Scenarios that need it are listed (§7) so that the safety architecture,
not a security measure, is known to be what carries them.

### 1.3 Scales and tolerable risk

| Likelihood | Meaning |
|---|---|
| 4 almost certain | happens by mistake in normal use, or needs nothing but network access and a browser |
| 3 likely | needs network access and public tools or documentation |
| 2 possible | needs physical access, specific knowledge or a compromised dependency |
| 1 unlikely | needs sophisticated means, or every documented path is closed by a requirement |

| Impact | Meaning |
|---|---|
| 4 severe | can cause, or fail to prevent, a hazard WP-C-03 rates S2 (serious, normally irreversible injury) |
| 3 major | can cause motion nobody commanded, but only within the limits the safety functions hold; or an S1 hazard |
| 2 moderate | loss of availability, a protective stop, loss of a layer with no safety claim, loss of evidence, disclosure of personal data |
| 1 minor | nuisance; disclosure of nothing that matters |

Risk is likelihood × impact: **1–3 low**, **4–8 medium**, **9–16 high**. Low risk is tolerable. Medium risk is
tolerable only as a residual the lead accepts in writing (§8). High risk is not tolerable.

## 2. System under consideration

The item of [WP-C-01](WP-C-01-item-definition.md) on both configurations, plus the development and supply chain
that builds what runs on it, because the gap assessment shows that chain is a path in (GAP-29). The site network,
the operator's devices and the fleet server are outside the item and are treated as an untrusted zone; what this
record needs from the site is written as requirements on it (WP-C-08 §6) and carried to the information for use.

**Security context (62443-4-1 SR-1).** The robot works in a workshop or a warehouse with staff, visitors and
contractors on a shared Wi-Fi (WP-C-02 §2). It carries no secrets. Its cameras see people, so their images are
personal data. Its operator interface is a browser page (CFG-001) or a tablet (CFG-002). It is maintained by
people who open the chassis and flash firmware. At BL-001 none of its interfaces authenticates anything
([GAP-27](../00-assessment/gap-assessment.md)), and the on-screen stop is a network request (GAP-28).

## 3. Assets

| ID | Asset | Config | Element | What must hold | FR |
|---|---|---|---|---|---|
| A-01 | Motion command path: `/cmd_vel` to the firmware (IF-01); the Jetson to STM32 link (IF-14) | both | E-03, E-04; E-12, E-13 | integrity, authenticity, freshness | FR 1, FR 2, FR 3 |
| A-02 | Firmware tuning, calibration and diagnostic inputs: `/debug/tune`, `/debug/enc_cal`, `/debug/openloop` (IF-02) | both | E-03; E-12 | integrity | FR 3 |
| A-03 | Navigation configuration and node state: Nav2 parameters, the collision monitor's lifecycle state (IF-05) | both | E-04; E-13 | integrity | FR 2, FR 3 |
| A-04 | Docking, undocking and goal commands (IF-05) | both | E-04; E-13 | authenticity | FR 1, FR 2 |
| A-05 | Firmware image and its build | both | E-03; E-12 | integrity, authenticity | FR 3 |
| A-06 | Compute operating system, container images and their dependencies | both | E-04; E-13 | integrity | FR 3 |
| A-07 | Operator interface: Flask on 5050, rosbridge on 9090, the video server on 8080; the tablet on CFG-002 (IF-15) | both | E-04; E-13, E-20 | authenticity, availability | FR 1, FR 7 |
| A-08 | Sensor data for navigation and docking: scan, cameras (IF-04) | both | E-05, E-06; E-14 | integrity, availability | FR 3, FR 7 |
| A-09 | Safety-device configuration: protective field sets, speed-monitor thresholds (SR-00.05) | both | safety chain (WP-H-02; E-16) | integrity | FR 3 |
| A-10 | The safety chain: emergency stops, safety relay, contactors, reset | both | safety chain (WP-H-02; E-16) | availability | FR 5, FR 7 |
| A-11 | Arm, gripper and lift commands (IF-11, IF-12) | CFG-002 | E-13, E-17, E-18 | integrity, authenticity | FR 1, FR 2, FR 3 |
| A-12 | Policy runtime and its model weights (WP-C-09) | CFG-002 | E-13 | integrity | FR 3 |
| A-13 | Internal buses CAN1 (drive), CAN2 (BMS), CAN3 (lift) (IF-09, IF-10, IF-11) | CFG-002 | E-11, E-12, E-15, E-17 | integrity | FR 3, FR 5 |
| A-14 | Logs and telemetry | both | E-04; E-13 | integrity, availability | FR 6 |
| A-15 | Camera images of people and the site map | both | E-06; E-14, E-19 | confidentiality (personal data) | FR 4 |
| A-16 | Remote administration (SSH) and the accounts on the compute | both | E-04; E-13 | authenticity | FR 1 |

## 4. Zones and conduits

A zone groups what shares one set of security requirements; a conduit is the only path between two zones. The
zones here are security zones SZ-n; they are not the operating zones Z0…Z5 of WP-C-02.

### 4.1 Zones

| Zone | Name | Contains | Assets | Trust |
|---|---|---|---|---|
| SZ-1 | Site network | Wi-Fi, operator computers, tablets and phones, the fleet server, other robots | none (outside the item) | untrusted |
| SZ-2 | Robot compute | Raspberry Pi 5 (CFG-001) or Jetson (CFG-002): the ROS 2 graph, the operator gateway, containers, the manipulation server and the policy runtime | A-01, A-03, A-04, A-06, A-07, A-08, A-11, A-12, A-14, A-15, A-16 | trusted once authenticated |
| SZ-3 | Motion control | Teensy (CFG-001) or STM32 (CFG-002) firmware, motor drivers, encoders, the CAN buses to the drive, BMS and lift, the arm joint drives | A-01, A-02, A-05, A-11, A-13 | trusted; channel 1 of the two-channel functions |
| SZ-4 | Safety chain | emergency stops, safety relay, contactors, reset, the safety scanner and speed monitor with their configuration | A-09, A-10 | highest; no data conduit in during operation |
| SZ-5 | Development, supply and maintenance | build hosts, the repositories and their CI, container registries, upstream repositories, the model hub, the maintainer's laptop | A-05, A-06, A-12 | outside the item; controlled by process |

### 4.2 Conduits

| Conduit | From | To | Carries | Interfaces | At BL-001 |
|---|---|---|---|---|---|
| CD-1 | SZ-1 | SZ-2 | operator traffic (HTTP 5050, websocket 9090, video 8080), SSH; today also DDS discovery and every topic of domain 0 | IF-05, IF-15 | open: no authentication, multicast DDS on the site Wi-Fi (GAP-27) |
| CD-2 | SZ-2 | SZ-3 | commands down (motion, tuning, arm and lift); odometry, IMU and status up | IF-01, IF-02, IF-03, IF-12, IF-14 | micro-ROS over USB serial with no authentication (CFG-001); protocol not public (CFG-002) |
| CD-3 | SZ-4 | SZ-3 | chain state as diagnostic inputs (emergency-stop spare contact, reset, relay state) through isolated inputs; one way | IF-13 | designed (WP-H-02; upstream `SAFETY-CHAIN-IO`), not built |
| CD-4 | SZ-5 | SZ-2 | images, packages, configuration and model weights at deployment | none | unpinned (GAP-29) |
| CD-5 | SZ-5 | SZ-3 | a firmware image flashed by a maintainer over USB (CFG-001) or the debug port (CFG-002) | none | manual copy, no image identity (GAP-10) |
| CD-6 | SZ-5 | SZ-4 | safety-device configuration with the vendor tool at commissioning only, disconnected in operation | none | not built |

![Figure 4-1: the five security zones as boxes: the site network on the left, the robot compute in the middle, motion control to its right and the safety chain at the far right with a heavy border, the development, supply and maintenance zone along the bottom. Arrows are the conduits CD-1 to CD-6, each labelled with what it carries. The only arrow into the safety chain is CD-6, dashed, for configuration at commissioning; the only data arrow out of it is CD-3, one way into motion control. A note says no conduit from the network reaches the safety chain](figures/fig-c07-4-1-zones-conduits.svg)

*Figure 4-1.* Zones and conduits. The design rule the figure shows is the one WP-S-03 §1 states: no input of the
safety chain is reachable from the network. The chain reports its state one way (CD-3) and is configured only at
commissioning with the device disconnected afterwards (CD-6). Generated by
[`figures/fig_c07.py`](figures/fig_c07.py) from §4.1 and §4.2; CI fails if it is stale.

Physical access is a boundary of its own: the chassis encloses SZ-3 and SZ-4, and TA-4 crosses it with a
screwdriver. The scenarios that need it say so.

## 5. Threat scenarios

Seeded from the gap assessment's software, firmware and cybersecurity findings, the interfaces of WP-C-01 §3.3
and §3.3a, and the misuses MU-09 and MU-10 of [WP-C-06](WP-C-06-human-robot-interaction-and-misuse.md).
Safety impact is anchored to the hazard list of WP-C-03: the hazard column names the hazards a scenario can cause,
and "none" marks a scenario with no path to a person.

| ID | Scenario | Actor | Conduit | Assets | Exploits | Hazard | Config |
|---|---|---|---|---|---|---|---|
| TS-01 | A person on the site Wi-Fi discovers the robot on DDS domain 0 and publishes `/cmd_vel` with the public ROS 2 tools | TA-1 | CD-1 | A-01 | GAP-27, GAP-06 | H-12, H-01, H-02 | both |
| TS-02 | A forgotten teleoperation node or a stale publisher keeps re-sending an old `/cmd_vel`; every message refreshes the firmware watchdog, so the robot keeps moving after the operator stopped | TA-2 | CD-1, CD-2 | A-01 | GAP-06, GAP-36 | H-02 | both |
| TS-03 | Someone on the network retunes the velocity loop, raises `motor2_gain`, loads a wrong encoder table or drives raw PWM through `/debug/*` | TA-1 | CD-1, CD-2 | A-02 | GAP-07, GAP-08 | H-12, H-03, H-04 | both |
| TS-04 | Someone calls the collision monitor's lifecycle service to deactivate it, or sets the Nav2 speed and acceleration parameters at runtime | TA-1 | CD-1 | A-03 | GAP-27, GAP-37 | H-12, H-01, H-11 | both |
| TS-05 | Someone triggers an undock or a docking goal while a person stands behind the robot; the undock is a blind reverse | TA-1 | CD-1 | A-04 | GAP-27, GAP-35 | H-12, H-01 | both |
| TS-06 | Anyone with a browser opens the operator UI or rosbridge from the site network and drives the robot, or calls any service through rosbridge | TA-1 | CD-1 | A-07, A-01 | GAP-27 | H-12, H-01 | both |
| TS-07 | The site Wi-Fi drops or is jammed; the on-screen stop does nothing, and the operator believes the robot is stopped | TA-1 | CD-1 | A-07 | GAP-28 | H-10, H-01 | both |
| TS-08 | A flood of DDS discovery or traffic from the site network starves the robot graph; scans and commands arrive late and the collision monitor works on stale data | TA-1 | CD-1 | A-08, A-01 | GAP-16, GAP-27 | H-11, H-01 | both |
| TS-09 | Someone with access to the chassis flashes a modified or wrong firmware image; nothing on the robot reports which image runs | TA-4 | CD-5 | A-05 | GAP-10 | H-02, H-03 | both |
| TS-10 | An unpinned dependency (the reusable CI workflow at `@main`, the base image, an apt or rosdep package, the micro-ROS agent) changes or is compromised and the next build carries it onto the robot | TA-3 | CD-4 | A-06, A-05 | GAP-29, GAP-32 | H-12 | both |
| TS-11 | A flaw in a network-facing service gives its process root on the compute, because the container runs as root with host networking and access to the serial device | TA-1 | CD-1 | A-06, A-01, A-16 | GAP-29 | H-12 | both |
| TS-12 | Someone with a laptop and the vendor tool shortens a protective field or raises a speed-monitor threshold on the safety device | TA-4 | CD-6 | A-09 | none (not built) | H-01 | both |
| TS-13 | Someone spoofs or blinds the navigation LiDAR, or shows the camera a false AprilTag, so the robot navigates or docks on false data | TA-5 | none (at the sensor) | A-08 | GAP-14 | H-01, H-11 | both |
| TS-14 | Someone on the network sends goals to the manipulation server or the policy runtime, or joint commands through the compute onto the arms' bus | TA-1 | CD-1, CD-2 | A-11 | gap assessment §8 | H-12, H-13, H-15 | CFG-002 |
| TS-15 | A swapped or altered policy model is loaded and the arms act on it | TA-3 | CD-4 | A-12 | none (WP-C-09) | H-13 | CFG-002 |
| TS-16 | Someone with access inside the chassis injects frames on CAN1, CAN2 or CAN3: drive commands, a false healthy BMS state, lift motion | TA-4 | none (inside the chassis) | A-13 | none | H-02, H-09, H-15 | CFG-002 |
| TS-17 | Logs are lost, altered or never written, so an incident cannot be reconstructed; or telemetry is presented as safety evidence | TA-2 | CD-1 | A-14 | GAP-13 | none | both |
| TS-18 | Anyone on the site network watches the camera streams of people through the open video server | TA-1 | CD-1 | A-15 | GAP-27 | none | both |
| TS-19 | A developer's simulation, a second robot or a fleet test on the same Wi-Fi and the same domain publishes `/cmd_vel` to the real robot | TA-2 | CD-1 | A-01 | GAP-27, GAP-40 | H-12, H-02 | both |
| TS-20 | Someone logs into the compute over SSH from the site network with a default, shared or leaked credential | TA-1 | CD-1 | A-16 | none (the image's SSH set-up is not documented upstream) | H-12 | both |

Notes:

- TS-03 is written for the Gate A firmware. The STM32 firmware of CFG-002 is not public; if it keeps tuning or
  raw-drive inputs, the scenario and its treatment apply to it unchanged.
- TS-12 and the safety-device half of A-09 appear once the bench build of WP-H-02 (DQ-007 A: a safety scanner and
  a rear bumper) or the 2.0 chain exists. Neither exists today.
- TS-13 is a sensing attack, not a network one; its counterpart without an attacker (the LiDAR that stops
  publishing on its own, the low obstacle) is in [WP-C-10](WP-C-10-functional-insufficiency-analysis.md).

## 6. Risk assessment

"Before treatment" is the robot as inherited at BL-001, or for an element not yet built, the design with no
security measure and no safety function. "With WP-S-03" keeps the likelihood and lowers the impact by what the
designed safety functions hold. "After" applies the requirements of WP-C-08 with the safety architecture in place.
The FR column names the foundational requirements the treatment relies on.

| ID | L | I | Before | I with WP-S-03 | FR | SL needed | Treatment | L after | Residual |
|---|---|---|---|---|---|---|---|---|---|
| TS-01 | 3 | 4 | 12 high | 3 | FR 1, FR 2, FR 5 | 2 | CSR-01, CSR-02, CSR-03, CSR-04, CSR-23 | 1 | 3 low |
| TS-02 | 4 | 4 | 16 high | 3 | FR 3 | 1 | CSR-04, CSR-05 | 1 | 3 low |
| TS-03 | 3 | 4 | 12 high | 3 | FR 3, FR 7 | 2 | CSR-09, CSR-10 | 1 | 3 low |
| TS-04 | 3 | 4 | 12 high | 2 | FR 2, FR 3 | 2 | CSR-01, CSR-02, CSR-03, CSR-10 | 1 | 2 low |
| TS-05 | 3 | 4 | 12 high | 3 | FR 1, FR 2 | 2 | CSR-01, CSR-02, CSR-03, CSR-04 | 1 | 3 low |
| TS-06 | 4 | 4 | 16 high | 3 | FR 1, FR 2, FR 5 | 2 | CSR-06, CSR-14, CSR-23 | 1 | 3 low |
| TS-07 | 3 | 4 | 12 high | 2 | FR 7 | 2 | CSR-07, CSR-08, CSR-21 | 3 | 6 medium |
| TS-08 | 3 | 4 | 12 high | 2 | FR 5, FR 7 | 2 | CSR-01, CSR-21 | 1 | 2 low |
| TS-09 | 2 | 4 | 8 medium | 3 | FR 3 | 2 | CSR-11, CSR-17, CSR-22 | 1 | 3 low |
| TS-10 | 2 | 4 | 8 medium | 3 | FR 3 | 2 | CSR-12, CSR-13 | 1 | 3 low |
| TS-11 | 2 | 4 | 8 medium | 3 | FR 2, FR 5 | 2 | CSR-03, CSR-12, CSR-14 | 1 | 3 low |
| TS-12 | 2 | 4 | 8 medium | 4 | FR 1, FR 3 | 2 | CSR-16, CSR-17 | 1 | 4 medium |
| TS-13 | 1 | 4 | 4 medium | 2 | FR 3 | 3 | none: outside the SL-T (§7) | 1 | 2 low |
| TS-14 | 3 | 4 | 12 high | 3 | FR 1, FR 2, FR 5 | 2 | CSR-02, CSR-03, CSR-18 | 1 | 3 low |
| TS-15 | 2 | 4 | 8 medium | 3 | FR 3 | 2 | CSR-13, CSR-19 | 1 | 3 low |
| TS-16 | 2 | 4 | 8 medium | 3 | FR 3, FR 5 | 2 | CSR-17, CSR-18 | 1 | 3 low |
| TS-17 | 3 | 2 | 6 medium | 2 | FR 6 | 1 | CSR-20 | 1 | 2 low |
| TS-18 | 4 | 2 | 8 medium | 2 | FR 1, FR 4 | 2 | CSR-06, CSR-24 | 1 | 2 low |
| TS-19 | 4 | 4 | 16 high | 3 | FR 1, FR 5 | 1 | CSR-01, CSR-02 | 1 | 3 low |
| TS-20 | 3 | 4 | 12 high | 3 | FR 1 | 2 | CSR-15 | 1 | 3 low |

![Figure 6-1: two four-by-four risk matrices side by side, likelihood up the side and impact along the bottom, cells shaded green for low, amber for medium and red for high. The left matrix, before treatment, has eleven scenarios in the red cells and nine in the amber cells. The right matrix, after the requirements with the safety architecture, has eighteen scenarios in green cells and two, TS-07 and TS-12, in amber cells](figures/fig-c07-6-1-risk-matrix.svg)

*Figure 6-1.* Where each scenario sits before treatment and after. Two things move it: the safety architecture
moves it left (lower impact), the requirements of WP-C-08 move it down (lower likelihood). Generated by
[`figures/fig_c07.py`](figures/fig_c07.py) from §6; CI recomputes every product and band and fails on a mismatch.

Reading the table:

- **Every high risk is a path from the network to the motors or the arms.** At BL-001 the network reaches the
  firmware directly, and the firmware is the only thing between a command and a motor (GAP-03). That is why the
  impact before treatment is severe almost everywhere.
- **The safety architecture is what makes a successful attack survivable.** With WP-S-03 the hardwired chain can
  stop the robot whatever the software does, and channel 2 bounds the speed channel 1 commands (SR-00.07), so an
  attacker who wins can still make the robot move, but within the limits the safety functions hold (impact 3).
- **TS-12 is the exception.** It attacks the safety device itself, so no safety function catches it; only
  keeping the configuration out of reach lowers it (CSR-16, CSR-17).
- **TS-04 drops to impact 2** because the collision monitor carries no safety claim (GAP-13): switching it off
  costs a layer of defence in depth, not a safety function.

## 7. Security level check

DQ-013 A set the security level target per foundational requirement: SL 2 for FR 1, 3, 5 and 7, SL 1 for FR 2, 4
and 6. Each scenario needs the level of its actor (§1.2) on the foundational requirements its treatment relies
on. Where a target is below what a scenario needs, the row is here with its disposition.

| TS | FR | SL-T | SL needed | Disposition |
|---|---|---|---|---|
| TS-01 | FR 2 | 1 | 2 | **Decision needed.** Network isolation and SROS2 authentication (FR 1, FR 5) keep the site network out; stopping an authenticated process on the robot from publishing motion it has no business publishing is authorisation of software processes, CR 2.1 RE(1), which sits at SL 2 of FR 2. Question to the lead (DQ-025) |
| TS-04 | FR 2 | 1 | 2 | Decision needed: who may call the lifecycle and parameter services of the navigation nodes (DQ-025) |
| TS-05 | FR 2 | 1 | 2 | Decision needed: who may send docking and undocking commands (DQ-025) |
| TS-06 | FR 2 | 1 | 2 | Covered: the operator UI serves human users only, and CR 2.1 at SL 1 enforces the operator and maintainer roles; the intentional attacker is stopped by the login at SL 2 of FR 1 (CSR-06) |
| TS-11 | FR 2 | 1 | 2 | Decision needed: a compromised service on the robot is an authenticated participant; only per-process authorisation contains it (DQ-025) |
| TS-13 | FR 3 | 2 | 3 | Outside the target: spoofing a LiDAR or a camera needs sophisticated means. Carried by the safety architecture: the protective stop SF-02 uses a safety-rated detection means independent of the navigation sensing (SR-02.06); the insufficiency of the navigation sensing is WP-C-10's |
| TS-14 | FR 2 | 1 | 2 | Decision needed: which process may command the arms and the lift (DQ-025) |
| TS-18 | FR 4 | 1 | 2 | Covered: no stream leaves the robot without the gateway login at SL 2 of FR 1 (CSR-06); FR 4 at SL 1 adds encryption in transit against casual capture (CSR-24) |

**Finding.** The target of DQ-013 A gave FR 2 SL 1 because the operator and maintainer are the only human roles.
The scenarios show that the use control that matters on this robot is between software processes, not people:
which node may command motion, docking, the arms and the lift. That is FR 2 at SL 2. Until the lead answers
DQ-025, WP-C-08 writes the requirement (CSR-03) so that it holds under either answer and marks which part
depends on it.

## 8. Treatment and residual risk

Treatment is the requirements CSR-01…CSR-24 of [WP-C-08 §4](WP-C-08-cybersecurity-requirements-and-sl-target.md#4-allocated-requirements).
After treatment, eighteen scenarios are low and two are medium:

| TS | Residual | Why it stays | What would lower it |
|---|---|---|---|
| TS-07 | 6 medium | Nobody can stop a person jamming the site Wi-Fi. With the requirements, a jammed link costs the on-screen stop request and the operator's view, never the stop: the hardwired emergency stops and the loss-of-command stop do not use the network (CSR-07, CSR-08) | a certified wireless emergency stop carried by whoever supervises the robot from a distance |
| TS-12 | 4 medium | A person with the device password and physical access can change a protective field; the safety architecture cannot catch an attack on itself | a start-up check that compares the safety device's configuration checksum with the recorded value and refuses to enable motion on a mismatch |

Both are a risk acceptance, which is the lead's to give (ZCR 7). The question is DQ-026.

## 9. Interface to the risk assessment

Each hazard the scenarios can cause, and the scenarios behind it. H-12 in WP-C-03 stands for all of them; the
dependency WP-C-03 §5 writes for H-12 (SF-03 at d, and SF-01) is the safety architecture of §6's middle column.

| Hazard | Threat scenarios |
|---|---|
| H-01 | TS-01, TS-04, TS-05, TS-06, TS-07, TS-08, TS-12, TS-13 |
| H-02 | TS-01, TS-02, TS-09, TS-16, TS-19 |
| H-03 | TS-03, TS-09 |
| H-04 | TS-03 |
| H-09 | TS-16 |
| H-10 | TS-07 |
| H-11 | TS-04, TS-08, TS-13 |
| H-12 | TS-01, TS-03, TS-04, TS-05, TS-06, TS-10, TS-11, TS-14, TS-19, TS-20 |
| H-13 | TS-14, TS-15 |
| H-15 | TS-14, TS-16 |

## 10. Assumptions and limitations

| ID | Assumption or limitation | Consequence |
|---|---|---|
| AS-01 | The site provides a Wi-Fi network with a site-specific key, not an open or guest network, for the robot and its operators (WP-C-08 §6) | TS-01, TS-06 and TS-19 assume it; without it the likelihood after treatment rises by one |
| AS-02 | The robot's chassis is closed and locked in operation, and only maintainers hold the key | TS-09, TS-12 and TS-16 assume it |
| AS-03 | No scenario is tested. The likelihoods come from the upstream record and the gap assessment | every value in §6 is a planning value until WP-V-06 |
| AS-04 | The upstream record does not say how the compute image sets up SSH, accounts or the firewall | TS-20 is rated as if defaults are in place |
| AS-05 | The CFG-002 interfaces (the Jetson to STM32 link, CAN-FD to the arms, the tablet) are known only by name | TS-14, TS-15 and TS-16 are re-assessed when the design is public |

## 11. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | DQ-025: FR 2 at SL 2 for per-process authorisation (TS-01, TS-04, TS-05, TS-11, TS-14) | Project lead | G1 |
| OI-2 | DQ-026: accept the residual of TS-07 and TS-12, or require the measures of §8 | Project lead | G1 |
| OI-3 | Re-assess TS-14, TS-15 and TS-16 when the CFG-002 interfaces are public (AS-05) | Cybersecurity manager | when public |
| OI-4 | Confirm every clause and security-level assignment against licensed copies of IEC 62443-3-2, -3-3, -4-1 and -4-2 | Cybersecurity manager | when DQ-016 allows |
| OI-5 | The interim cybersecurity review CS-I1 (external) is unscheduled while DQ-010 C holds; G1 cannot record it as performed | Project lead | G1 |
