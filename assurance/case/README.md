# Living Safety Case records

| Field | Value |
|---|---|
| Work product | Living Safety Case data (machine-readable copy of [WP-K-01](../10-safety-case/WP-K-01-safety-case.md)), validator and dashboard generator |
| Standard reference | ISO 13849-1:2023 §10; Regulation (EU) 2023/1230 Annex VII; UL 4600 principles (living safety case, defeaters) |
| Version | 0.1 (2026-10-20): ported from LionDriver `assurance/case` (validator, dashboard, schema, tests); records at BL-001 |
| Status | Draft |
| Author | Assurance team |
| Reviewer(s) | TBD (I1) |
| Baseline | BL-001 |

The folder layout, record format, rules V1–V8 and X3, and the acceptance rule are those of
[LionDriver's `assurance/case/README.md`](https://github.com/jherrodthomas/LionDriver/blob/liondriver-dev/assurance/case/README.md),
which is the reference text. Differences here:

| Folder / file | Content at BL-001 |
|---|---|
| `claims/claims.yaml` | 18 claims: G0 and G1–G4 with sub-claims per safety function, complementary measure, command path and process |
| `arguments/strategies.yaml` | 5 strategies |
| `evidence/evidence.yaml` | 15 evidence items (8 partial, 7 missing) |
| `defeaters/defeaters.yaml` | 40 open defeaters, one per gap-assessment finding |
| `actions/actions.yaml` | 11 open items of WP-K-01 §10 |
| `configurations/` | CFG-001, the Gate A unit; classification `fork-evaluated` |
| `baselines/baselines.yaml` | BL-001 |
| `reviews/reviews.yaml` | none |
| `schema/case-schema.json` | as LionDriver's, with trace prefixes `H`, `HE`, `SF` (hazard log), `AOU` (assumptions), `SR`, `SF`, … (requirements) and classification `fork-evaluated` |
| `tools/` | `validate.py`, `caselib.py`, `generate_dashboard.py`, `test_case.py`, `subsetyaml.py` (the YAML-subset parser, extracted from LionDriver's trace checker); the GSN diagram generator and snapshot builder are not ported yet |

Trace items the validator resolves against live in [`../trace/items/`](../trace/items/): `hazards.yaml`
(H-01…H-12 and SF-01…SF-07 from WP-C-03) and `aou.yaml` (AOU-01…AOU-07 from WP-C-01).

```sh
python3 assurance/case/tools/validate.py
python3 assurance/case/tools/test_case.py
python3 assurance/case/tools/generate_dashboard.py          # writes status.json, badge.json, the SVGs and the README blocks
python3 assurance/case/tools/generate_dashboard.py --check  # CI: fail if any output is stale
```
