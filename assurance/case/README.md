# Living Safety Case records

This folder will hold the machine-readable records of the Living Safety Case (claims, evidence items, defeaters,
assumptions, configurations, baselines, reviews), the validator and the dashboard generator.

The first record exists: [`baselines/baselines.yaml`](baselines/baselines.yaml) holds BL-001, the upstream Gate A
unit as inherited (commit hashes of the three platform repositories; the tag is local until the proxy allows a push).
Every record uses the same restricted YAML subset: a list of mappings with scalar fields, one `id` per entry, no
anchors or multi-document streams, so one validator can read them all.

Until the rest exists, the safety case is the document [WP-K-01](../10-safety-case/WP-K-01-safety-case.md) and the
README dashboard is not generated. Porting is priority action 11 of the [gap assessment](../00-assessment/gap-assessment.md#10-priority-actions-feed-into-the-g0g1-plan)
and open item OI-1 of [WP-M-01](../01-management/WP-M-01-assurance-strategy.md#10-open-items). The first records will
be GAP-01…GAP-40 as defeaters against the sub-claims G1…G6 of WP-M-01 §3.2.

What the dashboard will guarantee: a claim counts as accepted only when a recorded review accepts
it, every piece of evidence it cites is available and accepted, and no defeater against it is open; a passing CI run
never accepts a claim on its own.
