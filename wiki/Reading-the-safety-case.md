# Reading the safety case

The safety argument is published while it is being built. This page explains what the safety case is today, what
the dashboard will show once the Living Safety Case tooling exists, and what it does and does not promise.

## Today

The safety case is the document [WP-K-01](../assurance/10-safety-case/WP-K-01-safety-case.md), a skeleton with the
claim structure of [WP-M-01 §3.2](../assurance/01-management/WP-M-01-assurance-strategy.md#32-top-level-claim):

- **G0** The reference configuration, operated within its operating-environment limits by briefed personnel, does
  not expose people to unacceptable risk.
- **G1** The hazards are identified and each is reduced by design, safeguarding or information for use, in that
  order.
- **G2** Every safety function achieves its required Performance Level.
- **G3** The performance limits of sensing and navigation are known, bounded and covered.
- **G4** Learned components carry no safety function and cannot defeat one.
- **G5** Cybersecurity risks to safety are treated.
- **G6** The work was done by competent people under controlled processes with independent confirmation.

No claim has evidence. No evidence is accepted. The known counter-evidence is GAP-01…GAP-40 in the
[gap assessment](../assurance/00-assessment/gap-assessment.md), which become the first defeaters.

## What the dashboard shows

[`assurance/case/`](../assurance/case/README.md) holds claims, evidence items, defeaters, assumptions,
configurations, baselines and reviews as machine-readable records, a validator, and a generator that draws the
README dashboard and a one-line headline: the lifecycle stage, the baseline, the number of claims and how many have
accepted evidence, the evidence items and how many are accepted, the open defeaters, and a digest of every record.
These rules apply:

- A claim counts as accepted only when a recorded review accepts it, every piece of evidence it cites is available
  and accepted, and no defeater against it is open. The validator refuses anything else.
- A passing CI run, a passing test or the existence of a document never accepts a claim on its own, and an
  AI-generated review is not a substitute for independent confirmation.
- Every figure is generated from the records, never typed by hand, and the assurance workflow fails when the
  committed dashboard is out of date.

## Why zero accepted will be the honest number

Evidence becomes *accepted* only after a confirmation review by someone independent of the author
([WP-M-06](../assurance/01-management/WP-M-06-confirmation-measures-plan.md)). No work product has had one, no
assessor is engaged, and the project has one person. A dashboard that showed accepted evidence before any review had
happened would be the one to distrust.

## How the records will fit together

1. **Hazards and safety functions**, from the [risk assessment](../assurance/02-concept/WP-C-03-risk-assessment.md)
   and the [safety function specification](../assurance/02-concept/WP-C-04-safety-functions-and-plr.md). Each
   function carries a required PL.
2. **Claims**: the argument that each function achieves its PL and each hazard is reduced, broken into statements
   that can be evidenced.
3. **Evidence**, linked to claims: the PL calculation, the component certificates, the stopping-distance and
   detection tests, the fault-injection results, each with a review state.
4. **Defeaters**, attached to claims: the gap assessment, the open interfaces of the process model, the
   performance limits of the insufficiency analysis.
5. **Baselines and reviews**: named states of the whole, and the confirmation reviews recorded against them.

- [Read the safety case skeleton, WP-K-01](../assurance/10-safety-case/WP-K-01-safety-case.md)
- [Known gaps](../assurance/00-assessment/gap-assessment.md)
- [Gate skeletons](../assurance/10-safety-case/gates/skeletons/), generated from the process model

> Assurance status represents recorded engineering evidence and review state. It does not constitute
> certification or approval for operation around people.
