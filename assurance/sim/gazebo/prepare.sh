#!/usr/bin/env bash
# Fetch the pinned sources into docker/context/ so that the image builds need no network:
#   context/deps/                 laser_filters and the Nav2 packages (one layer, shared by every target)
#   context/targets/<target>/src  the software under test at the target's commit, and its software_commit file
# usage: assurance/sim/gazebo/prepare.sh            (run from anywhere; needs git and python3 with PyYAML)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
ctx="$here/docker/context"
pin() { python3 -c 'import sys, yaml; v = yaml.safe_load(open(sys.argv[1]))
for k in sys.argv[2:]: v = v[k]
print(" ".join(v) if isinstance(v, list) else v)' "$here/pins.yaml" "$@"; }
fetch() {  # url commit dir
  rm -rf "$3"; mkdir -p "$3"
  git -C "$3" init -q
  git -C "$3" remote add origin "$1"
  git -C "$3" fetch -q --depth 1 origin "$2" 2>/dev/null || git -C "$3" fetch -q origin
  git -C "$3" checkout -q "$2"
  echo "$(basename "$3") at $(git -C "$3" rev-parse --short HEAD)"
}
rm -rf "$ctx"; mkdir -p "$ctx/deps" "$ctx/fetch"
fetch "$(pin laser_filters repo)" "$(pin laser_filters commit)" "$ctx/fetch/laser_filters"
cp -r "$ctx/fetch/laser_filters" "$ctx/deps/laser_filters"; rm -rf "$ctx/deps/laser_filters/.git"
fetch "$(pin navigation2 repo)" "$(pin navigation2 commit)" "$ctx/fetch/navigation2"
for p in $(pin navigation2 packages); do cp -r "$ctx/fetch/navigation2/$p" "$ctx/deps/"; done
for t in $(python3 -c 'import sys, yaml; print(" ".join(yaml.safe_load(open(sys.argv[1]))["targets"]))' "$here/pins.yaml"); do
  fetch "$(pin software repo)" "$(pin targets "$t" commit)" "$ctx/fetch/$t"
  mkdir -p "$ctx/targets/$t/src"
  for p in $(pin software packages); do
    if [ -d "$ctx/fetch/$t/ros2/src/$p" ]; then cp -r "$ctx/fetch/$t/ros2/src/$p" "$ctx/targets/$t/src/"; fi
  done
  git -C "$ctx/fetch/$t" rev-parse HEAD > "$ctx/targets/$t/software_commit"
  echo "$t: $(ls "$ctx/targets/$t/src" | tr '\n' ' ')"
done
rm -rf "$ctx/fetch"
