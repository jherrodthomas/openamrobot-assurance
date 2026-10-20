# WP-H-02 Electrical and Safety-Chain Design

| Field | Value |
|---|---|
| Work product | WP-H-02 Electrical and safety-chain design (schematics, wiring, enclosure): the Gate A bench chain as the first version (the chain WP-V-07 validates), the 2.0 chain as the target |
| Standard reference | ISO 13849-1:2023 §6 (Category 3 designated architecture), §6.1.4, Annex C (MTTFd), Annex E (DC), Annex F (CCF); ISO 13849-2:2012 Annex D; EN 60204-1:2018 §9.2, §9.4, §13; ISO 13850:2015; IEC 60947-5-5; IEC 61496-1/-3 (ESPE, AOPD); ISO 13856-3 (pressure-sensitive bumpers) |
| Version | 0.1 (2026-10-20): bench-build design from WP-S-03 v0.2 and DQ-007. 0.0: skeleton |
| Status | Draft |
| PL / scope | PL d; Gate A unit (CFG-001) bench build |
| Author | Assurance team (AI-assisted draft, I0) |
| Reviewer(s) | TBD (I1, electrical; checks every part against its datasheet before anything is ordered) |
| Approver | Safety manager |
| Baseline | BL-001; WP-S-02 v0.1; WP-S-03 v0.2 |

> [!WARNING]
> Draft design. Part numbers are **candidates** chosen for class, certification and availability; the electrical
> reviewer confirms each against its datasheet and the ZBLD.C20 driver manual (not in the repository, WP-S-03
> OI-1) before purchase. Prices are list-price estimates for one unit in October 2026 and will differ. Nothing
> has been wired. MTTFd, DCavg and CCF are estimated from catalogue B10d values and must be recalculated in
> WP-H-03 with the final parts.
>
> **DQ-011 answered C (2026-10-20):** the bench safety hardware is not bought for the Gate A unit and no on-ground
> test runs until the 2.0 base with its chain exists. This design is kept as the first draft of that chain, its
> parts list is a budget, not an order, and the bench-build evidence it was to produce (stopping distance, field
> sizes, fault injection) waits for 2.0 (DQ-020).

## 1. What this build is for

The Gate A unit is upstream's test robot: a Pi 5, a Teensy 4.0 and two ZBLD-driven BLDC wheels. It will be
replaced by 2.0 (STM32, hub motors, Pilz chain). The bench build adds to it the minimum safety chain that lets
the fork test its firmware, its navigation stack and its validation procedures **with people in the room**, at
PL d for the stop functions, and that produces evidence (stopping distance, field sizes, fault-injection
results) that carries over to 2.0. It is not a product design; it is the test fixture the safety case needs.

## 2. Parts list (E-numbers from WP-S-03 §2)

