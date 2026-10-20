# Frequently asked questions

Short answers with a link to the record that holds the long one.

## Is the robot safe, certified or CE-marked?

No. OpenAMRobot is research hardware. As inherited it has no emergency stop in its documented wiring, no brakes, no
fuse, no disconnect and no safety-rated personnel detection; its only stop is a software watchdog. The fork's record
exists to change that in the open, starting with the [gap assessment](../assurance/00-assessment/gap-assessment.md).
No safety function reaches any Performance Level today, no assessment has taken place, and nothing is approved for
operation around people. [For the assessor](For-the-assessor.md) says what an assessment would involve.

## Is the fork safer than upstream OpenAMRobot?

Not yet, and the project does not claim it is. The fork carries no code changes; what it adds today is the record:
the gap assessment, the strategy, the plans, the register and the process model. The first engineering change will
be bench safety hardware on any unit the fork tests with, and it waits on a decision by the lead.

## Why machinery standards and not ISO 26262?

Because a robot that drives itself around a workplace is machinery under Regulation (EU) 2023/1230, not a road
vehicle. The standards are ISO 12100, ISO 3691-4, ISO 13849-1, EN 60204-1, IEC 62443
and ISO/IEC TR 5469. [How we use each standard](How-we-use-each-standard.md) has the mapping.

## What is a Performance Level, and why PL d?

ISO 13849-1's measure of how reliably a safety function performs, PL a to PL e. ISO 3691-4 expects PL d for the
emergency stop and the protective stop of a driverless machine that shares space with people. That is the planning
assumption; whether the lead accepts it, or restricts the robot to a separated area at a lower level, is an open
decision (DQ-005). See the [glossary](Glossary.md).

## Where are the safety functions implemented?

On a hardwired safety chain: E-stops and safety-scanner outputs into a safety relay that drops two contactors and
engages the brakes. The ROS 2 stack and the firmware are hardened as defence in depth but carry no Performance
Level claim in the first safety case. The argument is in
[WP-M-01 §6](../assurance/01-management/WP-M-01-assurance-strategy.md#6-safety-architecture-argument-the-central-strategy).

## Why a fork rather than contributing upstream?

The assurance work needs a record that moves at its own pace, with its own baselines, gates and decision
authority; upstream's contributor agreement transfers rights in contributions; and the fork must be free to say
what the evidence does not support. The lead decided to fork on 2026-10-20 (DQ-001). Upstream's register is quoted,
never restated ([WP-M-10](../assurance/01-management/WP-M-10-upstream-and-supplier-management.md)).

## Where is the Living Safety Case dashboard?

On the README, generated from the records in [`case/`](../assurance/case/README.md) by CI. No number on it is a
safety claim: a claim counts as accepted only when a recorded review accepts it, its evidence is available and
accepted, and no defeater against it is open. Today nothing is accepted and every defeater is open.

## Who decides what?

The project lead is the safety authority and decides risk acceptance, the required PL, robot behaviour defaults,
operating-environment limits, money, hardware, the assessor, roles and gates. Everything else is a technical choice,
recorded so the lead can change it. See [how decisions are made](How-decisions-are-made.md).

## I found a safety problem. Where do I report it?

- A security vulnerability: follow [SECURITY.md](../SECURITY.md).
- A hazard, a near miss or an event: the Safety concern issue template.
- Anything else: the Problem report template. See [reporting a safety concern](Reporting-a-safety-concern.md).

## Why is so much of it written with Claude?

Drafting is done in Claude Code sessions under the project lead's direction; the working rules are in
[CLAUDE.md](../CLAUDE.md). Every change goes through pull request review and the workflows described in
[how the repository is organized](How-the-repository-is-organized.md). The lead holds every safety decision, AI-drafted
work counts at independence level I0, and no work product leaves draft without a review by someone else
([WP-M-02 §3.3](../assurance/01-management/WP-M-02-safety-plan.md#33-ai-assisted-authoring)).

## Something is missing here

Open an [issue](https://github.com/jherrodthomas/openamrobot-assurance/issues). Questions that come up more than
once get added to this page by pull request against [`wiki/`](../wiki/README.md).
