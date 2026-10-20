# Change impact analysis records

One record per safety-relevant change, in the format [WP-M-11](../../01-management/WP-M-11-impact-analysis.md) sets:
`change-<YYYY-MM-DD>-<slug>.md` with the change, the hazards and safety functions it touches, the work products it
re-opens, the verification done and the residual open items. Required by [WP-P-02](../WP-P-02-change-management.md)
for every change on a path of class SR-A, SR-Q or SR-T in [`safety-relevant-paths.txt`](../safety-relevant-paths.txt).

The next record will be the bench safety hardware of [WP-V-07 §2](../../06-validation/WP-V-07-test-operations.md#2-conditions-before-any-on-ground-test)
(decision DQ-010).

| Record | Change | Status |
|---|---|---|
| [change-2026-10-20-fw-hardening](change-2026-10-20-fw-hardening.md) | Firmware hardening on the fork branch: `/cmd_vel` validation and ceilings, watchdog, encoder-table checks (GAP-06); opens decision DQ-006 on the ceiling | Open: not yet reviewed at I1 |