| E | Item | Candidate part | Qty | Safety data to confirm | Estimate (EUR) |
|---|---|---|---|---|---|
| E1 | Emergency-stop device, 2 NC, positive opening, twist release, Ø22 | Schneider XB4BS8445 (1 NC) + ZBE-102 (second NC block), yellow legend plate ZBY9330 | 2 | IEC 60947-5-5, B10d from Schneider (typ. 100,000 ops) | 2 × 45 |
| E2 | Safety relay, dual-channel, cross-monitored, monitored manual reset, EDM | Pilz PNOZ s3 24 V DC (750103) (3 safety contacts, 1 aux) or PNOZ s4 (750104, 3 NO + 1 NC, more inputs) | 1 | PL e, Cat 4 capable; B10d 20 × 10⁶ (DC-13 load dependent) | 220 (s3) / 260 (s4) |
| E3 | Contactors for traction supply, 24 V DC coil, NO main contact, mechanically linked NC mirror contact | Schneider LC1D09BD + LADN11 mirror block (9 A AC-3; DC-1 rating to check: traction peak ≤ 2 × 7.5 A) or Finder 22.32 power relay with forcibly guided contacts | 2 | mirror contact per IEC 60947-4-1 Annex F; B10d 1.3 × 10⁶ | 2 × 30 |
| E4 | Second shut-off path: driver `BRK/DI5` on both drivers driven from an E2 safety contact | wiring only; semantics from the ZBLD.C20 manual (OI-1) | — | input type NPN, COM reference | 0 |
| E5a | Safety laser scanner, type 3 (IEC 61496-3), PL d, two OSSD outputs, ≥ 2 m protective field, field switching | SICK nanoScan3 Core I/O (1090 series, 3 m protective field, 275°) or SICK TiM-S (781S-2174104, 2 m protective field, 270°) | 1 | OSSD 2 × PNP 24 V, response time 70–100 ms, field sets via static inputs | 2,200 (nanoScan3 Core) / 1,500 (TiM-S) |
| E5b | Rear safety bumper, pressure-sensitive edge with monitoring unit, PL d (ISO 13856-3) | Mayser SL/BK edge profile (≈ 600 mm) with Mayser SG-EFS 104 ZK2/1 monitoring unit, or ASO SENTIR edge with ELMON relay 31-xxx | 1 set | monitoring unit output 2 × safety contacts; edge 8.2 kΩ terminated | 350 |
| E6 | Speed monitor, independent of the Teensy | **Option 1 (recommended):** Pilz PNOZ s30 (750330) safety speed monitor, 2 pulse inputs (driver `SPD/DO2` of both wheels), PL e, configurable limits and direction. **Option 2:** small safety PLC (Pilz PNOZmulti 2 or SICK Flexi Classic) that also takes E1, E5a, E5b and does field switching | 1 | pulse spec of `SPD/DO2` (pulses per revolution, level) to confirm (OI-1) | 650 (s30) / 900+ (safety PLC) |
| E7 | Reset button with lamp, and a stack light | Schneider XB4BW36B5 (reset, blue illuminated, 1 NO + 1 NC); Patlite LR4 or similar 3-colour stack light 24 V | 1 + 1 | — | 40 + 90 |
| E8 | Teensy diagnostic inputs (opto-isolated) and one demand output | 4-channel 24 V → 3.3 V opto-isolator board (e.g. PC817-based); one NPN transistor output to an E2 input via a 24 V relay | 1 | 3.3 V logic, not 5 V tolerant | 15 |
| E10 | Battery-voltage monitoring relay with hysteresis | Finder 71.11 DC undervoltage relay (24 V, adjustable threshold) or a comparator board into E2 | 1 | threshold 22–23 V (TBC) | 60 |
| E11 | Main fuse and lockable disconnect (DM-04) | 20 A blade/ATO or 25 A MIDI fuse in a holder on battery +; Blue Sea 6006 (or any 48 V 100 A) battery switch with lock-out | 1 + 1 | fuse above stall current, below cable rating (hw `power.md` says 15–20 A) | 15 + 35 |
| — | Enclosure, DIN rail, terminals, 24 V DC-13 wiring (0.75 mm²), cable glands, labels | — | — | EN 60204-1 §13 | 120 |
| | **Total, recommended options (nanoScan3 Core, PNOZ s3, PNOZ s30)** | | | | **≈ 4,100** |
| | **Total, budget options (TiM-S, PNOZ s3, PNOZ s30)** | | | | **≈ 3,400** |

The scanner and the speed monitor are two thirds of the cost. The register question DQ-007 assumed a scanner
in the €2,000–4,000 class; the TiM-S fits the Gate A speed (0.20 m/s, 2 m field is ample) and halves it.

## 3. Architecture and wiring

### 3.1 Signal chain (Category 3)

