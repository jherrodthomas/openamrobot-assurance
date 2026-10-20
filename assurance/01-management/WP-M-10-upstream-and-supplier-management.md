# WP-M-10 Upstream

| Field | Value |
|---|---|
| Work product | WP-M-10 Upstream (Botshare) and supplier management |
| Standard reference | SRP/CS: 61508-1 §6.2 (subcontracted activities); IEC 62443: 62443-4-1 SM-9, SM-10; ASPICE: ACQ.4 |
| Version | 0.0 (skeleton: structure and clause map; 2026-10-20) |
| Status | Skeleton |
| PL / scope | All |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Approver | Safety manager |
| Baseline | `726046e` |

> [!NOTE]
> **Skeleton.** The structure and clause mapping exist; the content is still to be written. The gate that needs this
> work product is **G0** ([WP-M-00](WP-M-00-work-product-register.md#3-register)).

## 1. Purpose

How upstream OpenAMRobot (Botshare LTD) and the suppliers of safety components are managed: what the fork takes from upstream and when, how changes arrive, and what evidence suppliers must provide.

## 2. Upstream relationship

Botshare is a supplier under no contract (WP-M-01 T-08). The fork reads `openAMRobot/.github/decisions.yaml` as upstream's register of approved values and quotes it; the fork's own decisions live in the decision register. Forks must not imply Botshare's endorsement (upstream `GOVERNANCE.md`).

## 3. What is tracked

The three platform repositories (`openamr-platform-sw`, `-hw`, `-fw`), the release manifest, the linorobot2 firmware base, upstream's plan-set documents P-03, E-01 and B-02 (not public, GAP-33), the 2.0 milestones.

## 4. Synchronisation procedure

Upstream is merged at tagged points only, each with an impact analysis under WP-M-11 and a change record; the pins are moved in one pull request with the record.

## 5. Suppliers of safety components

Safety relay, contactors, scanner, brakes, E-stop devices: certificate, declaration of conformity, reliability data (B10D or MTTFD), manual with the fault exclusions the manufacturer allows. Collected in WP-H-07.

## 6. Open requests to upstream

P-03, E-01, B-02; the ZBLD.C20 manual; confirmation of the A1 LiDAR model; the deployed firmware's source (GAP-32).

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
