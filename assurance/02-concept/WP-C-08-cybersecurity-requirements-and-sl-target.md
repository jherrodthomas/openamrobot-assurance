# WP-C-08 Cybersecurity requirements and security level target

| Field | Value |
|---|---|
| Work product | WP-C-08 Cybersecurity requirements and security level target |
| Standard reference | IEC 62443: 62443-4-1 SR-3…SR-5 (security requirements); 62443-4-2 §5…§11 (component requirements CR 1…CR 7 and their enhancements), SL-T; 62443-3-2 ZCR 6; ASPICE: SEC.1 |
| Version | 0.1 (2026-10-23): first content. §2 the target of DQ-013 A kept, the FR 4 rationale corrected (camera images of people are personal data), the FR 2 finding of WP-C-07 §7 recorded (DQ-025); §3 the component requirements that apply at the target, each mapped to a requirement; §4 requirements CSR-01…CSR-24 with element, configuration, the threat scenarios they treat, the safety functions they support and their verification (Figure 4-1); §5 the interface to the safety functions; §6 requirements on the site; §7 the security requirements of WP-S-02 §15. 0.0: skeleton with the SL-T table |
| Status | Draft |
| PL / scope | Both configurations: CFG-001, the Gate A unit (bench only, DQ-011 C); CFG-002, the 2.0 mobile manipulator (unverified, WP-C-01 §1.2) |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD: interim cybersecurity review CS-I1, external (WP-M-06 §7; unscheduled while DQ-010 C holds) |
| Approver | Cybersecurity manager (WP-M-08 §5) |
| Baseline | BL-001 |

> [!WARNING]
> Draft. No requirement here is implemented on any build. The component requirements of IEC 62443-4-2, their
> enhancements and the security level each belongs to are cited from memory and are to be checked against a
> licensed copy (DQ-016, answered C). Values marked **(TBC)** are planning values. Everything about CFG-002 rests on
> upstream's plan set.

## 1. Purpose

The cybersecurity requirements for the robot as one IEC 62443-4-2 component: the security level target per
foundational requirement, the component requirements that follow from it, and the requirements CSR-nn allocated
to the compute, the firmware, the operator gateway, the safety chain's devices and the build. Each requirement
treats threat scenarios of [WP-C-07](WP-C-07-cybersecurity-threat-and-risk-assessment.md) and, where it protects a
safety function, names it. [WP-S-07](../03-system/WP-S-07-cybersecurity-architecture.md) designs them,
[WP-W-11](../05-software/WP-W-11-cybersecurity-implementation-verification.md) implements and tests them, and
[WP-V-06](../06-validation/WP-V-06-cybersecurity-validation.md) tries to break them.

## 2. Security level target

Decided by the lead on 2026-10-20 (DQ-013 A). The realistic threat is a person on the same Wi-Fi with public
tools, so the foundational requirements that stop such a person moving the robot or changing what it does get
SL 2; the rest get SL 1. The safety chain is designed to need neither: no attack on the software can hold a
contactor closed (WP-S-03 §1). Rationale per threat scenario in WP-C-07.

| FR | Foundational requirement | SL-T | Why |
|---|---|---|---|
| FR 1 | Identification and authentication control | **2** | Who may publish `/cmd_vel`, call lifecycle services or log into the operator UI |
| FR 2 | Use control | 1 | Roles are operator and maintainer only; per-process authorisation is the open question DQ-025 (WP-C-07 §7) |
| FR 3 | System integrity | **2** | Signed images, protected safety parameters, a reproducible firmware build |
| FR 4 | Data confidentiality | 1 | No secrets on the robot; camera images of people are personal data, protected through the gateway login of FR 1 (WP-C-07 TS-18) |
| FR 5 | Restricted data flow | **2** | Zones and conduits: the safety chain has no conduit from the ROS 2 network |
| FR 6 | Timely response to events | 1 | Logging and the field-monitoring route of WP-O-04 |
| FR 7 | Resource availability | **2** | The stop path does not depend on the network; denial of service must not block a stop |

