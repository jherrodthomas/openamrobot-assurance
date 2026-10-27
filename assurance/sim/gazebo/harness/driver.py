#!/usr/bin/env python3
"""Scenario driver: brings the collision monitor up, publishes the robot footprint the monitor's approach polygon
needs (normally the local costmap's job), runs the command profile on sim time, injects faults, and records a
trace at 20 Hz: the true pose from Gazebo, odometry, what was commanded, what reached the base and the monitor's
action. Writes <out>/<scenario>.trace.json and exits; the launch file then shuts everything down."""
import json
import math
import os
import time

import rclpy
import yaml
from geometry_msgs.msg import Point32, PolygonStamped, PoseStamped, Twist
from lifecycle_msgs.srv import ChangeState, GetState
from nav2_msgs.msg import CollisionMonitorState
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

RATE = 20.0


def yaw_of(q):
  return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


class Driver(Node):
  def __init__(self):
    super().__init__("scenario_driver")
    self.spec = json.loads(self.declare_parameter("scenario", "{}").value)
    self.out = self.declare_parameter("out", "/out").value
    self.scan_filter = self.declare_parameter("scan_filter", "").value
    params = yaml.safe_load(open(self.declare_parameter("nav2_params", "").value))
    fp = params["local_costmap"]["local_costmap"]["ros__parameters"]["footprint"]
    self.footprint = json.loads(fp) if isinstance(fp, str) else fp
    self.world = self.spec["id"].lower().replace("-", "_")
    self.odom = self.gt = self.cmd_out = None
    self.action = 0
    self.scans_in = self.scans_filtered = 0
    self.scan_min = None
    self.gate_open = True
    self.create_subscription(Odometry, "/odom", lambda m: setattr(self, "odom", m), 10)
    self.create_subscription(Twist, "/cmd_vel", lambda m: setattr(self, "cmd_out", m), 10)
    self.create_subscription(CollisionMonitorState, "/collision_monitor_state", lambda m: setattr(self, "action", m.action_type), 10)
    self.create_subscription(LaserScan, "/scan", self.on_scan, qos_profile_sensor_data)
    self.create_subscription(LaserScan, "/scan_filtered", self.on_filtered, qos_profile_sensor_data)
    self.create_subscription(PoseStamped, "/gt_pose", self.on_gt, 10)
    self.gated = self.create_publisher(LaserScan, "/scan_gated", 10)
    self.fp_pub = self.create_publisher(PolygonStamped, "/local_costmap/published_footprint", 10)
    self.pubs = {t: self.create_publisher(Twist, "/" + t, 10) for t in ("cmd_vel", "cmd_vel_smoothed")}
    self.create_timer(0.2, self.publish_footprint)

  def on_scan(self, m):
    self.scans_in += 1
    if self.gate_open:
      self.gated.publish(m)

  def on_filtered(self, m):
    self.scans_filtered += 1
    near = [r for r in m.ranges if math.isfinite(r) and m.range_min <= r <= m.range_max]
    self.scan_min = round(min(near), 3) if near else None

  def on_gt(self, m):
    self.gt = m.pose

  def publish_footprint(self):
    p = PolygonStamped()
    p.header.frame_id = "base_link"
    p.header.stamp = self.get_clock().now().to_msg()
    p.polygon.points = [Point32(x=float(x), y=float(y), z=0.0) for x, y in self.footprint]
    self.fp_pub.publish(p)

  def now(self):
    return self.get_clock().now().nanoseconds * 1e-9

  def spin_until(self, cond, timeout_wall, what):
    end = time.monotonic() + timeout_wall
    while rclpy.ok() and not cond():
      rclpy.spin_once(self, timeout_sec=0.05)
      if time.monotonic() > end:
        raise TimeoutError(f"timed out waiting for {what}")

  def lifecycle(self, transition):
    cli = self.create_client(ChangeState, "/collision_monitor/change_state")
    self.spin_until(lambda: cli.service_is_ready(), 60, "collision_monitor/change_state")
    req = ChangeState.Request()
    req.transition.id = transition
    fut = cli.call_async(req)
    self.spin_until(lambda: fut.done(), 30, f"transition {transition}")
    return fut.result().success

  def monitor_state(self):
    cli = self.create_client(GetState, "/collision_monitor/get_state")
    self.spin_until(lambda: cli.service_is_ready(), 30, "collision_monitor/get_state")
    fut = cli.call_async(GetState.Request())
    self.spin_until(lambda: fut.done(), 30, "get_state")
    return fut.result().current_state.label

  def sleep_sim(self, seconds):
    end = self.now() + seconds
    self.spin_until(lambda: self.now() >= end, 600, "sim time")

  def run(self):
    self.spin_until(lambda: self.now() > 0 and self.odom is not None and self.gt is not None, 180, "clock, odometry and true pose")
    self.spin_until(lambda: self.scans_filtered > 3, 120, "filtered scans")
    configured = self.lifecycle(1)
    active = self.lifecycle(3)
    state = self.monitor_state()
    self.sleep_sim(2.0)   # robot settles after the spawn
    faults = self.spec.get("faults", [])
    profile = self.spec["profile"]
    settle = float(self.spec.get("settle", 3.0))
    total = sum(float(s["duration"]) for s in profile) + settle
    rows, t0, step = [], self.now(), 1.0 / RATE
    nxt = t0
    while rclpy.ok():
      t = self.now() - t0
      if t > total:
        break
      seg, acc = None, 0.0
      for s in profile:
        if t < acc + float(s["duration"]):
          seg = s
          break
        acc += float(s["duration"])
      for f in faults:
        if f["kind"] == "scan_dropout" and t >= float(f["at"]):
          self.gate_open = False
      topic = seg["topic"] if seg else profile[-1]["topic"]
      cmd = Twist()
      if seg:
        cmd.linear.x, cmd.angular.z = float(seg["linear"]), float(seg.get("angular", 0.0))
      self.pubs[topic].publish(cmd)
      g, o, c = self.gt, self.odom, self.cmd_out
      rows.append({"t": round(t, 3), "x": round(g.position.x, 4), "y": round(g.position.y, 4), "yaw": round(yaw_of(g.orientation), 4),
                   "odom_x": round(o.pose.pose.position.x, 4), "v": round(o.twist.twist.linear.x, 4), "w": round(o.twist.twist.angular.z, 4),
                   "cmd": round(cmd.linear.x, 3), "cmd_topic": topic, "out": round(c.linear.x, 3) if c else None,
                   "action": int(self.action), "scan_gate": self.gate_open, "scan_min": self.scan_min})
      nxt += step
      self.spin_until(lambda: self.now() >= nxt, 120, "next sample")
    commit = open("/ws/software_commit").read().strip()
    trace = {"scenario": self.spec["id"], "target": os.environ.get("SCENARIO_TARGET", ""), "software_commit": commit,
             "scan_filter": self.scan_filter, "monitor": {"configured": configured, "activated": active, "state": state},
             "footprint": self.footprint, "scans": {"in": self.scans_in, "filtered": self.scans_filtered}, "rate_hz": RATE, "rows": rows}
    with open(f"{self.out}/{self.spec['id']}.trace.json", "w") as f:
      json.dump(trace, f, separators=(",", ":"))
    self.get_logger().info(f"wrote {len(rows)} samples; monitor {state}")


def main():
  rclpy.init()
  node = Driver()
  try:
    node.run()
  finally:
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
  main()
