# Documentation

This repository holds the engineering assurance record for the OpenAMRobot fork, not the robot's code. The code
lives in the forked platform repositories; the upstream documentation stays where upstream keeps it.

| If you want to | Read |
|---|---|
| Understand the safety architecture argument | [Architecture](architecture.md) |
| Browse every work product, with its gate and status | [Assurance record](../assurance/README.md) |
| See what the inherited robot lacks, finding by finding | [Gap assessment](../assurance/00-assessment/gap-assessment.md) |
| Get oriented: processes, process maps, standards, glossary | [Wiki](https://github.com/jherrodthomas/openamrobot-assurance/wiki), kept in [`wiki/`](../wiki/README.md) and mirrored on merge |
| Contribute | [Contributing](../CONTRIBUTING.md) |
| Report a vulnerability | [Security policy](../SECURITY.md) |

Every figure is generated and checked by CI; nothing in them is drawn by hand:

| Figures | Generator |
|---|---|
| README and wiki figures under [`assets/openamrobot/`](assets/openamrobot/): hero, standards, architecture, roadmap, lifecycle, status card, standards map, repository map | [`make_assets.py`](assets/openamrobot/make_assets.py) |
| Process swimlanes, lifecycle grid and interface figure under [`assets/openamrobot/process/`](assets/openamrobot/process/) | [`process_figures.py`](../assurance/process/tools/process_figures.py), from the process model |
| Living Safety Case dashboard and lifecycle areas under [`assets/assurance/`](assets/assurance/) | [`generate_dashboard.py`](../assurance/case/tools/generate_dashboard.py), from the case records |
