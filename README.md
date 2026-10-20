# OpenAMRobot assurance

OpenAMRobot, but designed for safety and assurance.

The engineering assurance record for a safety-assured fork of the
[OpenAMRobot](https://github.com/openAMRobot) mobile robot platform, built the same way as
[LionDriver](https://github.com/jherrodthomas/LionDriver): a baseline gap assessment of the inherited code, then the
management, concept, system, hardware, software, validation and safety-case work products, with a Living Safety Case
whose every figure is generated from reviewed records.

> [!IMPORTANT]
> Everything here is a **draft prepared for engineering review**. Nothing has passed verification review,
> confirmation review or a functional-safety assessment. The OpenAMRobot platform is research hardware: it is not
> CE-marked, makes no claim to a Performance Level under ISO 13849-1, and is not approved for operation around
> people without supervision.

## Standards

OpenAMRobot is a machine, not a road vehicle, so the frame differs from LionDriver's:

| Topic | Standard | Replaces (LionDriver) |
|---|---|---|
| Risk assessment and reduction | ISO 12100:2010 | HARA (ISO 26262-3) |
| Driverless industrial trucks, including AMRs | ISO 3691-4:2023 | vehicle-level safety goals |
| Industrial robots and robot systems (arms, 2.0) | ISO 10218-1/-2:2025, ISO/TS 15066:2016 | n/a |
| Safety-related parts of control systems | ISO 13849-1:2023, ISO 13849-2:2012 | ASIL (ISO 26262) |
| Functional safety of E/E/PE systems, where 13849 runs out | IEC 62061:2021, IEC 61508:2010 | ISO 26262-5/-6 |
| Industrial mobile robots, US market | ANSI/A3 R15.08-1:2020 | n/a |
| Cybersecurity | IEC 62443-4-1, -4-2 | ISO/SAE 21434 |
| Machine learning in safety functions | ISO/IEC TR 5469:2024 | ISO/PAS 8800 |
| Regulatory | Regulation (EU) 2023/1230 (Machinery), in force 20 January 2027; Regulation (EU) 2024/1689 (AI Act) Annex I | UNECE / national |
| Safety case structure | UL 4600 principles | same |

## Start here

| Document | Why read it |
|---|---|
| [assurance/00-assessment/gap-assessment.md](assurance/00-assessment/gap-assessment.md) | Baseline review of the inherited OpenAMRobot repositories against the standards above |
| [assurance/01-management/decisions/](assurance/01-management/decisions/README.md) | Questions that wait on the project lead |
| [assurance/README.md](assurance/README.md) | Layout, conventions and identifiers |

## Upstream and licensing

OpenAMRobot is published by Botshare LTD under MIT (software), CERN-OHL-P-2.0 (hardware) and CC BY 4.0
(documentation). This repository holds only assurance work products; the forked code lives in the forked platform
repositories. Forks must not imply Botshare's endorsement (upstream `GOVERNANCE.md`). The assurance record carries
no OpenAMRobot trademark claim.