```
                 ┌────────────────────────────────────── 24 V logic (from a fused 24 V branch, NOT the traction branch)
                 │
 E1a ──┬── S11/S12 ──┐
 E1b ──┘  (ch 1)     │   E2  PNOZ s3                     ┌── K1 coil ──┐
 E1a ──┬── S21/S22 ──┤   S11/S12 = ch 1 (E-stops)        │             │   traction 24 V ── F0 20 A ── DISCONNECT ──┐
 E1b ──┘  (ch 2)     │   S21/S22 = ch 2 (E-stops)        │             │                                            │
                     │                                   ├─ 13/14 ─────┤   K1 NO ─── K2 NO ─────────────────────────┴── V+ driver L, V+ driver R
 E5a OSSD1 ──► E6 ──►│   (E6 enables E2 only when       ├─ 23/24 ─────┴── K2 coil
 E5a OSSD2 ──► E6 ──►│    speed OK AND scanner OK        │
 E5b safety outputs ►│    AND bumper OK: E6 Y-outputs    ├─ 33/34 ──────── BRK/DI5 driver L and driver R   [second shut-off path]
   (via E6 inputs)   │    into E2 S11/S21 in series      │
                     │    with the E-stops)              ├─ 41/42 (aux NC) ─ E8 Teensy input "chain tripped"
 E7 reset ──────────►│   S34 (monitored reset)           │
 K1 mirror NC ──┐    │                                   │
 K2 mirror NC ──┴───►│   Y1/Y2 (EDM feedback loop)       │
 E10 undervoltage ──►│   in series with the E-stop ch    └─ A1/A2 24 V
 E8 Teensy demand ──►│   (optional demand, via relay)
```

- The PNOZ s3 has one reset input and a fixed two-channel input; the scanner, bumper and speed monitor are
  therefore combined in **E6** (the PNOZ s30 has safe inputs for OSSD pairs and safe outputs) and E6's enabling
  outputs are wired in series with the E-stop channels into E2. If the reviewer prefers one device for all inputs,
  Option 2 (a small safety PLC) replaces E2 and E6 together and takes E1, E5a, E5b, E7 and E10 directly.
- Two traction-power interruptions in series (K1, K2) plus the driver brake/inhibit input as a diverse second
  path meet Category 3 with a single fault not losing the function.
- The K1 and K2 mirror contacts are in the E2 feedback loop (EDM): a welded contactor blocks the reset.

### 3.2 Response time budget (SR-01.03: ≤ 200 ms to power removal)

| Stage | Typical | Source to confirm |
|---|---|---|
| E1 contact opening | 0 ms (mechanical) | — |
| E2 PNOZ s3 drop-out on input open | ≤ 30 ms | datasheet |
| K1/K2 opening | ≤ 20 ms (DC coil, no suppression delay beyond a diode; use a varistor, not a plain diode, to keep drop-out fast) | datasheet |
| **Total E-stop** | **≤ 50 ms** | |
| E5a scanner response (nanoScan3: 70 ms at 2 scans; TiM-S: 100 ms) | 70–100 ms | datasheet |
| E6 PNOZ s30 reaction to a safe input | ≤ 20 ms | datasheet |
| E2 + K1/K2 as above | ≤ 50 ms | |
| **Total protective stop (SF-02)** | **≤ 170 ms** | |

At 0.20 m/s the reaction distance is 0.034 m; the coasting distance after power removal (category 0, no brake
on Gate A) is unmeasured (WP-C-01 OI-2) and dominates the field size.

### 3.3 Protective field (SR-02.02), to be computed after the stopping test

`L_field = v × t_reaction + d_stop(v) + margin`. With `v = 0.20 m/s`, `t_reaction = 0.17 s`, `d_stop` **(TBC,
measured)** and a 0.10 m margin, a coasting distance of 0.3 m would give a field of about 0.45 m ahead of the
scanner window; a field of 1.0 m is proposed as the starting configuration until the measurement exists.
Two field sets: **navigation** (1.0 m) and **dock lane / crawl** (0.3 m at ≤ 0.05 m/s), selected by E6 from the
speed-limit selection input, never from the ROS 2 stack.

### 3.4 Rear bumper (SR-02.04)

A 600 mm pressure-sensitive edge across the rear panel at 150 mm height, with the monitoring unit's two safety
outputs into E6. Reverse is permitted only at the crawl limit (E6 direction + speed check); the Nav2 `backup`
recovery is disabled in the fork configuration (GAP-35) and undock uses the crawl speed.

### 3.5 Teensy I/O (E8) and firmware

