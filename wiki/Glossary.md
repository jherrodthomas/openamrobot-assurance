# Glossary

The codes that appear in file names, commit messages, the records and the maps, decoded in one place.

## Work product prefixes

Each work product is named `WP`, a letter for its area, and a number, for example `WP-C-04` is the safety function
specification. The [work product register](../assurance/01-management/WP-M-00-work-product-register.md) lists every
one with its clauses, gate and status.

| Prefix | Area | Folder |
|---|---|---|
| `WP-M` | Management: strategy, plans, confirmation measures, regulatory strategy, impact analysis | `01-management/` |
| `WP-C` | Concept: machine limits, risk assessment, safety functions and PLr, risk reduction, cybersecurity and ML concepts | `02-concept/` |
| `WP-S` | System: safety requirements, SRP/CS architecture, stopping budget, I/O, cybersecurity architecture | `03-system/` |
| `WP-H` | Hardware: safety chain, electrical safety, failure analysis, PL calculation, component qualification, stability | `04-hardware/` |
| `WP-W` | Software: firmware and ROS 2 chain requirements, architecture, verification, parameters, ML engineering | `05-software/` |
| `WP-V` | Validation: stopping, detection, E-stop, fault injection, cybersecurity, test operations, field trials | `06-validation/` |
| `WP-P` | Supporting processes: configuration, change, problem resolution, documentation, review, tools, release, the process model | `07-supporting/`, `process/` |
| `WP-A` | Analyses: FMEA, FTA, CCF, STPA, independence of the chain | `08-analyses/` |
| `WP-O` | Operation: assembly, operation, information for use, field monitoring, incident response | `09-production-operation/` |
| `WP-K` | Safety case, technical documentation, cybersecurity case, assessments, release record, AI Act record | `10-safety-case/` |
| `WP-T` | Traceability data | `trace/` |

## Record identifiers

