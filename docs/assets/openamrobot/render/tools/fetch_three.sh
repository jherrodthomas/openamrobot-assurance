#!/bin/sh
# Fetch the three.js r160 modules render.html imports (MIT) next to it. Run once; the files are not committed.
set -e
D=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$D/loaders" "$D/utils"
curl -sS -L -o "$D/three.module.js" https://raw.githubusercontent.com/mrdoob/three.js/r160/build/three.module.js
curl -sS -L -o "$D/loaders/GLTFLoader.js" https://raw.githubusercontent.com/mrdoob/three.js/r160/examples/jsm/loaders/GLTFLoader.js
curl -sS -L -o "$D/utils/BufferGeometryUtils.js" https://raw.githubusercontent.com/mrdoob/three.js/r160/examples/jsm/utils/BufferGeometryUtils.js
echo "three.js r160 fetched into $D"
