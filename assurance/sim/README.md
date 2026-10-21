# Simulation track

| Field | Value |
|---|---|
| Scope | Pictures and, later, physics for the review of the risk assessment: physics in a scriptable engine, Blender for the review pictures, labelled synthetic output with no evidence credit |
| Version | 0.1 (2026-10-21): the Blender track only: the base from upstream's CAD, the 2.0 mobile manipulator from the OpenArm description package and documented dimensions, eight review scenes with a person |
| Status | Draft. AI-drafted (Claude, AI assistant; I0 under WP-M-02 §3.3); reviewed by the project lead as pictures (2026-10-21). **Synthetic: pictures only, no evidence credit** |
| Feeds | Review of [WP-C-03](../02-concept/WP-C-03-risk-assessment.md), [WP-C-06](../02-concept/WP-C-06-human-robot-interaction-and-misuse.md) and [WP-S-04](../03-system/WP-S-04-response-time-and-stopping-budget.md); one derived planning value (the arm reach, [blender/README.md §4](blender/README.md#4-what-is-real-and-what-is-approximated)). Nothing in the safety case |

> **Pictures only.** Every image under this folder is synthetic and earns no evidence credit. A render shows a
> situation the risk assessment describes; it does not show that a measure works. The measurements that carry
> evidence are the ones of `06-validation/`.

| Path | Content |
|---|---|
| [`blender/`](blender/README.md) | The 3D scenes: STEP tessellation, the OpenArm arms from their description package, the procedural upper body, the warehouse set, the eight review renders and how to regenerate them |

Not built yet: a physics layer (the stopping-distance and field model of WP-S-04 run as a plant with the fault list of WP-V-05), known scenarios as scripted runs, a closed loop with the navigation stack. Each is a planned layer of the same pattern and is added here when it exists; none is a work product of [WP-M-00](../01-management/WP-M-00-work-product-register.md) until the process model gets an activity for it.
