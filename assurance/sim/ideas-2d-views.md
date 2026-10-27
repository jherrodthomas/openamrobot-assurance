# 2D views of the hazard situations: options and the lead's picks

| Field | Value |
|---|---|
| Scope | Ideation note for a family of 2D views of the hazard situations, to complement the Blender review scenes of [`blender/`](blender/README.md): which views earn their place, what each is generated from, static or looping, what a view may claim, and which one is built first |
| Version | 0.3 (2026-10-27): §8 steps 2, 4 and 5 built: the CAD sprites (three, pinned by hash, `blender/sprites`), the six loop diagrams (WP-S-04 Figures 2-1 to 2-6, `03-system/figures/fig_s04.py`) and the side elevation in two panels (WP-S-04 Figure 4-2), each 2D figure with a Blender companion render as the lead chose on 2026-10-27; OI-4 closed. 0.2 (2026-10-21): the pilot built on the lead's "go": `figures/fig_sim_is.py`, the warehouse plan as WP-C-02 Figure 2-2 and the IS-01 loop as WP-C-06 Figure 2-2, checked in CI; OI-1 and OI-2 closed. 0.1 (2026-10-21): the options as discussed with the project lead in one session, with mockups shown in chat and the lead's picks |
| Status | Draft. AI-drafted (Claude, AI assistant; I0 under WP-M-02 §3.3). Steps 1, 2, 4 and 5 of §8 are built; steps 3 and 6 are not. **Pictures only, no evidence credit** applies to everything this note proposes |
| Feeds | A later generator under this track; [WP-C-06](../02-concept/WP-C-06-human-robot-interaction-and-misuse.md) §2 and [WP-C-02](../02-concept/WP-C-02-operating-environment-and-tasks.md) §2 as the places the views would be embedded; [WP-S-04](../03-system/WP-S-04-response-time-and-stopping-budget.md) §2 as the place for the loop diagrams. Not a work product of [WP-M-00](../01-management/WP-M-00-work-product-register.md): the generator is a figure source of WP-C-02 and WP-C-06, as their other figure scripts are, listed in the sim README and checked by CI |

## 1. What this note is

The 3D review scenes committed on 2026-10-21 show the robot in its environment as pictures. What they cannot show is
scale, time and the arithmetic of a stop: how long the protective field is and why, how far the person walks while
the robot coasts, where the standstill lands. Vehicle safety records answer that with 2D views drawn from their
tables. This note weighs the same idea for OpenAMRobot and records what the lead chose. Mockups of each candidate were drawn
in the session and shown in chat; they are not committed, and the pilot (§7) reproduces what they showed.

## 2. What the record already draws

| Figure | What it shows | Bearing on the candidates |
|---|---|---|
| WP-C-06 Figure 2-1 | fifteen static scene cards IS-01…IS-15 on a 1 m grid, with the 1.0 m starting field of WP-H-02 §3.3 | the per-situation view replaces it once built: same cards, to scale, with the field set of WP-S-04 and motion |
| WP-C-06 Figure 3-1 | the detection distance L against the coasting time | stays; the loop shows one point of that curve in motion |
| WP-S-04 Figure 4-1 | L against speed for the four planning decelerations | stays |
| WP-C-02 Figure 2-1 | the zone plan Z0…Z5 with the 1.0 m field | the warehouse plan of §4 is its successor: same zones, the real vocabulary of a floor, every field set |
| WP-C-04 Figure 7-1 | response-time bars per safety function, demand to power removal | the loop diagrams of §4 add the standstill and the distance ledger that the bars cannot carry |

Every figure above is drawn by a standard-library Python script with a `--check` mode CI runs, from the tables of the
document it sits in. The views below follow that pattern.

## 3. The candidates and the verdict on each

