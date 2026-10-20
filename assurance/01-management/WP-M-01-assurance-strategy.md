# WP-M-01 Assurance Strategy and Lifecycle Tailoring

| Field | Value |
|---|---|
| Work product | WP-M-01 Assurance strategy and lifecycle tailoring |
| Standard reference | ISO 12100:2010 §4 (strategy for risk assessment and risk reduction); ISO 13849-1:2023 §4 (overview, planning); IEC 61508-1:2010 §6 (management of functional safety, tailoring of the lifecycle); IEC 62443-4-1:2018 SM-1 (development process); ISO/IEC TR 5469:2024 (AI in safety functions, informative); UL 4600 (safety case structure, informative); Regulation (EU) 2023/1230 Art. 25 (conformity assessment procedures) |
| Version | 0.1 (initial strategy; 2026-10-20) |
| Status | Draft |
| PL / scope | All (machinery safety, SRP/CS, cybersecurity, ML, process) |
| Author | Assurance team (initial draft) |
| Reviewer(s) | TBD (I1); confirmation review of the tailoring rationale by an independent assessor (I3) |
| Approver | Project maintainer (acting safety manager). Self-approval is an accepted interim limitation until a second person takes the safety manager or reviewer role ([WP-M-02](WP-M-02-safety-plan.md) OI-2) |
| Baseline | `726046e` |

## 1. Purpose

This document is the assurance path for the OpenAMRobot fork. It sets out:

1. what the fork will claim, and for which configuration of the robot,
2. the safety architecture argument that makes those claims achievable on inherited hardware and software,
3. which standards apply to a mobile manipulator, how each one is used and where it is tailored, with rationale,
4. the phases, gates and work products that take the project from today's baseline to a release decision,
5. the strategic decisions the project must take, and the risks to the plan.

The [safety plan (WP-M-02)](WP-M-02-safety-plan.md), [cybersecurity plan (WP-M-08)](WP-M-08-cybersecurity-plan.md),
[ML safety plan (WP-M-09)](WP-M-09-ml-safety-plan.md) and [regulatory conformity strategy (WP-M-13)](WP-M-13-regulatory-conformity-strategy.md)
carry out this strategy for their own disciplines. The [work product register (WP-M-00)](WP-M-00-work-product-register.md)
lists every output. The standards are the machinery set, because a robot that drives itself around a workplace is
machinery under Regulation (EU) 2023/1230, not a road vehicle.

## 2. Starting point

From the [baseline gap assessment](../00-assessment/gap-assessment.md), at the commits in its header:

