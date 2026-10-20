# Contributing to OpenAMRobot assurance

Contributions are welcome in machinery safety, safety-related control systems, electrical and mechanical
engineering, firmware and ROS 2 software, cybersecurity, verification, documentation and review. A review of an
analysis is as valuable as code. The [wiki's contributor guide](https://github.com/jherrodthomas/openamrobot-assurance/wiki/Contributor-guide)
is the short version of this page.

## Where to start

- **Questions and bugs:** [open an issue](https://github.com/jherrodthomas/openamrobot-assurance/issues) with the
  problem report or safety concern template.
- **Changes:** branch from `main` and open a pull request against `main`. The pull request template asks for a
  safety-impact statement; "none" is a valid answer with a reason.
- **Decisions for the project lead** are not issues. They go into the
  [decision register](assurance/01-management/decisions/README.md) as self-contained questions.
- **Upstream code** is never edited here. The forked platform repositories take code changes; this repository holds
  the record. Upstream's register (`openAMRobot/.github/decisions.yaml`) is quoted, not restated.

## Safety-relevant changes

A change is safety-relevant if it touches a path on the
[safety-relevant file list](assurance/07-supporting/safety-relevant-paths.txt) or changes an assurance work product.
Such a pull request must include:

1. **Rationale:** what the change does and why.
2. **Impact analysis:** which hazards, safety functions, requirements and assumptions it affects, following
   [WP-M-11](assurance/01-management/WP-M-11-impact-analysis.md) and [WP-P-02](assurance/07-supporting/WP-P-02-change-management.md),
   recorded under [`assurance/07-supporting/impact/`](assurance/07-supporting/impact/README.md).
3. **Verification:** the tests or analyses that show the change is correct, and their results.
4. **Record updates:** the affected work products, with every generator re-run.

## Checks to run locally

Only Python 3 is needed (PyYAML for the decision register):

```sh
python3 assurance/01-management/decisions/check_decisions.py
python3 assurance/tools/folder_index.py --check
python3 assurance/process/tools/process_model.py --check
python3 assurance/process/tools/process_figures.py --check
python3 assurance/02-concept/figures/fig_c01.py --check
python3 assurance/02-concept/figures/fig_c02.py --check
python3 assurance/02-concept/figures/fig_c03.py --check
python3 assurance/02-concept/figures/fig_c04.py --check
python3 assurance/02-concept/figures/fig_c06.py --check
python3 assurance/03-system/figures/fig_s02.py --check
python3 docs/assets/openamrobot/make_assets.py --check
python3 assurance/tools/check_links.py
python3 assurance/tools/check_tables.py
python3 tools/wiki/build_wiki.py
```

CI runs the same checks on every pull request and fails if a generated file is out of date.

## What can and cannot change a review state

- A work product leaves `Draft` only through a verification review by someone other than its author
  ([WP-P-05](assurance/07-supporting/WP-P-05-verification-review-procedure.md)), and a claim is accepted only through
  a confirmation review at the independence [WP-M-06](assurance/01-management/WP-M-06-confirmation-measures-plan.md)
  requires.
- A passing CI run, a passing test or an existing file does not accept anything. It can be evidence that a reviewer
  accepts.
- An AI-generated review is not a substitute for the required independent confirmation. AI-drafted work is the
  committer's work at independence level I0 ([WP-M-02 §3.3](assurance/01-management/WP-M-02-safety-plan.md#33-ai-assisted-authoring)).
- Never edit generated files (process maps, swimlane figures, gate skeletons, folder READMEs, README figures, the dashboard) by hand. Change the
  source and regenerate.

## Working with Claude sessions

Much of the drafting is done in Claude Code sessions under the project lead's direction. The rules those sessions
follow are in [CLAUDE.md](CLAUDE.md): sort questions before asking, keep every question self-contained, ask in
batches of ten, record decisions in the register. A session's pull request is reviewed like any other.

## Licensing

Contributions to this record are under the [MIT license](LICENSE). OpenAMRobot itself is published by Botshare LTD
under MIT (software), CERN-OHL-P-2.0 (hardware) and CC BY 4.0 (documentation); forks must not imply Botshare's
endorsement.
