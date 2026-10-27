"""Write a Gazebo world for one scenario: the world-level systems of upstream's walled_world.sdf (physics, user
commands, scene broadcaster, sensors with ogre2), a ground plane, a light and the scenario's static obstacles."""
from __future__ import annotations

import re


def world_systems(upstream_world_sdf: str) -> str:
  head = upstream_world_sdf.split("<model", 1)[0]
  plugins = re.findall(r"\s*<plugin\b.*?</plugin>", head, re.S)
  if not plugins:
    raise ValueError("no world-level plugins found in the upstream world")
  physics = re.search(r"\s*<physics\b.*?</physics>", head, re.S)
  return (physics.group(0) if physics else "") + "".join(plugins)


def obstacle_sdf(o: dict) -> str:
  x, y, z = o["pose"]
  if o["shape"] == "box":
    sx, sy, sz = o["size"]
    geom = f"<box><size>{sx} {sy} {sz}</size></box>"
  elif o["shape"] == "cylinder":
    r, h = o["size"]
    geom = f"<cylinder><radius>{r}</radius><length>{h}</length></cylinder>"
  else:
    raise ValueError(f"unknown shape {o['shape']}")
  return (f'<model name="{o["name"]}"><static>true</static><pose>{x} {y} {z} 0 0 0</pose><link name="link">'
          f"<collision name=\"c\"><geometry>{geom}</geometry></collision>"
          f"<visual name=\"v\"><geometry>{geom}</geometry></visual></link></model>")


def world(upstream_world_sdf: str, obstacles: list[dict], name: str = "scenario") -> str:
  ground = ('<model name="ground_plane"><static>true</static><link name="link"><collision name="c"><geometry><plane>'
            '<normal>0 0 1</normal><size>40 40</size></plane></geometry></collision><visual name="v"><geometry><plane>'
            '<normal>0 0 1</normal><size>40 40</size></plane></geometry></visual></link></model>')
  light = '<light type="directional" name="sun"><pose>0 0 10 0 0 0</pose><direction>-0.5 0.1 -0.9</direction></light>'
  return (f'<?xml version="1.0"?>\n<sdf version="1.9"><world name="{name}">{world_systems(upstream_world_sdf)}'
          f"{light}{ground}{''.join(obstacle_sdf(o) for o in obstacles)}</world></sdf>\n")