| Signal | Direction | Pin (proposed, free on the overlay pin map) | Use |
|---|---|---|---|
| chain tripped (E2 aux NC) | in | 24 (via opto) | `/firmware/status` `chain=0/1`; inhibits closed-loop drive in software as a functional measure |
| reset required (E7 lamp line) | in | 25 (via opto) | status |
| bench-arming key switch | in | 26 (via opto) | SR-07.03 |
| battery undervoltage (E10 aux) | in | 27 (via opto) | status; SR-06.05 |
| demand (watchdog/stall fault) | out | 28 (transistor to a 24 V relay into an E6 input) | optional additional demand |

Diagnostic signals from the chain to the firmware are informative only: these are reporting and functional inputs, and the chain does not depend on them (WP-S-03 §2 rule). Firmware changes
for them are a follow-up change record.

### 3.6 Power (DM-04, DM-06)

Battery + → F0 (20 A) → lockable disconnect → traction branch (K1, K2, drivers) and a separately fused 3 A
logic branch (E2, E6, scanner, bumper monitor, stack light, Pi buck). The mains converter is **not** paralleled
with the battery any more: it charges the battery through the disconnect only while the disconnect is in the
charge position (or through a charge relay whose NC contact opens the E2 supply, as upstream decided for 2.0).

## 4. Estimated PL (to be recalculated in WP-H-03)

| Function | Category | MTTFd (channel) | DCavg | CCF | PL estimate |
|---|---|---|---|---|---|
| SF-01 | 3 | high (E1 B10d 10⁵ at 10 ops/day → > 100 a; E2 PL e; K1/K2 B10d 1.3 × 10⁶ at 100 ops/day → 36 a each, high) | medium–high (EDM on contactors, cross-monitoring on inputs, direct opening on E1) | ≥ 65 (separation, diverse shut-off path, FMEA) | **d** |
| SF-02 | 3 | high (scanner PL d type 3; monitoring unit PL d; E2, K1/K2 as above) | medium–high | ≥ 65 | **d** |
| SF-03 | 3 (two pulse sources: driver `SPD/DO2` and, via E8, the Teensy's encoder-derived output as a diagnostic cross-check) or 2 (single source with the monitor's own test) | high (PNOZ s30 PL e) | medium (single pulse source) to high | ≥ 65 | **d** (Cat 3) or **c** (Cat 2); confirm with OI-1 |

## 5. Validation hooks (feeds WP-V-01)

Every item of WP-S-02 §11 can be exercised on this build: each E-stop and each channel opened separately, a
welded-contactor simulation (bridge K1's main contact and attempt a reset), reset held, OSSD line open, bumper
pressed, pulse line disconnected, overspeed by a forced command above the limit (bench image), undervoltage by
a bench supply, and the stopping-distance measurement that sizes the field.

## 6. Open items

| ID | Item | Blocks |
|---|---|---|
| OI-1 | ZBLD.C20 manual: `BRK/DI5` semantics and polarity, `SPD/DO2` pulse spec, `ERR/DO1` polarity, DC-1 contactor rating against driver inrush | §2 E3, E4, E6 |
| OI-2 | Choose Option 1 (PNOZ s3 + s30) or Option 2 (safety PLC); reviewer's call on wiring simplicity | §3.1 |
| OI-3 | Scanner choice between nanoScan3 Core and TiM-S after checking mounting height and the chassis lip; both need a window ≥ 60 mm above the floor and clear of the castor swivel | §2 E5a |
| OI-4 | Stopping-distance measurement (WP-C-01 OI-2) to size the fields | §3.3 |
| OI-5 | Charge path redesign (DM-06): charge relay or disconnect position | §3.6 |
| OI-6 | WP-H-03: MTTFd, DCavg, CCF with the final parts and the SISTEMA library entries | §4 |


## 7. Still to write (skeleton sections of v0.0)

- Schematics and panel layout as drawings (§3 is the signal chain in text).
- Wire gauges, colours, connectors, routing, strain relief, labelling, enclosure IP rating (EN 60204-1 §13).
- Certificate references per safety component (WP-H-07) once parts are confirmed.
- The 2.0 chain as the target design, from upstream's register entries, once its documents are public.