**FR 2 is open.** WP-C-07 §7 finds five scenarios (TS-01, TS-04, TS-05, TS-11, TS-14) whose treatment needs
authorisation between software processes, not only between people: which node may command motion, docking, the
arms and the lift. That is FR 2 at SL 2 (CR 2.1 RE(1)). The lead decided the target, so raising it is the lead's
call (DQ-025). CSR-03 below is written to hold under either answer and says which part depends on it.

## 3. Component requirements at the target

The requirements of IEC 62443-4-2 for each foundational requirement, the lowest security level at which each
applies, and whether it applies at the target of §2. A row that applies names the requirements of §4 that meet it.
Where 62443-4-2 has a separate embedded-device or host-device variant (EDR, HDR), the row stands for the variant
that fits the element.

| CR | Requirement | SL | Applies | Met by |
|---|---|---|---|---|
| CR 1.1 | Human user identification and authentication | 1 | yes | CSR-06, CSR-15 |
| CR 1.1 RE(1) | Unique identification and authentication | 2 | yes | CSR-06, CSR-15 |
| CR 1.2 | Software process and device identification and authentication | 2 | yes | CSR-02 |
| CR 1.3 | Account management | 1 | yes | CSR-06, CSR-15 |
| CR 1.4 | Identifier management | 1 | yes | CSR-06, CSR-15 |
| CR 1.5 | Authenticator management | 1 | yes | CSR-02, CSR-06, CSR-15, CSR-16 |
| CR 1.7 | Strength of password-based authentication | 1 | yes | CSR-06 |
| CR 1.8 | Public key infrastructure certificates | 2 | yes | CSR-02 |
| CR 1.9 | Strength of public key-based authentication | 2 | yes | CSR-02, CSR-15 |
| CR 1.10 | Authenticator feedback | 1 | yes | CSR-06 |
| CR 1.11 | Unsuccessful login attempts | 1 | yes | CSR-06, CSR-15 |
| CR 1.12 | System use notification | 1 | yes | CSR-06 |
| CR 1.14 | Strength of symmetric key-based authentication | 2 | no: not used, every authentication here is by password or public key | — |
| CR 2.1 | Authorisation enforcement | 1 | yes | CSR-03, CSR-04, CSR-06, CSR-14, CSR-18 |
| CR 2.1 RE(1) | Authorisation enforcement for all users: humans, software processes and devices | 2 | pending DQ-025 | CSR-03 |
| CR 2.1 RE(2) | Permission mapping to roles | 2 | pending DQ-025 | CSR-06 |
| CR 2.2 | Wireless use control | 1 | yes | CSR-23 |
| CR 2.5 | Session lock | 1 | yes | CSR-06 |
| CR 2.6 | Remote session termination | 2 | no: above the FR 2 target | — |
| CR 2.8 | Auditable events | 1 | yes | CSR-20 |
| CR 2.9 | Audit storage capacity | 1 | yes | CSR-20 |
| CR 2.10 | Response to audit processing failures | 1 | yes | CSR-20 |
| CR 2.11 | Timestamps | 1 | yes | CSR-20 |
| CR 2.12 | Non-repudiation | 3 | no: above the FR 2 target | — |
| CR 2.13 | Use of physical diagnostic and test interfaces | 2 | no: above the FR 2 target; the interfaces are removed or enclosed anyway | CSR-09, CSR-17 |
| CR 3.1 | Communication integrity | 1 | yes | CSR-02, CSR-06 |
| CR 3.2 | Protection from malicious code | 1 | yes | CSR-12, CSR-14 |
| CR 3.3 | Security functionality verification | 1 | yes | CSR-11, CSR-12 |
| CR 3.4 | Software and information integrity | 1 | yes | CSR-10, CSR-11, CSR-12, CSR-13, CSR-19 |
| CR 3.4 RE(1) | Authenticity of software and information | 2 | yes | CSR-11, CSR-12, CSR-19 |
| CR 3.5 | Input validation | 1 | yes | CSR-04, CSR-05 |
| CR 3.6 | Deterministic output | 1 | yes | CSR-05, CSR-08 |
| CR 3.7 | Error handling | 1 | yes | CSR-05, CSR-06 |
| CR 3.8 | Session integrity | 2 | yes | CSR-02, CSR-06 |
| CR 3.9 | Protection of audit information | 2 | yes | CSR-20 |
| CR 3.10 | Support for updates | 1 | yes | CSR-11, CSR-12, CSR-22 |
| CR 3.11 | Physical tamper resistance and detection | 2 | yes | CSR-16, CSR-17 |
| CR 3.12 | Provisioning product supplier roots of trust | 2 | yes | CSR-11, CSR-12 |
| CR 3.13 | Provisioning asset owner roots of trust | 2 | yes | CSR-02 |
| CR 3.14 | Integrity of the boot process | 1 | yes | CSR-11, CSR-12 |
| CR 3.14 RE(1) | Authenticity of the boot process | 2 | yes | CSR-11, CSR-12 |
| CR 4.1 | Information confidentiality | 1 | yes | CSR-06, CSR-24 |
| CR 4.2 | Information persistence | 2 | no: above the FR 4 target | — |
| CR 4.3 | Use of cryptography | 1 | yes | CSR-02, CSR-06, CSR-24 |
| CR 5.1 | Network segmentation | 1 | yes | CSR-01, CSR-08, CSR-14, CSR-18 |
| CR 6.1 | Audit log accessibility | 1 | yes | CSR-20 |
| CR 6.2 | Continuous monitoring | 2 | no: above the FR 6 target | — |
| CR 7.1 | Denial of service protection | 1 | yes | CSR-07, CSR-08, CSR-21 |
| CR 7.1 RE(1) | Manage communication load | 2 | yes | CSR-21 |
| CR 7.2 | Resource management | 1 | yes | CSR-14, CSR-21 |
| CR 7.3 | Control system backup | 1 | yes | CSR-22 |
| CR 7.4 | Control system recovery and reconstitution | 1 | yes | CSR-22 |
| CR 7.6 | Network and security configuration settings | 1 | yes | CSR-01, CSR-10, CSR-16 |
| CR 7.7 | Least functionality | 1 | yes | CSR-09, CSR-14 |
| CR 7.8 | Control system component inventory | 2 | yes | CSR-11, CSR-12, CSR-13 |