- The fork carries no changes yet. Every finding is a finding about upstream OpenAMRobot as inherited, and upstream
  states most of them itself (`docs/safety/00_safety_overview.md` §4, `KNOWN_LIMITATIONS.md`, the hardware "Known
  hardware limitations").
- **No safety function reaches any Performance Level.** The Gate A unit has no emergency stop in its documented
  wiring, no protective stop, no safe speed, no brakes, no battery fuse and no disconnect. The only stop is a 200 ms
  software watchdog that sets motor PWM to zero on the same core that generates it (GAP-01…GAP-05, GAP-19).
- **The architecture is the right shape.** A large ROS 2 stack sits in front of a small firmware layer on a
  separate microcontroller that is the last thing before the motors, and upstream intends the 2.0 stop chain to
  bypass that microcontroller in hardware (`ESTOP-SCOPE`, `TELEMETRY-NOT-SAFETY-EVIDENCE` in upstream's register).
- **The risk assessment does not exist.** The documentation site's risk-assessment page is an empty template; there
  is no hazard list, no safety function, no required PL, no stopping distance and no stated mass (GAP-23, GAP-30).
- **Process is ahead of product.** Upstream has a decision register with CI consistency scans, two-human approval on
  safety paths and an engineering quality standard, but no verification review, no independence and no firmware
  verification at all (GAP-11, GAP-31, GAP-34).
- **Anyone on the ROS 2 domain can move the robot.** No authentication, no command arbitration, no SROS2 (GAP-27).
- **OpenAMRobot 2.0 decides a real safety chain** (two certified E-stops, a Pilz PNOZ s3, two contactors, hub motors
  with brakes, a 110 A fuse and a lockable disconnect) but none of it is in a public repository (GAP-33, §8 of the
  gap assessment).

## 3. What the fork will claim

### 3.1 Reference configuration (the only scope claims apply to)

| Element | Reference configuration |
|---|---|
| Robot | Upstream's **Gate A unit**: v0.0.1 differential-drive base, Raspberry Pi 5, Teensy 4.0, ZD BLDC motors with ZBLD.C20-120L2R drivers, AS5040 encoders, MPU6500 IMU, RPLIDAR A1, two 12 V lead-acid batteries, **plus the bench safety hardware the fork adds before any test** (§4.1, [WP-V-07](../06-validation/WP-V-07-test-operations.md)). Recorded as `CFG-001` once the Living Safety Case records are ported |
| Function | Autonomous navigation (Nav2) and docking of the mobile base in a defined indoor operating area; teleoperation for test. No arm, no lift ([decision register](decisions/register.yaml) DQ-004) |
| Software | A tagged fork release that pins the three platform repositories, the linorobot2 firmware base, the ROS 2 Jazzy distribution and the container image by commit or digest |
| Operating environment | Defined in [WP-C-02](../02-concept/WP-C-02-operating-environment-and-tasks.md): indoor, level floor, defined zones, defined people presence |
| Operator | A trained test operator with a hand on the bench E-stop during development ([WP-V-07](../06-validation/WP-V-07-test-operations.md)). After release: personnel briefed per [WP-O-03](../09-production-operation/WP-O-03-information-for-use.md) |

The choice of the Gate A unit over the 2.0 design is decision DQ-002 (recommended A, open). The 2.0 safety-chain
decisions are tracked as claims to verify, never as evidence, until their drawings and code reach a repository.

Any other configuration, including the 2.0 base, the arms and the lift, needs an impact analysis ([WP-M-11](WP-M-11-impact-analysis.md))
and supporting evidence before it joins the claimed scope.

### 3.2 Top-level claim

> **G0**: The OpenAMRobot reference configuration (CFG-001), operated within its operating environment limits by
> personnel briefed as its information for use requires, does not expose people to unacceptable risk. The residual
> risk after the three-step method of ISO 12100 is acceptable for the machine's intended use and reasonably
> foreseeable misuse.

Sub-claims that structure the [safety case (WP-K-01)](../10-safety-case/WP-K-01-safety-case.md):

| Sub-claim | Standards | Core argument |
|---|---|---|
| G1 The hazards of the machine are identified and each is reduced by inherently safe design, safeguarding or information for use, in that order | ISO 12100, ISO 3691-4, ISO 10218-2 | The risk assessment (WP-C-03) is complete for the machine limits; every hazard has a risk reduction measure (WP-C-05) |
| G2 Every safety function achieves its required Performance Level | ISO 13849-1/-2, EN 60204-1, ISO 13850 | The safety functions (WP-C-04) are implemented by a hardwired safety chain whose category, MTTFD, DCavg and CCF are calculated (WP-H-04) and validated (WP-V-01…V-05), and the software layers above it cannot defeat it (WP-A-05) |
| G3 Performance limits of the sensing and navigation stack are known, bounded and covered by a safety function or an operating-environment limit | ISO 3691-4 §4, ISO 21448 (method) | The insufficiency analysis (WP-C-10) lists what the LiDAR and Nav2 chain cannot see or do; each limit is closed by SF-02, SF-03 or a limit in WP-C-02 |
| G4 Learned components carry no safety function and cannot defeat one | ISO/IEC TR 5469, AI Act | The learned policy and perception models are usage level "outside the safety function" (WP-C-09); their outputs pass through the same checker as every other command |
| G5 Cybersecurity risks to safety are treated | IEC 62443-4-1/-4-2 | The threat assessment (WP-C-07) covers the ROS 2 network, the operator UI and the update path; the safety chain is a zone with no network conduit (WP-S-07) |
| G6 The work was done by competent people under controlled processes with independent confirmation | IEC 61508-1 §6, §8; ASPICE | Plans, configuration management, change control, reviews and the confirmation measures of WP-M-06 |

**No claim is made, now or as a target, for operation of the arms or lift, for operation outside the defined
operating area, or for any configuration outside §3.1.**

## 4. The standards and how each one is used

OpenAMRobot is machinery. The method is one hazard log, one requirements database, generated figures and a Living
Safety Case; the standards that feed it are these.

| Question | Answered with | Where |
|---|---|---|
| What are the hazards and how much risk reduction does each need? | **ISO 12100** risk assessment (three-step method); **ISO 3691-4** list of significant hazards for AMRs; **ISO 10218-2** and **ISO/TS 15066** for the arms when they come; required **Performance Level** from the ISO 13849-1 Annex A risk graph | WP-C-01, C-03, C-04, C-05 |
| Which safety functions must the machine have? | **ISO 3691-4 §4**: emergency stop, protective stop on personnel detection, speed control, braking, stability; **ISO 13850** for the emergency stop; **EN 60204-1 §9** for stop categories | WP-C-04 |
| How good must the control system be, and how is that shown? | **ISO 13849-1** categories B to 4, MTTFD, DCavg, CCF, PL a to e; **ISO 13849-2** validation and fault lists; **IEC 62061 / IEC 61508** where 13849 runs out (software beyond 13849-1 §7, management, assessment) | WP-S-02…S-05, WP-H-01…H-07, WP-W-01…W-09, WP-V-01…V-05 |
| Is the electrical installation safe? | **EN 60204-1**: supply disconnecting device, overcurrent protection, protection against electric shock, control circuits, verification | WP-H-02, H-05 |
| Where may a person be relative to the robot? | **ISO 13855** approach speeds and safety distances; **IEC 61496** for electro-sensitive protective equipment; **ISO/TS 15066** power and force limits for the arms | WP-C-06, S-04, V-03 |
| What if nothing fails but the sensors do not see? | No machinery standard covers performance limits of perception. **ISO 21448 is used as an informative method** (triggering conditions, known and unknown scenarios) inside WP-C-10 and WP-V-08; the resulting limits become operating-environment limits or safety functions | WP-C-10, V-08 |
| What if someone attacks it? | **IEC 62443-4-1** (secure development lifecycle) and **62443-4-2** (component requirements, security level target); 62443-3-2 for the zone and conduit model | WP-M-08, C-07, C-08, S-07, W-11, V-06, O-05 |
| How far can a learned component be trusted? | **ISO/IEC TR 5469**: AI technology class and usage level; the fork's position is that no learned component implements a safety function. **AI Act** Annex I lists the Machinery Regulation, so a learned safety component would be a high-risk AI system | WP-M-09, C-09, W-10, K-07 |
| Is the whole argument convincing? | **UL 4600** principles for the safety case; the Living Safety Case records and generators | WP-K-01, `case/` |
| What does the law require? | **Regulation (EU) 2023/1230** (Machinery Regulation, applies from 20 January 2027): essential health and safety requirements (Annex III), technical documentation (Annex IV), conformity assessment (Art. 25, Annexes VI–X) with third-party assessment mandatory for machinery with self-evolving safety behaviour (Annex I Part A); **Regulation (EU) 2024/1689** (AI Act) for a learned safety component | WP-M-13, K-02, K-06, K-07 |
| Are the processes capable? | **ASPICE 4.0** kept as the process capability frame (self-assessment), because the gap assessment already rates upstream against it and no machinery-specific process model exists | WP-M-12 |

How each standard is cited: work products are structured after these standards and cite their clauses. **No
compliance is claimed**, because no assessment has been performed and the drafting environment has no licensed copy
of any standard (WP-M-06 OI-1). The wiki page [How we use each standard](../../wiki/How-we-use-each-standard.md)
is the plain-language version of this table.

## 5. Tailoring

The machinery standards assume a manufacturer placing a finished machine on the market. The fork is an open-source
assurance record for research hardware built by someone else. The table records each tailoring decision. Each one
needs confirmation review by an independent assessor.

| # | Topic | Decision | Rationale |
|---|---|---|---|
| T-01 | Lifecycle entry | Treat the fork as a **modification of existing machinery**: impact analysis ([WP-M-11](WP-M-11-impact-analysis.md)), then a full concept phase. Nothing is reused from upstream as a safety work product, because none exists | Upstream has no risk assessment, safety functions or validation; the "deliberate and tracked" gaps are strengths of process, not evidence |
| T-02 | Machine boundary | The machine is the mobile base as delivered plus the safety hardware the fork adds. The docking station, the Wi-Fi network and the operator's computer are outside the machine, with interface assumptions | The fork controls the robot; it does not control the site network or the operator's laptop |
| T-03 | Safety function allocation | **The stops and interlocks that remove actuator power (SF-01, SF-02, SF-05, SF-10, SF-12) are implemented by a hardwired safety chain alone** (E-stops, safety relay, contactors, brakes, safety scanner OSSDs, pose signals). **The speed and loss-of-control functions (SF-03, SF-04, SF-06, SF-09) are two-channel functions whose channel 1 is the base-controller firmware and whose channel 2 is the hardwired monitor** (WP-S-03 §3.5); the firmware carries a PL claim at their PLr and the ISO 13849-1 §7 lifecycle. The ROS 2 stack stays a functional layer with no PL claim. Decided by the lead 2026-10-20 (DQ-014, option B) | Matches upstream's own principle (`TELEMETRY-NOT-SAFETY-EVIDENCE`); keeps the PL d argument inside components with certificates and known reliability data; avoids a PL d software lifecycle on 2,765 lines of untested Python |
| T-04 | Firmware as safety-related embedded software | The firmware hardening (watchdog, `/cmd_vel` validation, plausibility checks, debug paths removed) is the first increment of channel 1 of T-03 and is **claimed** once its evidence exists: reproducible build, coding rules, static analysis, unit and integration tests with coverage, a software safety analysis and independent review (WP-W-01…WP-W-08 at PL d). Until then the chain alone carries the claim and the firmware is defence in depth | The hardening is cheap and reduces demand on the chain; a later decision can promote the firmware to part of the SRP/CS once it has a verification history |
| T-05 | Hardware | Safety components are bought with certificates (safety relay, contactors with mirror contacts, type 3 scanner, brakes) and qualified under ISO 13849-1 as well-tried or certified components; the remaining hardware (drivers, motors, encoders) is treated as not safety-related | No supplier evidence exists for the inherited drivers or motors; the chain removes power upstream of them |
| T-06 | Proven in use | **Not claimed** for any element. Upstream's run history is supporting evidence only ([WP-P-09](../07-supporting/WP-P-09-proven-in-use.md)) | No controlled configuration or field-problem history that would meet IEC 61508 |
| T-07 | Production | Tailored to assembly, commissioning and configuration control of a kit ([WP-O-01](../09-production-operation/WP-O-01-assembly-installation-commissioning.md)). The fork manufactures nothing | The robot is built by whoever follows the instructions; the instructions and the commissioning checks are the product |
| T-08 | Upstream | Botshare is treated as an upstream supplier with no development interface agreement; the supplier-side activities fall to the fork ([WP-M-10](WP-M-10-upstream-and-supplier-management.md)). Upstream's `decisions.yaml` is quoted, never restated | Upstream is under no contract |
| T-09 | Independence | Verification reviews may be done by project members (I0/I1), never by the author. With one maintainer, I1 review needs an external reviewer and self-review is recorded as I0. Confirmation reviews of the risk assessment, the safety plan and the safety case, and the functional safety assessment, need an **external** assessor (I2/I3) ([WP-M-06](WP-M-06-confirmation-measures-plan.md)) | One maintainer today |
| T-10 | Performance limits of perception | ISO 21448 is used as a method, not a standard to comply with, inside WP-C-10 and WP-V-08 | No machinery standard covers it and the gap assessment's worst findings (GAP-14, GAP-22, GAP-35) are performance limits, not faults |
| T-11 | Cybersecurity scope | IEC 62443-4-1 practices are applied to the three platform repositories; IEC 62443-4-2 component requirements to the robot as one component with a security level target decided by the lead (DQ-013). The site network is an external zone | The fork controls the robot's software and configuration, not the network it is deployed on |
| T-12 | Process capability | ASPICE 4.0 is used for a self-assessment of process capability ([WP-M-12](WP-M-12-process-capability-baseline.md)), target CL2 for management, support, system and software processes, CL1 for hardware and ML. No ASPICE assessment is claimed | Continues the gap assessment's GAP-34 rating; gives the fork a process model the robotics standards lack |
| T-13 | Regulatory | EU frame recommended (DQ-003): Machinery Regulation and the harmonised route through ISO 3691-4 and ISO 13849-1. The conformity module is decision DQ-009. The AI Act applies only if a learned component becomes a safety component, which T-03 avoids | Where the robot is made and sold; one technical file |
| T-14 | Arms and lift | **In the item** on CFG-002, the 2.0 mobile manipulator, which is the hardware reference beside the Gate A unit as the software and firmware reference (DQ-004 B and DQ-020 A, 2026-10-20). The arms are an industrial robot system under ISO 10218-2 with collaborative operation per ISO/TS 15066 only where WP-C-06 §4 proves it (DQ-021); the lift carries loads, never persons. Every CFG-002 value is quoted from upstream's plan set and unverified until its design is public | No arm or lift code is public; the base case must not have to be rewritten when they arrive |

## 6. Safety architecture argument (the central strategy)

### 6.1 Doer, checker, and a checker of last resort

```
 ┌──────────────── mobile base ──────────────────────────────────────────────────────────┐
 │  Raspberry Pi 5 (ROS 2 Jazzy)            Teensy 4.0 (firmware)        Hardwired safety │
 │  ┌──────────────────────────────┐        ┌─────────────────────┐      chain (SRP/CS)   │
 │  │ Nav2 → smoother → collision  │ USB    │ /cmd_vel validation │     ┌──────────────┐  │
 │  │ monitor → twist_mux          │───────▶│ watchdog, clamps,   │────▶│ E-stop (x2)  │  │
 │  │ docking, teleop, operator UI │ serial │ plausibility, PWM   │ PWM │ safety relay │──┼─▶ contactors
 │  │ (learned policy, later)      │◀───────│ fault inputs, brake │     │ scanner OSSD │  │   motor drivers
 │  └──────────────────────────────┘        │ output              │     │ brakes       │  │   brakes
 │        FUNCTIONAL (no PL claim)          └─────────────────────┘     └──────────────┘  │
 │                                             FUNCTIONAL, hardened          PL d target   │
 └────────────────────────────────────────────────────────────────────────────────────────┘
          Operator: hand on the bench E-stop during development (WP-V-07)
          Environment: defined operating area and people presence (WP-C-02)
```

- **Doer:** the ROS 2 stack. It decides where to go and how fast. Everything it publishes is a request. It is
  functional software: upstream calls its envelope "best-effort" and the fork agrees (GAP-13). It is hardened
  (command arbitration, bounded parameters, docking inside the envelope) so that the chain is rarely demanded, but
  no safety function is allocated to it.
- **Checker (functional):** the Teensy firmware. The last software before the motors. Hardened per T-04 so that a
  stale, out-of-range or absent command stops the motors, but on its own it is Category B at best (no monitoring,
  one channel, GAP-03) and carries no PL claim in the first safety case.
- **Checker of last resort (SRP/CS):** the hardwired safety chain. Two-channel E-stops and the safety scanner's
  OSSDs feed a safety relay whose outputs drop two contactors in the actuator supply and engage the brakes. Nothing
  in software can hold a contactor closed. This is where the PL d argument is made, with certified components and
  calculated MTTFD, DCavg and CCF.

### 6.2 Consequences that shape the plan

1. **The hardware does not exist yet.** The Gate A unit has no chain at all. The first engineering act of the fork
   is bench safety hardware (fuse, disconnect, dual-channel E-stop through a safety relay, driver fault read-back)
   before any further on-ground test ([WP-V-07](../06-validation/WP-V-07-test-operations.md), gap assessment §10 action 4, decision DQ-011).
2. **Personnel detection decides the operating environment.** Without a safety-rated scanner or bumpers, nothing
   below the LiDAR plane is seen and no protective stop exists (GAP-14, GAP-22). Either the fork fits a type 3
   scanner, or the operating area excludes people (DQ-005, DQ-007). Until decided, no operation around people is
   inside the case.
3. **Stopping distance is the number everything hangs on.** Protective field dimensions (ISO 13855), the speed
   limit and the stop category all derive from a measured stopping distance that nobody has measured (GAP-02,
   GAP-23). [WP-S-04](../03-system/WP-S-04-response-time-and-stopping-budget.md) owns the budget; [WP-V-02](../06-validation/WP-V-02-stopping-braking-stability-tests.md) measures it.
4. **Independence of the chain from the stack is the hinge.** The chain shares power, the chassis and the operator
   with the stack. Shared power (GAP-21), the parameter injection topics (GAP-07), the lifecycle services (GAP-27)
   and the docking sequencer's habit of switching protection off (GAP-15) are each analysed in [WP-A-05](../08-analyses/WP-A-05-independence-of-the-safety-chain.md).
5. **Software verification starts from nothing.** The firmware has no build in CI, no tests and no static analysis;
   the docking sequencer has no tests (GAP-11, GAP-39). The software work products begin with the environment
   ([WP-W-01](../05-software/WP-W-01-software-development-environment-guidelines.md)) and a pinned, reproducible build.
6. **The 2.0 design is a plan, not a fact.** Every 2.0 safety-chain decision in upstream's register is recorded as a
   claim to verify with a defeater "not in any repository" until its drawings arrive (GAP-33).

## 7. Phases, gates and sequence

The lifecycle has seven phases, each closed by a gate; gate names and exit criteria are in
[WP-M-00 §2](WP-M-00-work-product-register.md#2-gates), the activities per phase in [WP-M-02 §4](WP-M-02-safety-plan.md#4-lifecycle-activities-per-phase),
and the integrated maps in the [process model (WP-P-11)](../process/README.md).

| Phase | Gate | What it settles | Hold points |
|---|---|---|---|
| P0 Governance | G0 | Plans, roles, configuration control, the frame (DQ-002, DQ-003), the conformity route (DQ-009) | None; the fork drives nothing |
| P1 Concept | G1 | Machine limits, risk assessment, safety functions with PLr, risk reduction concept, detection concept, cybersecurity and ML concepts, test operations | **Hold point:** no on-ground test without the bench safety hardware and WP-V-07 approved |
| P2 System design | G2 | SRS, chain architecture and category, response-time and stopping budget, I/O map, mechanical and stability analysis, system analyses | |
| P3 HW/SW development | G3 | Chain hardware and PL calculation, firmware hardening, software verification, qualification of components and tools | |
| P4 Integration and verification | G4 | Integration, PL verification, stopping, detection and E-stop tests, fault injection | **Hold point:** no operation with people in the area before WP-V-03 passes |
| P5 Validation and release | G5 | Validation on the robot, cybersecurity validation, safety case, assessment, technical file, release record | |
| P6 Operation | G6 | Field monitoring, incident response, updates | |

## 8. Strategic decisions required

Each decision is asked of the project lead through the [decision register](decisions/README.md); this table is the
index, the register entry is the question.

| # | Decision | Register | Status |
|---|---|---|---|
| D-01 | Fork rather than contribute upstream | DQ-001 | Answered: fork (2026-10-20) |
| D-02 | Reference configuration: Gate A unit now, 2.0 tracked | DQ-002 | Applied: A (2026-10-20); DQ-020 asks whether 2.0 joins it after D-04 and D-09 |
| D-03 | Regulatory frame: EU machinery | DQ-003 | Applied: A, EU frame (2026-10-20) |
| D-04 | First machine: base only | DQ-004 | Applied: B, the base with the arms and lift on CFG-002 (2026-10-20; T-14) |
| D-05 | Required PL for the stop functions: PL d, people share the space | DQ-005 | Applied: A (2026-10-20) |
| D-06 | Conformity assessment route and module | DQ-009 | Applied: A, Module A (2026-10-20) |
| D-07 | Independent assessor: when | DQ-010 | Applied: C, not for now; every I2 and I3 measure unscheduled (2026-10-20) |
| D-08 | Personnel detection means: scanner, bumpers or separated area | DQ-007 | Applied: A, scanner plus rear bumper (2026-10-20) |
| D-09 | Bench safety hardware for the Gate A unit before further tests | DQ-011 | Applied: C, no on-ground tests until the 2.0 base with its chain exists; the Gate A unit is bench only (2026-10-20) |
| D-10 | Roles and self-approval while the project has one person | DQ-012 | Applied: A, self-approval as a recorded interim limitation (2026-10-20) |
| D-11 | Cybersecurity security level target | DQ-013 | Open, batch 2 |
| D-12 | Safety function allocation: hardwired chain only, or firmware inside the SRP/CS | DQ-014 | Applied: B, firmware as channel 1 of the speed and loss-of-control functions (2026-10-20; T-03, T-04, WP-S-03 §3.5) |
| D-13 | Stop category for the emergency stop | DQ-015 | Open, batch 2 |
| D-14 | Buying the standards | DQ-016 | Applied: C, not until an assessor is engaged (2026-10-20) |

## 9. Top risks to the assurance path

Project risks are managed in [WP-M-07](WP-M-07-risk-management.md). The ones that shape this strategy:

| Risk | Effect | Response |
|---|---|---|
| The lead cannot fund a safety scanner, a safety relay and brakes | No protective stop; the operating environment must exclude people and the case shrinks to a test cell | DQ-005 option B is a defensible fallback; the chain is still needed for the E-stop |
| One person holds every role | No I1 review, no confirmation measure, self-approval everywhere | T-09; DQ-010, DQ-012; verification reviews by any second contributor count |
| Upstream 2.0 lands and moves the hardware under the assessment | Hardware findings on Gate A overtaken; re-statement of WP-C-01, WP-H-* | DQ-002 option A accepts this; the ROS 2 and firmware findings carry over |
| The standards are not available to the authors | Clause numbers wrong; tailoring argued against memory | DQ-016; every clause reference marked to check; WP-M-06 OI-1 |
| The Machinery Regulation's AI provisions pull a learned component into Annex I Part A | Mandatory third-party conformity assessment and an AI Act file | T-03 keeps learned components outside every safety function; WP-M-13 tracks the threshold |

## 10. Open items

| ID | Item | Owner | Gate |
|---|---|---|---|
| OI-1 | Record CFG-001 as a configuration record once the Living Safety Case records exist | Safety manager | G1 |
| OI-2 | Replace the text diagram of §6.1 with a generated figure pinned to §6.1 and §6.2 so CI detects when it may be stale | Safety manager | G1 |
| OI-3 | Confirm the tailoring table with the assessor once engaged (DQ-010) | Safety manager | G1 |
| OI-4 | ~~Rewrite T-03, T-04 and T-14~~ done 2026-10-20 after DQ-020 A. Remaining: widen the software work products WP-W-01…WP-W-08 to the ISO 13849-1 §7 lifecycle at PL d for the firmware channel (WP-S-03 OI-6) | Safety manager | G2 |
| OI-4 | Obtain upstream's plan-set documents P-03, E-01 and B-02 or record their content as the fork's own design (GAP-33) | Project maintainer | G1 |
