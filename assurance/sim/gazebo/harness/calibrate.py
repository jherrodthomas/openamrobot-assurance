"""Apply plant.yaml to the robot description: replace each named element inside upstream's DiffDrive plugin block.
Fails if an element is missing or does not hold the value plant.yaml says upstream has. A scenario can also replace
one value of a Gazebo sensor (`sensor_overrides`), under the same guard. Standard library only."""
from __future__ import annotations

import re


def load_plant(path: str) -> dict:
  """The flat subset of YAML plant.yaml uses: `name: {value: v, upstream: u, source: "..."}` under diff_drive."""
  out = {}
  with open(path, encoding="utf-8") as f:
    lines = f.readlines()
  for line in lines:
    m = re.match(r"\s+(\w+):\s*\{value:\s*([-\d.]+),\s*upstream:\s*([-\d.]+)", line)
    if m:
      out[m.group(1)] = (float(m.group(2)), float(m.group(3)))
  return out


def calibrate(urdf: str, plant: dict) -> tuple[str, list[str]]:
  m = re.search(r"<plugin[^>]*gz::sim::systems::DiffDrive[^>]*>(.*?)</plugin>", urdf, re.S)
  if not m:
    raise ValueError("no DiffDrive plugin in the robot description")
  block, notes = m.group(1), []
  for name, (value, upstream) in plant.items():
    tag = re.search(rf"<{name}>\s*([-\d.eE+]+)\s*</{name}>", block)
    if not tag:
      raise ValueError(f"DiffDrive has no <{name}>")
    have = float(tag.group(1))
    if abs(have - upstream) > 1e-9:
      raise ValueError(f"<{name}> is {have} at the pin, plant.yaml expects upstream {upstream}: re-check plant.yaml")
    block = block[:tag.start(1)] + f"{value:g}" + block[tag.end(1):]
    notes.append(f"{name}: {upstream:g} -> {value:g}")
  return urdf[:m.start(1)] + block + urdf[m.end(1):], notes


def override_sensor(urdf: str, o: dict) -> tuple[str, str]:
  """Replace `element` (a path such as range/min) inside the Gazebo sensor named `sensor`; fails unless it holds
  `upstream`."""
  m = re.search(rf'<sensor name="{re.escape(o["sensor"])}"[^>]*>(.*?)</sensor>', urdf, re.S)
  if not m:
    raise ValueError(f"no sensor {o['sensor']} in the robot description")
  block, start = m.group(1), m.start(1)
  for tag in o["element"].split("/")[:-1]:
    inner = re.search(rf"<{tag}>(.*?)</{tag}>", block, re.S)
    if not inner:
      raise ValueError(f"sensor {o['sensor']} has no <{tag}>")
    block, start = inner.group(1), start + inner.start(1)
  leaf = o["element"].split("/")[-1]
  tag = re.search(rf"<{leaf}>\s*([-\d.eE+]+)\s*</{leaf}>", block)
  if not tag:
    raise ValueError(f"sensor {o['sensor']} has no {o['element']}")
  have = float(tag.group(1))
  if abs(have - float(o["upstream"])) > 1e-9:
    raise ValueError(f"{o['sensor']} {o['element']} is {have} at the pin, the scenario expects upstream {o['upstream']}")
  a, b = start + tag.start(1), start + tag.end(1)
  return urdf[:a] + f"{float(o['value']):g}" + urdf[b:], f"{o['sensor']} {o['element']}: {have:g} -> {float(o['value']):g}"


POSE_PUBLISHER = ('<gazebo><plugin filename="gz-sim-pose-publisher-system" name="gz::sim::systems::PosePublisher">'
                  '<publish_link_pose>false</publish_link_pose><publish_model_pose>true</publish_model_pose>'
                  '<publish_nested_model_pose>false</publish_nested_model_pose><use_pose_vector_msg>false</use_pose_vector_msg>'
                  '<update_frequency>50</update_frequency></plugin></gazebo>')


def instrument(urdf: str) -> str:
  """Add Gazebo's pose publisher so the harness can read the model's true pose (/model/<name>/pose). Instrumentation
  only: it publishes, it changes nothing the robot does."""
  i = urdf.rindex("</robot>")
  return urdf[:i] + POSE_PUBLISHER + urdf[i:]