## 4. Allocated requirements

Verification: **I** inspection of the design or the build, **T** test in WP-W-11 (62443-4-1 SVV-1…SVV-3), **P**
penetration test in WP-V-06 (SVV-4). "Supports" names the safety function, or the requirement of
[WP-S-02](../03-system/WP-S-02-safety-requirements.md), that relies on the requirement; "none" means no safety
function relies on it.

| ID | Requirement | CR | Element | Config | Treats | Supports | Verif. |
|---|---|---|---|---|---|---|---|
| CSR-01 | **Robot graph off the site network.** The ROS 2 graph shall not be reachable from the site network: discovery limited to the robot (localhost or a robot-internal interface), a domain ID unique to the robot, no DDS traffic on the site interface. The operator gateway (CSR-06) and maintainer SSH (CSR-15) are the only services on that interface | CR 5.1, CR 7.6 | E-04; E-13 | both | TS-01, TS-04, TS-05, TS-08, TS-19 | SF-03, SF-04, SF-09 (channel 1); SR-90.01 | I, T, P |
| CSR-02 | **SROS2 on every node.** Every node of the robot graph shall run in an SROS2 enclave with authentication, access control and encryption enforced; a participant without a certificate from the robot's own certificate authority shall be refused; keys are provisioned per robot by a maintainer and are in no repository | CR 1.2, CR 1.5, CR 1.8, CR 1.9, CR 3.1, CR 3.8, CR 3.13, CR 4.3 | E-04; E-13 | both | TS-01, TS-04, TS-05, TS-14, TS-19 | SF-03, SF-04, SF-09 (channel 1); SR-90.01 | I, T, P |
| CSR-03 | **Per-node access control.** The access-control policies shall name the only nodes that may publish to the command arbiter's inputs, publish its output, send docking, undocking, manipulation and lift goals, and call lifecycle and parameter services; everything else is denied. At SL 1 of FR 2 the policy separates the robot's nodes from every other participant; at SL 2 (DQ-025 A) it also separates the nodes from each other, so a compromised node holds only its own permissions | CR 2.1, CR 2.1 RE(1) | E-04; E-13 | both | TS-01, TS-04, TS-05, TS-11, TS-14 | SR-00.02; SR-90.01 | I, T, P |
| CSR-04 | **One command arbiter.** One command arbiter shall be the only publisher to the firmware's command input. Every source (navigation, docking, teleoperation, the operator gateway) shall be a named input, with the stop request at the highest priority; a source that stops publishing shall lose its claim within the arbiter's timeout | CR 2.1, CR 3.5 | E-04; E-13 | both | TS-01, TS-02, TS-05 | SR-00.02; SF-04, SF-09 (channel 1) | T |
| CSR-05 | **Fresh commands only.** The firmware shall accept a command only if it carries a sequence number newer than the last one accepted and is younger than the command timeout, in addition to the validity and ceiling checks of SR-04.02 and SR-03.04; a repeated or stale command shall not refresh the watchdog | CR 3.5, CR 3.6, CR 3.7 | E-03; E-12 | both | TS-02 | SF-03, SF-04 (channel 1); SR-90.04 | T |
| CSR-06 | **One authenticated gateway.** The operator UI, rosbridge and the video server shall be reachable only through one gateway on the site interface: a personal account per operator and maintainer, passwords of at least 12 characters, lockout after 5 failed attempts and session lock after 15 minutes idle **(TBC)**, TLS, a notice at login. rosbridge shall be bound to the robot with an allowlist (goals, the stop request, status, the camera stream) and shall never offer `/cmd_vel`, lifecycle or parameter services | CR 1.1, CR 1.1 RE(1), CR 1.3, CR 1.4, CR 1.5, CR 1.7, CR 1.10, CR 1.11, CR 1.12, CR 2.1, CR 2.1 RE(2), CR 2.5, CR 3.1, CR 3.7, CR 3.8, CR 4.1, CR 4.3 | E-04; E-13, E-20 | both | TS-06, TS-18 | SR-90.02 | I, T, P |
| CSR-07 | **An honest stop request.** The operator interface shall call its stop a stop request, show the state of its link to the robot, and never present itself as an emergency stop; losing the operator link while the robot moves under an operator command shall stop that motion | CR 7.1 | E-04; E-13, E-20 | both | TS-07 | SF-04; SR-00.04 | I, T |
| CSR-08 | **A stop path with no network.** The chain-only functions and channel 2 of the two-channel functions shall have no network interface, and no network event shall delay a stop | CR 3.6, CR 5.1, CR 7.1 | safety chain | both | TS-07 | SF-01, SF-02, SF-05, SF-10, SF-12; SF-03, SF-04, SF-06, SF-09 (channel 2); SR-90.03 | I, T |
| CSR-09 | **No debug paths in the reference build.** The reference build shall not contain the raw-PWM, tuning or calibration inputs. A bench build that contains them shall identify itself (CSR-11, SR-07.02) and is used only under the hold point of WP-V-07 | CR 2.13, CR 7.7 | E-03; E-12 | both | TS-03 | SF-07 | I, T |
| CSR-10 | **Parameters closed to the network.** Motion-tuning parameters and the safety-related parameters of SR-00.05 shall not be writable from the network at runtime; the parameter services of the velocity smoother and the collision monitor shall be disabled or denied by policy; the firmware shall report its active parameters with a checksum | CR 3.4, CR 7.6 | E-03, E-04; E-12, E-13 | both | TS-03, TS-04 | SF-03, SF-06 (channel 1); SR-00.05 | I, T |
| CSR-11 | **Firmware identity and integrity.** The firmware shall report its build identity (version, commit, image hash) and its reset cause. It shall be built reproducibly with a pinned toolchain; the hash of each released image shall be recorded in the baseline and checked at commissioning. On CFG-002 the STM32 image shall be signed, verified at boot and read-out protected | CR 3.3, CR 3.4, CR 3.4 RE(1), CR 3.10, CR 3.12, CR 3.14, CR 3.14 RE(1), CR 7.8 | E-03; E-12 | both | TS-09 | SF-03, SF-04, SF-06, SF-09 (channel 1); SR-00.06, SR-90.04 | I, T |
| CSR-12 | **Pinned, signed compute images.** The compute's operating system and container images shall be built from dependencies pinned by digest, with a software bill of materials; images shall be signed and verified before deployment; on CFG-002 the Jetson's secure boot shall be enabled | CR 3.2, CR 3.3, CR 3.4, CR 3.4 RE(1), CR 3.10, CR 3.12, CR 3.14, CR 3.14 RE(1), CR 7.8 | E-04; E-13 | both | TS-10, TS-11 | SR-90.01 | I, T |
| CSR-13 | **A pinned supply chain.** Every reusable CI workflow shall be pinned to a commit, and every package and model to a version and a hash; the bill of materials shall be watched for published vulnerabilities, and a finding handled under WP-O-05 (62443-4-1 SM-9, SM-10, DM-1…DM-6) | CR 3.4, CR 7.8 | SZ-5 (build and supply) | both | TS-10, TS-15 | none | I |
| CSR-14 | **Least privilege on the compute.** Containers shall run as non-root users without host networking; only the driver container shall reach the serial device or the CAN interfaces; the operator gateway shall run in its own container with no device access | CR 2.1, CR 3.2, CR 5.1, CR 7.2, CR 7.7 | E-04; E-13 | both | TS-06, TS-11 | SR-90.01 | I, T, P |
| CSR-15 | **Key-only SSH.** Remote administration shall be by SSH with public keys only, one account per maintainer, no default or shared accounts and a lockout after repeated failures; SSH on the site interface shall accept only the maintainers' keys | CR 1.1, CR 1.1 RE(1), CR 1.3, CR 1.4, CR 1.5, CR 1.9, CR 1.11 | E-04; E-13 | both | TS-20 | none | I, T, P |
| CSR-16 | **Safety-device configuration locked.** The configuration ports of the safety scanner and the speed monitor shall be disconnected in operation; each device's password shall be set at commissioning and held by the safety manager; each device's configuration checksum shall be recorded under WP-P-02 and compared at every start-up check | CR 1.5, CR 3.11, CR 7.6 | safety chain | both | TS-12 | SF-02; SF-03 (channel 2); SR-00.05 | I |
| CSR-17 | **Chassis locked and sealed.** The chassis shall be locked in operation, with a tamper-evident seal over the cover that the start-up check inspects; the firmware's USB and debug ports, the CAN connectors and the compute's storage are inside it | CR 2.13, CR 3.11 | E-01; E-11 | both | TS-09, TS-12, TS-16 | none | I |
| CSR-18 | **Arm and bus access.** On CFG-002 the manipulation server and the policy runtime shall accept goals only from the nodes CSR-03 names; only the arm-driver process shall write to the arms' CAN-FD bus; no network interface shall reach CAN1, CAN2, CAN3 or CAN-FD | CR 2.1, CR 5.1 | E-12, E-13, E-18 | CFG-002 | TS-14, TS-16 | SR-11.04 | I, T |
| CSR-19 | **Policy model integrity.** On CFG-002 the policy model shall be pinned by hash and signed; the runtime shall load it read-only and refuse to start on a mismatch | CR 3.4, CR 3.4 RE(1) | E-13 | CFG-002 | TS-15 | none | I, T |
| CSR-20 | **Security event log.** Security events (logins and failed logins, denied permissions, parameter writes, a change of firmware identity, stop requests, link losses) shall be logged with synchronised time, copied off the robot and protected from change; telemetry shall never be presented as safety evidence (upstream `TELEMETRY-NOT-SAFETY-EVIDENCE`) | CR 2.8, CR 2.9, CR 2.10, CR 2.11, CR 3.9, CR 6.1 | E-04; E-13 | both | TS-17 | none | I, T |
| CSR-21 | **Overload never delays a stop.** Overload of the site network, the robot's Wi-Fi link or the compute shall not delay a stop; the gateway shall limit request rates; loss of the commanding link shall stop the motion it commanded | CR 7.1, CR 7.1 RE(1), CR 7.2 | E-04; E-13 | both | TS-07, TS-08 | SF-04 | T, P |
| CSR-22 | **Backup and recovery.** The robot's configuration, keys and parameters shall be backed up off the robot; the compute and the firmware shall be restorable to a recorded baseline image | CR 3.10, CR 7.3, CR 7.4 | E-03, E-04; E-12, E-13 | both | TS-09 | none | T |
| CSR-23 | **Site Wi-Fi with a key.** Requirement on the site (§6): the robot and its operators shall use a Wi-Fi network with WPA2 or WPA3 and a site-specific key, never an open or guest network | CR 2.2 | SZ-1 (site) | both | TS-01, TS-06 | none | I |
| CSR-24 | **Camera streams protected.** Camera streams shall leave the robot only through the gateway (CSR-06) and encrypted; recording shall be off by default; the information for use shall say what is recorded and for how long | CR 4.1, CR 4.3 | E-04; E-13 | both | TS-18 | none | I, T |

