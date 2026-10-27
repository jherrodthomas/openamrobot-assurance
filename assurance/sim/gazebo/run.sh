#!/usr/bin/env bash
# Run the Gazebo scenarios on every target of pins.yaml and judge them. Needs Docker.
# usage: assurance/sim/gazebo/run.sh [GZ-01 ...]        writes results/traces/<target>/ and regenerates results/
#   SCENARIO_TARGETS  targets to run (default: every target in pins.yaml)
#   SCENARIO_OUT      where traces go (default results/traces)
#   SCENARIO_MODE     write (default) or verify (judge only, write nothing else; used by CI)
# Images are openamr-scenarios:<target>, built from docker/ when missing.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="${SCENARIO_OUT:-$here/results/traces}"
targets="${SCENARIO_TARGETS:-$(python3 -c 'import sys, yaml; print(" ".join(yaml.safe_load(open(sys.argv[1]))["targets"]))' "$here/pins.yaml")}"
for t in $targets; do
  image="openamr-scenarios:$t"
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    [ -d "$here/docker/context/targets/$t" ] || "$here/prepare.sh"
    docker build --build-arg TARGET="$t" -t "$image" "$here/docker"
  fi
  mkdir -p "$out/$t"
  if [ $# -eq 0 ]; then rm -f "$out/$t"/*.trace.json; else for id in "$@"; do rm -f "$out/$t/$id.trace.json"; done; fi
  docker run --rm -v "$here:/scenarios:ro" -v "$out/$t:/out" "$image" bash /scenarios/harness/run_in_container.sh "$@" || true
done
python3 "$here/evaluate.py" --traces "$out" "--${SCENARIO_MODE:-write}"
