# Working with the project lead

OpenAMRobot assurance is the safety-assurance record for a fork of the OpenAMRobot mobile manipulator platform,
built the way LionDriver's is. The project lead is its safety authority and often reviews from a phone. Keep the
decisions asked of them few, and make each one quick to answer.

## Decisions

Every question for the lead lives in the decision register,
[`assurance/01-management/decisions/register.yaml`](assurance/01-management/decisions/register.yaml). Its
[README](assurance/01-management/decisions/README.md) has the lifecycle and the inbox page it builds.

1. **Sort before asking.** Ask the lead only what they alone can decide: risk acceptance, Performance Level or
   hazard scope, robot behaviour defaults, operating-environment limits, money or hardware, the assessor, roles and
   independence, gate go/no-go. A reversible technical choice gets `decider: claude`: go with the recommendation
   and say so. A task is not a decision; it stays in its work product.
2. **Every question stands on its own.** Never send a bare ID ("decide F-3"). An entry has the question in plain
   words, two or three lines on what is at stake, two to four options with what each does and costs, the
   recommendation first, how hard it is to undo, what it blocks, and its sources. Add one picture when it shows the
   difference between the options; skip it when it would only decorate.
3. **Batches of ten.** Keep about ten questions open, those that unblock the most. When the lead has answered a
   batch, open the next ten from the queue and rewrite each to the standard above. Everything else waits as `queued`.
4. **Start of a session:** read the inbox page's `answers` and `explain` collections, copy them into the register, and
   answer explanation requests before asking anything new.
5. **In chat**, name a decision by its question, not its ID. Ask in chat only when blocked right now: multiple choice
   with the recommendation first.

## The record

- The standards are the machinery set (ISO 12100, ISO 3691-4, ISO 13849-1, EN 60204-1, IEC 62443, ISO/IEC TR 5469,
  the Machinery Regulation), mapped from LionDriver's automotive frame in
  [WP-M-01 §4](assurance/01-management/WP-M-01-assurance-strategy.md#4-the-standards-and-how-each-one-is-used). No
  standard is held: mark every clause reference as to be checked against a licensed copy.
- Generated files are never edited by hand: folder READMEs (`assurance/tools/folder_index.py`), process maps and
  gate skeletons (`assurance/process/tools/process_model.py`), README figures
  (`docs/assets/openamrobot/make_assets.py`), the decision lifecycle figure. Run the generator and commit its output.
- A new work product goes into [WP-M-00](assurance/01-management/WP-M-00-work-product-register.md) first, with the
  document-control header of the [assurance README](assurance/README.md#document-control-header); then the process
  model gets an activity that produces it.
- The wiki is kept in [`wiki/`](wiki/README.md) and mirrored on merge; it explains and links, never claims.
- Before pushing, run the checks in [CONTRIBUTING.md](CONTRIBUTING.md); CI runs the same.

## Upstream

The assessed code lives in the openAMRobot GitHub organisation (Botshare LTD). Read-only clones of the upstream
repositories sit beside this one under `../openamrobot/`; never edit them there. Upstream keeps its own register of
approved values in `openAMRobot/.github/decisions.yaml`; quote it, do not restate it.
