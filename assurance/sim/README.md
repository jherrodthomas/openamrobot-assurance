# Simulation track

| Field | Value |
|---|---|
| Scope | Pictures and physics for the review of the risk assessment: scenario tests in Gazebo, Blender for the review pictures, labelled synthetic output with no evidence credit |
| Version | 0.3 (2026-10-27): the first physics layer, [`gazebo/`](gazebo/README.md): six scenario tests in Gazebo Harmonic with upstream's collision monitor, run on the baseline and on upstream main, in CI; two findings under GAP-40. 0.2 (2026-10-21): the 2D views piloted: the warehouse plan and the IS-01 loop of `figures/fig_sim_is.py`, embedded in WP-C-02 and WP-C-06 (ideas-2d-views.md §8 step 1). 0.1 (2026-10-21): the Blender track only: the base from upstream's CAD, the 2.0 mobile manipulator from the OpenArm description package and documented dimensions, eight review scenes with a person |
| Status | Draft. AI-drafted (Claude, AI assistant; I0 under WP-M-02 §3.3); reviewed by the project lead as pictures (2026-10-21). **Synthetic: pictures only, no evidence credit** |
| Feeds | The Gazebo finding under GAP-40 of the [gap assessment](../00-assessment/gap-assessment.md); review of [WP-C-03](../02-concept/WP-C-03-risk-assessment.md), [WP-C-06](../02-concept/WP-C-06-human-robot-interaction-and-misuse.md) and [WP-S-04](../03-system/WP-S-04-response-time-and-stopping-budget.md); one derived planning value (the arm reach, [blender/README.md §4](blender/README.md#4-what-is-real-and-what-is-approximated)); WP-C-02 Figure 2-2 and WP-C-06 Figure 2-2 are drawn by [`figures/fig_sim_is.py`](figures/fig_sim_is.py). Nothing in the safety case |

> **No evidence credit.** Every image and every run under this folder is synthetic. A render shows a situation the
> risk assessment describes; a simulated run shows how the software behaves against a model of the robot, which can
> find a defect but never shows that a measure works on the robot. The measurements that carry evidence are the ones
> of `06-validation/`.

| Path | Content |
|---|---|
| [`blender/`](blender/README.md) | The 3D scenes: STEP tessellation, the OpenArm arms from their description package, the procedural upper body, the warehouse set, the eight review renders and how to regenerate them |
| [`figures/`](figures/fig_sim_is.py) | The 2D views: `fig_sim_is.py` draws the warehouse plan (WP-C-02 Figure 2-2) and one looping top view per interaction scenario (IS-01 so far, WP-C-06 Figure 2-2) from the WP-C-06, WP-S-04, WP-C-02 and WP-C-03 tables; `--check` runs in CI with its self-tests |
| [`gazebo/`](gazebo/README.md) | The scenario tests: the software under test, pinned, in Gazebo Harmonic with Nav2's collision monitor; six scenarios whose checks carry the outcome the record predicts on each target; the results, the image build and the CI job |
| [`ideas-2d-views.md`](ideas-2d-views.md) | Ideation note (Draft, no figures): the 2D views of the hazard situations to complement the 3D scenes, the options weighed, what each is generated from, and the lead's picks of 2026-10-21 |

Not built yet: the other fourteen scenario loops, the tour loop, the six loop diagrams and the side elevation of [`ideas-2d-views.md`](ideas-2d-views.md) §4; the top-down CAD render that replaces the drawn robot footprint; the stopping-distance and field model of WP-S-04 run as a plant with the fault list of WP-V-05; a closed loop with the full navigation stack (planner, controller, costmaps and velocity smoother; the Gazebo scenarios drive the collision monitor directly). Each is a planned layer of the same pattern and is added here when it exists; none is a work product of [WP-M-00](../01-management/WP-M-00-work-product-register.md) until the process model gets an activity for it.