![Figure 4-1: a matrix with the requirements CSR-01 to CSR-24 down the side and the threat scenarios TS-01 to TS-20 across the top, a dot where a requirement treats a scenario. A right-hand column of chips names the safety functions each requirement supports. Scenario TS-13 has an empty column, marked outside the security level target. Column heads are shaded by the residual risk of WP-C-07: green for low, amber for the two medium residuals TS-07 and TS-12](figures/fig-c08-4-1-trace.svg)

*Figure 4-1.* Every requirement treats at least one scenario, and every scenario except TS-13 is treated. The
column of chips on the right is §5 read the other way: which safety function leans on which requirement.
Generated by [`figures/fig_c08.py`](figures/fig_c08.py) from §3 and §4 and the tables of WP-C-07; CI fails if a
reference does not resolve or the two documents disagree.

## 5. Interface to the safety functions

Which requirements protect each safety function, and what still holds if the protection fails. The middle column
of WP-C-07 §6 rests on the last column here.

| SF | Path | Protected by | If the protection fails |
|---|---|---|---|
| SF-01 | chain only | CSR-08, CSR-17 | nothing in software can hold a contactor closed; an attacker needs the chassis open |
| SF-02 | chain only, with a safety-rated detection device | CSR-08, CSR-16, CSR-17 | the device's configuration is the attack surface (WP-C-07 TS-12); no other function catches a shortened field |
| SF-03 | channel 1 firmware, channel 2 hardwired speed monitor | CSR-01, CSR-02, CSR-04, CSR-05, CSR-08, CSR-10, CSR-11, CSR-16 | channel 2 bounds the speed channel 1 commands and trips on a disagreement (SR-00.07); a changed speed-monitor threshold is TS-12 |
| SF-04 | channel 1 firmware, channel 2 hardware watchdog | CSR-01, CSR-02, CSR-04, CSR-05, CSR-07, CSR-08, CSR-11, CSR-21 | channel 2 stops the robot when channel 1's heartbeat stops |
| SF-05 | chain only (monitored manual reset) | CSR-08 | the reset is wired; no message can reset the chain |
| SF-06 | channel 1 firmware, channel 2 hardwired monitor | CSR-08, CSR-10, CSR-11 | channel 2 trips on a speed disagreement between the channels |
| SF-07 | firmware build | CSR-09, CSR-11 | a bench build reports itself (SR-07.02) and SF-03 channel 2 still bounds speed |
| SF-08 | warning device driven from the chain state and the motion request (SR-08.04) | CSR-04, CSR-05 | a forged motion request can at worst sound a warning; a suppressed one leaves the residual SF-08 already has, which SF-02 covers |
| SF-09 | channel 1 firmware, channel 2 enabling device | CSR-01, CSR-02, CSR-04, CSR-08, CSR-11 | releasing the enabling device stops the robot through channel 2 whatever the software does |
| SF-10 | chain only (CFG-002) | CSR-08, CSR-17 | the pose signals are wired into the safety controller (SR-10.04 cross-checks them) |
| SF-11 | station detection device and power removal (CFG-002) | CSR-08, CSR-16, CSR-18 | the stop removes the arms' actuator power; the manipulation server's hand-over rule (SR-11.04) is the only software part, and CSR-18 protects it |
| SF-12 | chain only (CFG-002) | CSR-08, CSR-17 | holding is by design on power loss; no command is needed |