| Code | Reads as | Where it lives |
|---|---|---|
| `H-` | Hazard | [Risk assessment, WP-C-03](../assurance/02-concept/WP-C-03-risk-assessment.md) |
| `SF-` | Safety function, with its required Performance Level `PLr` | [WP-C-04](../assurance/02-concept/WP-C-04-safety-functions-and-plr.md) |
| `SR-` | Safety requirement of the SRP/CS | [WP-S-02](../assurance/03-system/WP-S-02-safety-requirements-specification.md) |
| `HWSR-`, `SWSR-` | Hardware and software safety requirement | [WP-H-01](../assurance/04-hardware/WP-H-01-hardware-safety-requirements.md), [WP-W-02](../assurance/05-software/WP-W-02-software-safety-requirements.md) |
| `CSR-`, `TS-` | Cybersecurity requirement, threat scenario | [WP-C-08](../assurance/02-concept/WP-C-08-cybersecurity-requirements-and-sl-target.md), [WP-C-07](../assurance/02-concept/WP-C-07-cybersecurity-threat-and-risk-assessment.md) |
| `AIR-` | Requirement on a learned component | [WP-C-09](../assurance/02-concept/WP-C-09-ml-component-definition-and-safety-requirements.md) |
| `FI-`, `TC-` | Functional insufficiency, triggering condition | [WP-C-10](../assurance/02-concept/WP-C-10-functional-insufficiency-analysis.md) |
| `PAR-` | Safety-related parameter | [WP-W-09](../assurance/05-software/WP-W-09-safety-parameters-and-configuration-data.md) |
| `AOU-` | Assumption of use: what the analysis assumes about the environment, the operator or the site | Safety case and machine definition |
| `VS-` | Verification specification (test case) | The verification work products |
| `DF-` | Defeater: known counter-evidence against a claim | [Safety case, WP-K-01](../assurance/10-safety-case/WP-K-01-safety-case.md) |
| `GAP-` | A finding of the baseline gap assessment; never reused | [Gap assessment](../assurance/00-assessment/gap-assessment.md) |
| `OI-` | Open item of a work product, due at a gate | The last section of every work product |
| `IX-`, `FB-` | Cross-domain interface, feedback route | [Process model](../assurance/process/README.md) |
| `GOV-`, `CON-`, `DES-`, `DEV-`, `INT-`, `REL-`, `OPS-` | Activities of the process model, by phase | [Process maps](Process-maps.md) |
| `CR-`, `FSA-`, `AUD-`, `CS-`, `ML-R`, `NB-` | Confirmation reviews, functional safety assessments, audits, cybersecurity review and assessment, ML reviews, notified body | [WP-M-06](../assurance/01-management/WP-M-06-confirmation-measures-plan.md) |
| `DQ-` | Decision question for the project lead | [Decision register](How-decisions-are-made.md) |
| `T-`, `D-` | Tailoring decision, strategic decision | [WP-M-01 §5, §8](../assurance/01-management/WP-M-01-assurance-strategy.md) |
| `G0` to `G6` | Lifecycle gates | [WP-M-00 §2](../assurance/01-management/WP-M-00-work-product-register.md#2-gates) |
| `CFG-` | Robot configuration (once the case records are ported) | `case/configurations/` |

## Machinery safety vocabulary

| Term | Meaning |
|---|---|
| **Performance Level (PL)** | ISO 13849-1's measure of a safety function's ability to perform under foreseeable conditions, PL a (lowest) to PL e. The **required** PL, `PLr`, comes from the risk graph on the hazard; the **achieved** PL from the control system's category, MTTFD, DCavg and CCF. |
| **Category** | The designated architecture of a safety-related part: B, 1, 2, 3 or 4. Category 3 and 4 have two channels so that a single fault does not lose the function. |
| **MTTFD, DCavg, CCF** | Mean time to dangerous failure per channel; average diagnostic coverage; the common cause failure score. The three numbers the PL calculation needs. |
| **SRP/CS** | Safety-related part of a control system: everything from the sensor or button through the logic to the contactor that implements a safety function. |
| **Safety function** | A function of the machine whose failure can immediately increase risk: emergency stop, protective stop, safely limited speed, and so on. |
| **Emergency stop, protective stop** | A stop a person triggers (ISO 13850) versus a stop a safeguard triggers when a person enters a protective field. |
| **Stop category 0 / 1** | EN 60204-1: immediate removal of power (0) or a controlled stop followed by removal of power (1). |
| **OSSD** | Output signal switching device: the safety outputs of a scanner or light curtain that feed the safety relay. |
| **Protective field, safety distance** | The area a scanner guards; its size follows from the approach speed and the measured stopping distance (ISO 13855). |
| **Three-step method** | ISO 12100's order of risk reduction: inherently safe design first, then safeguarding, then information for use. |
| **Technical documentation** | The file Regulation (EU) 2023/1230 Annex IV requires a manufacturer to hold; [WP-K-02](../assurance/10-safety-case/WP-K-02-technical-documentation-index.md) indexes it. |
| **Security level target (SL-T)** | IEC 62443's target per foundational requirement, SL 1 to SL 4. |
| **Doer, checker, checker of last resort** | The ROS 2 stack proposes; the firmware checks; the hardwired chain acts regardless of software. |
| **Gate A unit** | Upstream's name for the robot that has been wired, flashed and driven: the reference configuration. See [Reference robot](Reference-robot.md). |
| **Hold point** | A condition no test proceeds past: [WP-V-07](../assurance/06-validation/WP-V-07-test-operations.md) before any on-ground test, and [WP-V-03](../assurance/06-validation/WP-V-03-personnel-detection-validation.md) before anyone shares the area. |

## Safety-case vocabulary

| Term | Meaning |
|---|---|
| **Claim** | A statement the safety case argues is true. |
| **Evidence item** | A test result, analysis or review that supports a claim. Each carries a review state; it is *accepted* only after confirmation review. |
| **Defeater** | Known counter-evidence, or a reason the argument might not hold. Open defeaters are published, not hidden. GAP-01…GAP-40 are the first. |
| **Confirmation review** | An independent check that a work product does what its standard asks. Nothing leaves draft without a verification review; nothing is accepted without a confirmation measure. |
| **Baseline** | A frozen, named state of the whole record. |
| **Independence I0 to I3** | Who may review: the author, another person, someone outside the team, someone outside the organisation. |
