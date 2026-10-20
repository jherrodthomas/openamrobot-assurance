# Security Policy

OpenAMRobot assurance is the safety-assurance record for a fork of the OpenAMRobot mobile manipulator. A
security problem in the robot's software can move a machine around people, so please report it privately.

## Reporting a vulnerability

- Use GitHub private vulnerability reporting on this repository: **Security** tab → **Report a vulnerability**
  (or [open a report directly](https://github.com/jherrodthomas/openamrobot-assurance/security/advisories/new)).
- Do not open public issues, pull requests or discussions for security problems.

Please include the affected repository and commit (this record, or one of the forked platform repositories), the
robot configuration, a description of the issue and its impact, and how you found it. Proof-of-concept material is
welcome but not required. Do not send personal data of other people.

### What to expect

- Acknowledgement within 3 working days.
- Initial assessment within 5 working days (2 if the issue could move the robot or defeat a stop).
- If the issue can affect safety, we may say to stop driving the robot before a fix is ready. Such notices contain
  no technical detail.
- We aim to release a fix and publish an advisory within 90 days, and we coordinate disclosure timing with you. We
  credit reporters who wish to be credited.

### Scope

In scope: this repository and the fork's platform repositories (`openamr-platform-sw`, `-hw`, `-fw` under the
fork), the fork's firmware and container builds, and the fork's update and release process.

Out of scope here: upstream OpenAMRobot (Botshare LTD), ROS 2 and Nav2, and third-party services. Report those to
their owners; upstream's policy is in the `openAMRobot/.github` repository. If you are unsure, report to us and we
will route it.

### Testing rules

Test only on equipment you own or are authorised to test. Never test on a robot with people in its operating area.
Do not access other people's devices, networks or accounts, and do not attack upstream or third-party
infrastructure.

### Supported releases

The fork publishes no release yet. When it does, only the latest release receives security fixes.

The process behind this policy is [WP-O-05](assurance/09-production-operation/WP-O-05-cybersecurity-incident-response-updates.md);
the cybersecurity plan is [WP-M-08](assurance/01-management/WP-M-08-cybersecurity-plan.md).

## Cybersecurity engineering under IEC 62443

Cybersecurity is treated as an engineering discipline alongside machinery safety, not only as vulnerability
intake. The fork follows IEC 62443-4-1 (secure product development lifecycle) and IEC 62443-4-2 (component
requirements) with a security level target decided by the project lead. The known starting position, from the
[gap assessment](assurance/00-assessment/gap-assessment.md): anyone on the ROS 2 domain can move the robot or retune
it (GAP-27), the on-screen E-stop is a network request (GAP-28), and the supply chain is unpinned (GAP-29).
Threats that can cause a hazard are rated against the hazard list, and the hardwired safety chain is designed as a
zone with no conduit from the network, so that no attack on the software can hold a contactor closed.
