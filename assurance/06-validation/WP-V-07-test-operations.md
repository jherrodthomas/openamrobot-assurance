# WP-V-07 Test Operations and Safety Procedures for On-Ground Testing

| Field | Value |
|---|---|
| Work product | WP-V-07 Test operations and safety procedures for on-ground testing (hold point) |
| Standard reference | ISO 12100:2010 §6.4 (information for use, including for the development phase), §6.3 (safeguarding and complementary protective measures); ISO 3691-4:2023 §6 (information for use, operating areas); ISO 13850:2015 §4 (emergency stop function, as bench equipment); EN 60204-1:2018 §5.3 (supply disconnecting device), §7.2 (overcurrent protection); ASPICE 4.0 VAL.1 |
| Version | 0.1 (initial procedure; 2026-10-20) |
| Status | Draft |
| PL / scope | Development testing only. No PL is claimed for the bench equipment |
| Author | Assurance team (initial draft) |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

## 1. Purpose

This procedure is the **hold point** of [WP-M-01 §7](../01-management/WP-M-01-assurance-strategy.md#7-phases-gates-and-sequence):
no OpenAMRobot unit is driven under the fork's control until the conditions below hold. It exists because the Gate A
unit as inherited has no emergency stop, no brake, no battery fuse and no disconnect, and its only stop is a software
watchdog on the same core that drives the motors ([gap assessment](../00-assessment/gap-assessment.md) GAP-01…GAP-05,
GAP-19). The procedure makes the next months of testing defensible without claiming any Performance Level: it relies
on bench equipment and on the operator, and says so.

It applies to every on-ground test, from the first stopping-distance measurement to the validation runs of
[WP-V-01](WP-V-01-safety-validation.md). Bench tests with the wheels off the ground are outside it.

## 2. Conditions before any on-ground test

| # | Condition | Evidence | Closes |
|---|---|---|---|
| C-1 | A battery fuse sized for the drive current and a lockable battery disconnect are fitted in the 24 V supply | Photo and part numbers in the change record under [`07-supporting/impact/`](../07-supporting/impact/README.md) | GAP-19 (bench) |
| C-2 | A dual-channel emergency stop (two NC contacts, mushroom button, latching) through a safety relay drops the motor driver supply (or opens both drivers' `BRK/DI5` brake inputs **and** the supply). The button is on a tethered or wireless pendant in the operator's hand, not on the robot | Wiring sketch in the change record; a functional test before every session (§4) | GAP-01, GAP-02 (bench) |
| C-3 | Both motor drivers' `ERR/DO1` fault outputs are read by the firmware and a fault on either driver stops both motors | Firmware change record and a bench test with a forced fault | GAP-04 (bench) |
| C-4 | The battery and mains are never connected at the same time during a drive (source selector or procedure) | Procedure step in §4 | GAP-20 (bench) |
| C-5 | The firmware build is reproducible from the fork repository, with the watchdog enabled and `ENABLE_POWERED_DEBUG` off; its version is published on a topic and read before the test | Build manifest; `ros2 topic echo` log | GAP-03, GAP-08, GAP-10 (bench) |
| C-6 | A command arbiter (twist_mux) exists with a stop input at highest priority, and the docking sequencer cannot deactivate the collision monitor | Change record; launch file | GAP-15, GAP-36 (bench) |
| C-7 | The test area is defined, level, free of steps and drops, and marked; no person other than the operator and one observer is inside it during a drive | Area sketch in the test log | Operating-environment limit pending WP-C-02 |
| C-8 | The operator has read this procedure and run the pre-session checks of §4 | Signed line in the test log | WP-M-04 competence |

Conditions C-1 to C-3 are the bench safety hardware of [WP-M-02 §4.1](../01-management/WP-M-02-safety-plan.md#41-early-implementation-of-at-risk-work);
buying it was decision DQ-011: the lead decided on 2026-10-20 (option C) that there are no on-ground tests until
the 2.0 base with its safety chain exists. The hold point is therefore not expected to open on the Gate A unit;
C-1 to C-3 stay as the conditions for whichever base is first driven under the fork, and every Gate A activity is
bench work with the wheels off the ground (WP-C-02 T-08, AOU-03).

## 3. Limits during development testing

| Limit | Value | Source |
|---|---|---|
| Maximum commanded speed | 0.20 m/s forward, 0.05 m/s reverse (the Nav2 limits as committed), 0.5 rad/s | `nav2_params.yaml` as assessed; tightened, never relaxed, until WP-S-04 sets a budget |
| Reverse motion | Only with the observer watching the rear; the rear sector is masked from the scan (GAP-35) | gap assessment §4.1 |
| Docking and undocking | Not run with any person in the docking lane; the lane is marked | GAP-15, GAP-35 |
| Battery | Pack voltage measured before each session; no drive below 23.0 V at rest | GAP-17 |
| Payload | None until the robot has been weighed and WP-H-08 sets a payload | GAP-23 |
| People | Nobody inside the area except the operator (hand on the E-stop) and one observer, both outside the robot's path | No protective stop exists (GAP-14, GAP-22) |

## 4. Pre-session and per-session checks

1. Measure and log the battery pack voltage; confirm mains is disconnected.
2. Press and release the pendant E-stop with the robot powered and wheels free: the drivers must lose supply (or
   brake) and not restart until the reset is pressed. Log the result.
3. Read the firmware version topic and compare with the planned build. Log it.
4. Walk the area; confirm markings and the absence of other people.
5. Drive 1 m forward at 0.1 m/s and press the E-stop; confirm the stop and note the distance.
6. Only then start the planned test.

A failed check ends the session.

## 5. Test log

Every session has a log entry in [`06-validation/test-sites/`](test-sites/README.md): date, operator, observer,
build, battery voltage, pre-session check results, the tests run with their references (WP-V-02, V-03, V-04, V-05,
V-01), anomalies, and the E-stop presses with their reasons.

## 6. Anomalies

Any unexpected motion, any failure of a pre-session check, any contact with a person or object, and any E-stop press
that was not planned is a safety anomaly ([WP-M-02 §9](../01-management/WP-M-02-safety-plan.md#9-safety-anomaly-handling)).
Testing stops; the anomaly is raised as an issue labelled `safety-anomaly`; the safety manager lifts the stop in
writing after the cause is understood.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | ~~Buy and fit the bench safety hardware (DQ-011)~~ decided 2026-10-20 (option C): no on-ground test until the 2.0 base with its chain exists; the first on-ground test moves to that base | closed | — |
| OI-2 | Name and train the test operator(s) (WP-M-02 §3.1) | PM | Before the first on-ground test |
| OI-3 | Replace the §3 speed limits with the budget of WP-S-04 once the stopping distance is measured (WP-V-02) | SRP | G2 |
| OI-4 | Define the test area in WP-C-02 and reference it here | SM | G1 |
