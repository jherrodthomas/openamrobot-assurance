#!/bin/bash
# Run scenarios inside the image: /scenarios is this folder (read-only), /out receives traces and logs.
# usage: bash /scenarios/harness/run_in_container.sh [GZ-01 ...]   (no argument: every scenario)
for f in $SCENARIO_SETUP; do source "$f"; done
ids=("$@")
if [ ${#ids[@]} -eq 0 ]; then
  mapfile -t ids < <(python3 -c 'import yaml; [print(s["id"]) for s in yaml.safe_load(open("/scenarios/scenarios.yaml"))["scenarios"]]')
fi
rc=0
for id in "${ids[@]}"; do
  start=$(date +%s)
  timeout 900 ros2 launch /scenarios/harness/scenario.launch.py scenario:="$id" out:=/out > "/out/$id.log" 2>&1
  code=$?
  if [ -f "/out/$id.trace.json" ]; then echo "$id: trace written ($(( $(date +%s) - start )) s)"; else echo "$id: no trace (exit $code), see $id.log"; rc=1; fi
done
exit $rc
