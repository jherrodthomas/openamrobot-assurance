# For the assessor

This page is for the person asked to look at the fork independently: a confirmation reviewer, a functional safety
auditor or assessor, a cybersecurity or ML reviewer, a notified body's examiner, or someone deciding whether to take
that role on. It says what state to expect, where the plans are, what you would be asked to do, what to assess
against, how independence is recorded, and how to send findings. Every line points at the record that owns it;
this page decides nothing and claims nothing.

> [!NOTE]
> **No confirmation measure has been performed, and no assessor has been engaged.** The project has one
> maintainer, so every review at independence level I2 or I3 is planned as external. Whether and when to engage an
> assessor is an open question for the project lead (decision register DQ-007).

## Where things stand

| Fact | Where it is recorded |
|---|---|
| No confirmation review, audit or assessment has taken place | [Confirmation records folder](../assurance/10-safety-case/confirmation/README.md), [WP-M-06 §1](../assurance/01-management/WP-M-06-confirmation-measures-plan.md#1-purpose) |
| No gate review has been held | [Gate records folder](../assurance/10-safety-case/gates/README.md) |
| The assessor role is open | [WP-M-02 §3.1](../assurance/01-management/WP-M-02-safety-plan.md#31-role-assignments); decision register entry DQ-007 in [`register.yaml`](../assurance/01-management/decisions/register.yaml) |
| Every role in the safety plan resolves to the maintainer; roles needing independence are TBD | [WP-M-02 §3.1](../assurance/01-management/WP-M-02-safety-plan.md#31-role-assignments) |
| Much of the record is AI-assisted drafting, which counts at I0 and gives no review credit | [WP-M-02 §3.3](../assurance/01-management/WP-M-02-safety-plan.md#33-ai-assisted-authoring) |
| Clause citations are marked "check against the licensed copy"; no standard is held | [WP-M-06 OI-1](../assurance/01-management/WP-M-06-confirmation-measures-plan.md#11-open-items); decision register DQ-014 |
| No work product is approved or baselined; 7 are drafts, the rest skeletons | [WP-M-00 §3](../assurance/01-management/WP-M-00-work-product-register.md#3-register) |
| Nothing has been tested: the fork has driven no robot | [WP-V-07](../assurance/06-validation/WP-V-07-test-operations.md), [test sites](../assurance/06-validation/test-sites/README.md) |

![The work product register at a glance.](register-status.svg)

*Rendered from the register at every wiki sync.*

## Read in this order

| Step | Work product | What to take from it |
|---|---|---|
| 1 | [WP-M-01 assurance strategy](../assurance/01-management/WP-M-01-assurance-strategy.md) | The one configuration claims apply to (§3.1), the three-layer argument the whole case rests on (§6), how each standard is used (§4), the tailoring decisions T-01 to T-14 (§5), the strategic decisions and their status (§8), the top risks (§9) |
| 2 | [WP-M-02 functional safety plan](../assurance/01-management/WP-M-02-safety-plan.md) | Roles and who holds them (§3), the activities per phase (§4), the early-implementation rule for the bench safety hardware (§4.1), gate reviews (§10) |
| 3 | [WP-M-06 confirmation measures plan](../assurance/01-management/WP-M-06-confirmation-measures-plan.md) | What you would be asked to do (below), the independence scheme and its mapping onto IEC 61508-1 §8 (§3), the assessor qualification (§6.1), the schedule (§9), the records (§10) |
| 4 | [WP-M-13 regulatory conformity strategy](../assurance/01-management/WP-M-13-regulatory-conformity-strategy.md) | The Machinery Regulation route, the Annex I Part A threshold, the technical documentation mapping |
| 5 | [WP-M-00 work product register](../assurance/01-management/WP-M-00-work-product-register.md) | The gates and their exit criteria (§2), every work product with its clauses, gate and status (§3) |
| 6 | [Process model and maps](../assurance/process/README.md) | How the disciplines' work fits together per phase, the cross-domain interfaces, the confirmation measures each gate needs and whether they have been performed, the readiness of each gate |
| 7 | [Baseline gap assessment](../assurance/00-assessment/gap-assessment.md) | What the project itself found wanting in the inherited robot and process, finding by finding, with the standard each bears on |
| 8 | [WP-K-04 functional safety assessment](../assurance/10-safety-case/WP-K-04-functional-safety-assessment.md) | The report template you would fill in, including the independence declaration |

[Standards at a glance](Standards-at-a-glance.md) lists which standard each work product answers to.
[How the repository is organized](How-the-repository-is-organized.md) maps the folders.

## What you would be asked to do

WP-M-06 plans every measure by gate; the summary table is
[WP-M-06 §9](../assurance/01-management/WP-M-06-confirmation-measures-plan.md#9-schedule-summary).

- **Confirmation reviews** CR-01 to CR-12, each naming the work products, the planned independence level and the
  gate ([§4.1](../assurance/01-management/WP-M-06-confirmation-measures-plan.md#41-list-and-independence)). The risk
  assessment (CR-02), the safety functions and their required PL (CR-04), the PL calculation (CR-07) and the safety
  case (CR-12) are the ones that carry the argument.
- **Functional safety audits** AUD-1 and AUD-2, checking that the plans are carried out as written (§5).
- **Functional safety assessments** FSA-I1 and FSA-I2 at the concept and system-design gates, and the final FSA-F
  before any release record (§6), in the sense of IEC 61508-1 §8 and the validation of the achieved PL against the
  required PL.
- **Cybersecurity review and assessment** CS-I1 and CS-A1 under IEC 62443 (§7).
- **ML reviews** ML-R1 to ML-R3 of the position that no learned component carries a safety function (§7).
- **Conformity assessment** NB-1 by a notified body, if the route the lead chooses needs one (§8).

Who may do each is in [§6.1](../assurance/01-management/WP-M-06-confirmation-measures-plan.md#61-assessor-qualification-and-independence):
no authorship of or contribution to the assessed work, no reporting line to the maintainer, no financial interest
beyond the fee, no involvement in upstream OpenAMRobot development, competence in machinery functional safety with
evidence, declared in writing in each report.

## What to assess against

A review is against a named state of the record, never against the moving branch.

| Thing | Where |
|---|---|
| The commit of this record and of the platform repositories | The `Baseline` field of every work product; the gap assessment header |
| The reference configuration the claims apply to | [WP-M-01 §3.1](../assurance/01-management/WP-M-01-assurance-strategy.md#31-reference-configuration-the-only-scope-claims-apply-to) and the [reference robot](Reference-robot.md) page |
| Which files count as safety-relevant, and in which class | [Safety-relevant paths](../assurance/07-supporting/safety-relevant-paths.txt), owned by WP-P-01 |
| Baselines, snapshots and controlled copies | To come with the Living Safety Case port ([`case/`](../assurance/case/README.md)) and WP-P-04 |

Everything is public. Read access is a clone of the repository at the baseline commit.

## How independence is recorded

- The levels I0 to I3 and who can reach each one today are in
  [WP-M-06 §3](../assurance/01-management/WP-M-06-confirmation-measures-plan.md#3-independence-levels).
- A confirmation record is written by the named reviewer at the required level, states that independence in
  writing, and is stored under [`10-safety-case/confirmation/`](../assurance/10-safety-case/confirmation/README.md)
  using the WP-P-05 record template.
- **What does not count.** A passing CI run. An AI-generated pre-review. A self-assessment such as the
  [ASPICE capability baseline](../assurance/01-management/WP-M-12-process-capability-baseline.md).

## Where the known problems are listed

The project publishes its own counter-evidence. Start with these rather than hunting for it.

| List | Where |
|---|---|
| Findings against the inherited robot and process, GAP-nn | [Gap assessment](../assurance/00-assessment/gap-assessment.md) |
| Open items of each work product | The last section of every work product, counted per gate in the [gate skeletons](../assurance/10-safety-case/gates/skeletons/) |
| Open cross-domain interfaces | The readiness section of each [process map](Process-maps.md) |
| Project risks | [WP-M-07](../assurance/01-management/WP-M-07-risk-management.md) (skeleton; the top risks are in [WP-M-01 §9](../assurance/01-management/WP-M-01-assurance-strategy.md#9-top-risks-to-the-assurance-path)) |
| Questions the lead has decided, and the ones still open | [Decision register](../assurance/01-management/decisions/README.md); see [How decisions are made](How-decisions-are-made.md) |

## How to send findings

- **A finding from a confirmation measure** becomes a GitHub issue labelled `confirmation-finding`, handled under
  [WP-P-03](../assurance/07-supporting/WP-P-03-problem-resolution.md), and is listed with its ID in your record.
- **A comment on a work product short of a formal review** goes to the pull request that changes it, or to an
  [issue](https://github.com/jherrodthomas/openamrobot-assurance/issues) naming the work product and section.
- **A vulnerability** goes through [SECURITY.md](../SECURITY.md), never a public issue. See
  [Reporting a safety concern](Reporting-a-safety-concern.md).

## Taking the role on

Engaging an assessor is a decision of the project lead, recorded in the decision register (DQ-007 for functional
safety; the cybersecurity assessor and the notified body are open items of WP-M-06 and WP-M-13). If you are
considering it, the shortest route is an issue saying so, with the competence evidence
[WP-M-04](../assurance/01-management/WP-M-04-organization-competence-safety-culture.md) asks for.

> Assurance status represents recorded engineering evidence and review state. It does not constitute
> certification or approval for operation around people.
