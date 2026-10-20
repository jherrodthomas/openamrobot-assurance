# WP-M-09 Machine-learning safety plan

| Field | Value |
|---|---|
| Work product | WP-M-09 Machine-learning safety plan |
| Standard reference | Other: TR 5469 (AI technology classes, usage levels); AI Act Art. 9; ASPICE: MLE.1–4 |
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

How learned components (a future navigation or manipulation policy, perception models) are managed so that none carries a safety function, and what evidence the fork keeps about them under ISO/IEC TR 5469 and, if the threshold of WP-M-13 §5 is ever crossed, the AI Act.

## 2. Position

No safety function is allocated to a learned component (WP-M-01 T-03). Every learned output passes the same checker as any other command. This plan keeps that true and documents it.

## 3. Classification under ISO/IEC TR 5469

Each learned component gets an AI technology class and a usage level; the target is usage outside the safety function, with the chain as the independent safeguard. Recorded in [WP-C-09](../02-concept/WP-C-09-ml-component-definition-and-safety-requirements.md).

## 4. Activities by gate

G1 classification and requirements (WP-C-09) and the insufficiency analysis (WP-C-10); G3 ML engineering evidence (WP-W-10); G5 the AI Act record (WP-K-07).

## 5. Roles

| Role | Holder (today) | Duty |
|---|---|---|
| ML safety lead | Jherrod Thomas (acting); permanent holder TBD | Owns this plan and WP-C-09 |
| External ML reviewer | TBD (may be the FS assessor) | ML-R1…ML-R3 (WP-M-06 §7) |

## 6. Upstream

Upstream's embodied-AI repositories (`openamrobot-embodied-ai`) were not reviewed in the gap assessment; the first task is to find out what learned components exist in the inherited stack.

## 7. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | Write the content; the sections above are the clause map and the seed from the gap assessment | Safety manager | G0 |
