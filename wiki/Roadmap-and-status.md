# Roadmap and status

Four phases. Status is taken from what exists in the repository: "draft" means written but not reviewed,
"skeleton" means the structure and clause map exist, and nothing is called complete before its review. This table
mirrors the [roadmap in the README](../README.md#roadmap); a status changes here only when the owning work product
changes its document-control header.

![Roadmap: four phases, status from repository evidence.](../docs/assets/openamrobot/roadmap.svg)

| Phase | State |
|---|---|
| 1 · Foundation | Active |
| 2 · Safety engineering | Active |
| 3 · Build and verify | Planned |
| 4 · Validate and release | Planned |

## Where each phase stands

| Phase | Work | Status |
|---|---|---|
| **1 · Foundation** | [Assurance strategy](../assurance/01-management/WP-M-01-assurance-strategy.md), [safety plan](../assurance/01-management/WP-M-02-safety-plan.md), [confirmation measures](../assurance/01-management/WP-M-06-confirmation-measures-plan.md), [regulatory strategy](../assurance/01-management/WP-M-13-regulatory-conformity-strategy.md) | Draft |
| | [Baseline gap assessment](../assurance/00-assessment/gap-assessment.md) | Draft |
| | [Work product register](../assurance/01-management/WP-M-00-work-product-register.md), [process model](../assurance/process/README.md), [decision register](../assurance/01-management/decisions/README.md) | Draft; checked by CI |
| | Project plan, QA plan, risk register, cybersecurity and ML plans, upstream management, impact analysis, capability baseline | Skeleton |
| | [Living Safety Case records and dashboard](../assurance/case/README.md) | Draft: records at BL-001, validated and drawn by CI |
| **2 · Safety engineering** | [Item definition](../assurance/02-concept/WP-C-01-item-definition.md), [operating environment](../assurance/02-concept/WP-C-02-operating-environment-and-tasks.md), [risk assessment](../assurance/02-concept/WP-C-03-risk-assessment.md), [safety functions and PLr](../assurance/02-concept/WP-C-04-safety-functions-and-plr.md), [human-robot interaction and misuse](../assurance/02-concept/WP-C-06-human-robot-interaction-and-misuse.md) | Draft; figures generated and checked by CI |
| | [Risk reduction concept](../assurance/02-concept/WP-C-05-risk-reduction-concept.md) | Draft; every rated row allocated to the three steps with a residual class |
| | [3D review scenes](../assurance/sim/README.md) | Draft; eight renders of the base, the manipulator and five hazard scenes; pictures only, no evidence credit |
| | [Gazebo scenario tests](../assurance/sim/gazebo/README.md) | Draft; six scenarios on the baseline and on upstream main, run in CI; each check carries the outcome the record predicts; two findings under GAP-40; development evidence only, no evidence credit |
| | [Cybersecurity threat assessment](../assurance/02-concept/WP-C-07-cybersecurity-threat-and-risk-assessment.md) and [cybersecurity requirements](../assurance/02-concept/WP-C-08-cybersecurity-requirements-and-sl-target.md) | Draft; twenty threat scenarios rated before and after treatment, 24 requirements traced to them and to the safety functions; nothing implemented or tested |
| | [Insufficiency analysis](../assurance/02-concept/WP-C-10-functional-insufficiency-analysis.md), [ML component definition](../assurance/02-concept/WP-C-09-ml-component-definition-and-safety-requirements.md) | Skeleton |
| | [Test operations hold point](../assurance/06-validation/WP-V-07-test-operations.md) | Draft; the bench safety hardware waits on the lead |
| **3 · Build and verify** | Bench safety hardware, firmware hardening, [chain architecture](../assurance/03-system/WP-S-03-technical-safety-concept.md), [stopping budget](../assurance/03-system/WP-S-04-response-time-and-stopping-budget.md) and [PL calculation](../assurance/04-hardware/WP-H-04-reliability-data-and-pl-calculation.md), [stopping tests](../assurance/06-validation/WP-V-02-stopping-braking-stability-tests.md), [fault injection](../assurance/06-validation/WP-V-05-fault-injection.md) | Planned |
| **4 · Validate and release** | [Safety validation](../assurance/06-validation/WP-V-01-safety-validation.md), [assessment](../assurance/10-safety-case/WP-K-04-functional-safety-assessment.md), [technical documentation](../assurance/10-safety-case/WP-K-02-technical-documentation-index.md), [release record](../assurance/10-safety-case/WP-K-06-release-record.md), [field monitoring](../assurance/09-production-operation/WP-O-04-field-monitoring.md) | Planned |

## What the next gate needs

![The seven phases and gates; today is P0 and no gate is passed.](../docs/assets/openamrobot/lifecycle.svg)

G0 needs the plans approved, the roles assigned and configuration control running. Today every plan is a draft or
a skeleton, the verification reviewer and QA roles are open, and the three platform repositories are not yet forked
and pinned. The generated [G0 readiness section](../assurance/process/maps/g0-governance.md#5-g0-readiness) lists
what is missing, and the [G0 gate skeleton](../assurance/10-safety-case/gates/skeletons/G0-skeleton.md) is the
pre-filled review record. The questions that wait on the project lead are in the
[decision register](How-decisions-are-made.md); the two that shape everything below G0 are the regulatory frame and
the conformity route.

## Sources

- [README, Roadmap](../README.md#roadmap)
- [WP-M-00 work product register](../assurance/01-management/WP-M-00-work-product-register.md): every work product, its gate and status
- [WP-M-01 §7](../assurance/01-management/WP-M-01-assurance-strategy.md#7-phases-gates-and-sequence): phases, gates and hold points