| Candidate | What it would be | Verdict |
|---|---|---|
| (a) top view per situation | one view per IS-xx, to scale, the field as the sum of its WP-S-04 terms, the person's walk at K = 1.6 m/s, the standstill ghost | **kept**, merged into the per-situation loop of §4 |
| (b) plan of each zone with the field sets | WP-C-02 Figure 2-1 extended with FS-1…FS-4, the blind corner, the dock lane, the station rings | **kept**, merged into the warehouse plan of §4 |
| (c) side elevation | scan plane against a 0.15 m and a 0.30 m carton and a person below the plane; the arm workspace and the lift keep-clear; the 1.7 m envelope | **kept, after the pilot**: one static sheet, the only 2D view with no counterpart today |
| (d) loop diagram per hazardous event | demand, detection, logic, power removal, coast, standstill, with the WP-S-04 times on the arrows and a distance ledger | **kept**: one per field-sizing path of WP-S-04 §2 (SF-02 scanner, SF-02 bumper, SF-03, SF-04 fault path, SF-11, SF-12), six, in WP-S-04 |
| (e) review dashboard | the 3D render, a top view, the WP-C-03 rating and the WP-C-05 allocation on one frame | **deferred** to the physics layer (blender README OI-4): without a plant run it composes what the other views already show |
| factory-floor top view (the lead's addition) | the robot on a warehouse plan with its fields, zones and the situations where they happen, the way a known-scenario loop puts a vehicle on its road | **this is the family**: §4 |

Two things the mockups settled on the way. A straightened aisle with the robot held in place, the road
device of the vehicle loops, is wrong here: at 0.20 m/s the robot moves 0.26 m over a whole loop while the person walks 2 m, so the
view is a fixed crop of the plan with the robot moving through it. And the plan is drawn in the vocabulary of a
warehouse seen from above (rack rows with hazard striping, a dashed lane grid, pallets and cartons, an office, a
truck loading dock, people as small figures), not in the schematic of WP-C-02 Figure 2-1; the zones of the record
are mapped onto that floor, so the loading dock reads as Z0 (no dock edges, WP-C-02 §5) and the office and visitor
route as Z5 (excluded, DQ-019).

## 4. The agreed family

| View | Form | Where it lives |
|---|---|---|
| **The warehouse plan** | one still of a typical site: the five zones, the rack rows and aisles, the station bay with the SR-11.02 workspace ring and the SR-12.03 keep-clear, the dock lane with the robot's dock and the undock reverse, the charging bay, the loading dock and the office; the robot on it with every WP-S-04 field set at its planning length; hazard chips naming the hazard, the situation and the PLr adopted | WP-C-02 §2 as the successor of Figure 2-1; the sim README |
| **The per-situation loops** | one looping view per IS-01…IS-15: a fixed crop of the plan around the event, about 6 × 3.6 m; the robot sprite moving at the zone speed with the field set that applies drawn as the sum of its terms; the person on their path at K; the field outline changing state at the demand and at power removal; an event row that lights up; a time strip with a cursor; a plot of the person-to-robot distance with the field edge marked. The three with no motion (IS-07, IS-08, IS-11) are stills | WP-C-06 §2, replacing Figure 2-1; listed in the sim README |
| **The tour loop** | the robot driving the plan's route, the field set switching at each zone boundary, each situation playing as it is reached | the sim README, later, from the same generator |
| **The loop diagrams** | six, one per field-sizing path of WP-S-04 §2, each with the distance ledger that makes the field length; beside each, a render of the standstill moment from the Blender track (the lead's pick of 2026-10-27: companions, the 2D figure stays the checked one) | WP-S-04 §2.1, Figures 2-1 to 2-6 (built) |
| **The side elevation** | one static sheet, two panels (the scan plane against low objects; the CFG-002 envelope, workspace and keep-clear), with an orthographic render of each panel beside it, the heights drawn on | WP-S-04 §4.2, Figure 4-2 (built) |

**The sprite.** No free top-down sprite of an AMR exists (the CC0 packs found are cars, tanks and side-view pixel
robots; the warehouse vectors found are stock art under attribution licences). The robot is therefore its own CAD:
the Blender pipeline's existing `top` camera made orthographic, rendered with a transparent background at a fixed
pixels-per-metre, one PNG per configuration and pose (CFG-001; CFG-002 stowed and carry), pinned by hash like
a sprite sheet, and embedded by the SVG. A drawn footprint of the same shape (white deck, dark
bumper ends, two drive wheels, three castors, the scanner dot at the front) is the fallback when Blender is absent,
and is what the mockups used. Built in v0.3: `blender/sprites/` holds the three files at 250 px/m with a sidecar
giving the base's centre; `fig_sim_is.py` embeds them as data URIs and fails `--check` when a file's SHA-256 differs
from its pin.

## 5. What each view is generated from

Everything written on a view comes from a table of the record; the generator fails in CI if a row is gone or a
number disagrees with the formula, as `fig_s04.py` does today.

| Content | Source table |
|---|---|
| scenario ID, who, zone, task, what the person does, closest distance, hazard, measure | WP-C-06 §2 |
| K, t_r, Z, C | WP-C-06 §3 parameter table; WP-S-04 §1 |
| stage times per path, t_r per safety function | WP-S-04 §2 |
| speed, deceleration case, t_b, d_s, L per field set | WP-S-04 §3.2 and §4.1, recomputed from L = v·t_r + d_b + K·(t_r + t_b) + Z + C |
| workspace ring, lift keep-clear | WP-S-04 §4.5; WP-S-02 SR-11.02, SR-12.03 |
| zones, people class, speed limit, dock lane length, aisle width | WP-C-02 §2 |
| rating per rated row (S, F, P, PLr adopted) for the hazard chips | WP-C-03 §5 |

The scene geometry per situation (the robot's pose and route in the crop, the person's path, the props) lives as a
spec in the generator script, as `fig_c06.py` keeps the pictogram of each card today, and is checked against the
scenario IDs of WP-C-06 §2. No scenes.yaml is introduced now; see §9 for the alternative the lead can return to.

The plan geometry is the generator's own: a fictional but typical site, with the sizes WP-C-02 §2 states where it
states them (dock lane 2 m plus the robot's length; aisle width at least the footprint plus 0.5 m each side) and the
rest chosen to be ordinary. It is replaced by the surveyed site when WP-O-01 records one (OI-3).

## 6. Static or looping, and where embedded

- The per-situation loops are SMIL animations in SVG, no script: they play
  in a browser and in GitHub's markdown preview, and a viewer that shows the SVG as a still shows the first frame
  (t = −0.5 s, the robot driving and the person approaching). The mockup of IS-01 was 15 KB.
- The warehouse plan, the loop diagrams and the side elevation are static SVG.
- Embedding: the loops in WP-C-06 §2 where Figure 2-1 is now, the plan in WP-C-02 §2, the loop diagrams in WP-S-04
  §2, and every loop listed in the sim README with one line each. The wiki links to them and never embeds a figure
  that touches safety content (wiki README).

## 7. What a view may claim

Nothing. A loop shows a situation the risk assessment describes; it does not show that a measure works, and no
number on it is measured. Every view carries the band the Blender renders carry, in its own drawing and in its
caption: *drawn to WP-S-04 v0.1 planning values; the coast is unmeasured (WP-V-02); synthetic, no evidence
credit*. Where a loop prints a derived quantity (the closest approach in the planning case came out at 0.72 m for
IS-01 in the mockup), the caption says it is the planning case and names the term that is unmeasured. The
decelerations stay the three planning cases of WP-S-04 §3.1 until WP-V-02 replaces them, and the generator then
redraws every view from the measured value.

## 8. Order of work

1. **Pilot (built 2026-10-21, v0.2):** the IS-01 crop as a loop and the warehouse plan as a still, both with the drawn stand-in sprite, so the
   family is judged before any Blender time is spent. The pilot must show: the field as the sum of its terms with
   the coast hatched as unmeasured; the person's 0.91 m walk and the robot's 0.11 m; the outline changing at the
   demand and at power removal; the event row, the time strip and the distance plot; the band of §7.
2. **Built 2026-10-27:** the CAD sprite rendered and swapped in; the generator keeps the fallback.
3. The other fourteen situations; Figure 2-1 of WP-C-06 retired.
4. **Built 2026-10-27:** the six loop diagrams in WP-S-04 §2.1, each with its render of the standstill moment.
5. **Built 2026-10-27:** the side elevation sheet in WP-S-04 §4.2, two panels, each with its orthographic render.
6. The tour loop; the dashboard when the physics layer exists.

Before step 1 is committed: the generator goes into WP-M-00 as a work product or as a figure source of the work
products it serves, with the document-control header; CONTRIBUTING.md gets its `--check` line; the sim README
lists it (OI-1).

## 9. The lead's picks

Taken on 2026-10-21 in chat. The lead answered the closing set of questions with "ok" on the recommendations; each
pick below is the recommended option and can be overturned by a line in this table.

| Question | Options offered (recommendation first) | Pick |
|---|---|---|
| Which views | the factory-floor family (plan still plus per-situation loops) with (c) after and (d) kept; or the five candidates as separate figures | the family; (d) kept at the lead's request; (c) after the pilot; (e) deferred |
| The robot on the view | the CAD rendered top-down as the sprite, drawn footprint as fallback; drawn footprint only; a recoloured stock vehicle | CAD sprite with the fallback |
| What the loop diagrams cover | the six field-sizing paths, in WP-S-04; one per rated row of WP-C-03 §5, in the sim README; both | the six paths |
| The plan geometry | a fictional typical site now, sizes from WP-C-02 §2 where stated; wait for the WP-O-01 survey | fictional typical site now |
| Pilot | the IS-01 crop as a loop plus the plan still, drawn stand-in, then the sprite; the sprite first; a loop diagram first | IS-01 crop plus the plan still |
| Scene description | the existing tables plus the scene spec in the script; a scenes.yaml per situation in reBot-DevArm's schema | tables plus spec in the script |
| Format and embedding | SMIL loops in the work product with a still first frame; static only; loops in the sim README only | SMIL loops in the work product |

## 10. Sources

- This record: WP-C-02 §2 and Figure 2-1; WP-C-03 §3, §4, §5; WP-C-05 §5; WP-C-06 §2, §3 and Figures 2-1, 3-1,
  5-1; WP-S-04 §1 to §5 and Figure 4-1; WP-C-04 Figure 7-1; WP-S-02 SR-02.03, SR-11.02, SR-12.03;
  `blender/README.md` (the renders, the rule that pictures earn no evidence credit, the overlap check, OI-1 to OI-4).
- A message relayed from the reBot-DevArm session (2026-10-21, information to weigh, not adopted): its
  `assurance/sim/` pipeline on branch `claude/dreamy-feynman-ljvcno` of jherrodthomas/reBot-DevArm has a
  scenes.yaml to scene.json exporter with a CI test needing only PyYAML and numpy, an HTML dashboard composer
  screenshotted with headless Chromium, and a CC0 Quaternius figure with hand IK that gives a reaching pose
  (bearing on `blender/README.md` OI-1). It was not cloned or read in this session.
- Asset search: no CC0 top-down AMR or warehouse set exists; the hits were Kenney's cars and tanks, side-view pixel
  robots on OpenGameArt, and stock warehouse vectors under attribution licences.

## 11. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | ~~Register the generator before the pilot is committed~~ done in v0.2: `figures/fig_sim_is.py` is a figure source of WP-C-02 (Figure 2-2) and WP-C-06 (Figure 2-2), listed in the sim README, with its `--check` and self-tests in CONTRIBUTING.md and CI | closed | — |
| OI-2 | ~~The session's mockups are not committed; the pilot reproduces the plan and the IS-01 loop from the tables~~ done in v0.2; the loop-diagram, side-elevation and dashboard mockups stay uncommitted until their steps of §8 | closed | — |
| OI-3 | Replace the fictional site with the surveyed one when WP-O-01 records it; the aisle width and dock-lane length stay **(TBC)** against WP-C-02 §2 until then | Assurance team | with WP-O-01 |
| OI-4 | ~~The CAD sprite needs the Blender environment of `blender/README.md` §2; render CFG-001 and CFG-002 (stowed, carry) orthographic top-down, transparent, at a fixed scale, and pin the files~~ done in v0.3 (`blender/sprites`, pinned in `fig_sim_is.py`) | closed | — |
| OI-5 | Decide whether the reBot-DevArm scenes.yaml schema is adopted when the tour loop or the dashboard is built, so that the 2D views and the Blender scenes share one description | Project lead | when the tour loop is scheduled |