## 6. Requirements on the site and the operator

The site network, the operator's devices and the keys to the chassis are outside the item (WP-C-01 §3.2). What
this record needs from them is an assumption of use, carried to the information for use
([WP-O-03](../09-production-operation/WP-O-03-information-for-use.md)) and to the start-up check.

| Requirement | Why | From |
|---|---|---|
| A Wi-Fi network with WPA2 or WPA3 and a site-specific key for the robot and its operators; never an open or guest network | without it the site network is anyone's (CSR-23) | WP-C-07 AS-01 |
| The chassis locked in operation, the key held by named maintainers, the seal checked at the start-up check | physical access is the one path the network requirements do not cover (CSR-17) | WP-C-07 AS-02 |
| One account per person on the gateway and for SSH; accounts removed when a person leaves | CR 1.3 is met only if the site manages its people (CSR-06, CSR-15) | CR 1.3 |
| Security findings reported through the route of `SECURITY.md`, incidents through WP-O-05 | 62443-4-1 DM-1 needs a reporting route | 62443-4-1 DM-1 |

## 7. The security requirements of WP-S-02

[WP-S-02 §15](../03-system/WP-S-02-safety-requirements.md#15-security-requirements-supporting-the-safety-functions-iec-62443-4-2-target-dq-013)
states, as safety requirements, what the safety functions need from security. Each is met here:

| WP-S-02 | Met by |
|---|---|
| SR-90.01 | CSR-01, CSR-02, CSR-03, CSR-12, CSR-14 |
| SR-90.02 | CSR-06 |
| SR-90.03 | CSR-08 |
| SR-90.04 | CSR-05, CSR-11 |

## 8. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | DQ-025: FR 2 at SL 2; CSR-03 and CR 2.1 RE(1), RE(2) follow the answer | Project lead | G1 |
| OI-2 | DQ-026: the residual of WP-C-07 TS-07 and TS-12; a "B" or "C" answer adds a requirement here | Project lead | G1 |
| OI-3 | Confirm every CR, enhancement and its security level against a licensed copy of IEC 62443-4-2 | Cybersecurity manager | when DQ-016 allows |
| OI-4 | Every **(TBC)** value of CSR-06 (password length, lockout, session lock) | Cybersecurity manager | G2 (WP-S-07) |
| OI-5 | CSR-11, CSR-12, CSR-18 and CSR-19 on CFG-002 are re-checked when the STM32, Jetson and arm interfaces are public | Cybersecurity manager | when public |
