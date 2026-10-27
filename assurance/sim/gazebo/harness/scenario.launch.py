"""Launch one scenario: Gazebo (server only) with the scenario world, the calibrated robot, upstream's bridge, scan
body filter and collision monitor configuration, and the driver. Usage, inside the image:
  ros2 launch /harness/scenario.launch.py scenario:=GZ-01 out:=/out
Nothing of upstream is edited: its files are read from the installed packages and the calibration is applied to the
expanded robot description in memory."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402
from ament_index_python.packages import get_package_share_directory  # noqa: E402
from launch import LaunchDescription  # noqa: E402
from launch.actions import DeclareLaunchArgument, EmitEvent, ExecuteProcess, OpaqueFunction, RegisterEventHandler, SetEnvironmentVariable  # noqa: E402
from launch.event_handlers import OnProcessExit  # noqa: E402
from launch.events import Shutdown  # noqa: E402
from launch.substitutions import LaunchConfiguration  # noqa: E402
from launch_ros.actions import Node  # noqa: E402

import calibrate  # noqa: E402
import world  # noqa: E402

HARNESS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HARNESS)


def setup(context):
  sid = LaunchConfiguration("scenario").perform(context)
  out = LaunchConfiguration("out").perform(context)
  os.makedirs(out, exist_ok=True)
  spec = next(s for s in yaml.safe_load(open(os.path.join(ROOT, "scenarios.yaml")))["scenarios"] if s["id"] == sid)
  desc = get_package_share_directory("openamrobot_description")
  gz = get_package_share_directory("openamrobot_gazebo")
  nav2 = get_package_share_directory("openamrobot_nav2")
  urdf = subprocess.run(["xacro", os.path.join(desc, "urdf", "robo_urdf.urdf.xacro")], check=True, capture_output=True, text=True).stdout
  urdf, notes = calibrate.calibrate(urdf, calibrate.load_plant(os.path.join(ROOT, "plant.yaml")))
  for o in spec.get("sensor_overrides", []):
    urdf, note = calibrate.override_sensor(urdf, o)
    notes.append(note)
  urdf = calibrate.instrument(urdf)
  wname = sid.lower().replace("-", "_")
  world_path = os.path.join(out, f"{sid}.sdf")
  with open(world_path, "w") as f:
    f.write(world.world(open(os.path.join(gz, "worlds", "walled_world.sdf")).read(), spec.get("obstacles", []), wname))
  with open(os.path.join(out, f"{sid}.calibration.json"), "w") as f:
    json.dump(notes, f, indent=1)
  params = os.path.join(nav2, "config", "nav2_params.yaml")
  sim = {"use_sim_time": True}
  # upstream's sim scan body filter as the target's own sim bringup starts it, fed through the driver's gate so that a
  # dropout can be injected: the per-sector node where the target has its sim configuration (upstream issue #74),
  # else the laser_filters angular-bounds chain of the baseline
  sector = os.path.join(nav2, "config", "scan_body_filter_sim.yaml")
  if os.path.exists(sector):
    filter_name = "openamrobot_perception/scan_body_filter with scan_body_filter_sim.yaml"
    scan_filter = Node(package="openamrobot_perception", executable="scan_body_filter", name="scan_body_filter", output="log",
                       parameters=[sector, sim, {"scan_in": "/scan_gated", "scan_out": "/scan_filtered"}])
  else:
    filter_name = "laser_filters scan_to_scan_filter_chain with scan_body_filter.yaml"
    scan_filter = Node(package="laser_filters", executable="scan_to_scan_filter_chain", name="scan_body_filter", output="log",
                       parameters=[os.path.join(nav2, "config", "scan_body_filter.yaml"), sim],
                       remappings=[("scan", "/scan_gated"), ("scan_filtered", "/scan_filtered")])
  driver = Node(executable=os.path.join(HARNESS, "driver.py"), name="scenario_driver", output="screen",
                parameters=[sim, {"scenario": json.dumps(spec), "out": out, "nav2_params": params, "scan_filter": filter_name}])
  return [
    SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.dirname(desc)),
    ExecuteProcess(cmd=["gz", "sim", "-r", "-s", "-v", "2", world_path], output="log"),
    Node(package="robot_state_publisher", executable="robot_state_publisher", parameters=[sim, {"robot_description": urdf}], output="log"),
    Node(package="ros_gz_sim", executable="create", arguments=["-name", "openamrobot", "-string", urdf, "-x", "0", "-y", "0", "-z", "0.05"], output="log"),
    Node(package="ros_gz_bridge", executable="parameter_bridge", output="log",
         parameters=[{"config_file": os.path.join(gz, "config", "gz_bridge.yaml"), "qos_overrides./tf_static.publisher.durability": "transient_local"}]),
    # true model poses from Gazebo, for contact (odometry keeps counting when a blocked wheel slips)
    Node(package="ros_gz_bridge", executable="parameter_bridge", name="truth_bridge", output="log",
         arguments=["/model/openamrobot/pose@geometry_msgs/msg/PoseStamped[gz.msgs.Pose"],
         remappings=[("/model/openamrobot/pose", "/gt_pose")]),
    scan_filter,
    Node(package="nav2_collision_monitor", executable="collision_monitor", name="collision_monitor", output="log", parameters=[params, sim]),
    driver,
    RegisterEventHandler(OnProcessExit(target_action=driver, on_exit=[EmitEvent(event=Shutdown(reason="scenario done"))])),
  ]


def generate_launch_description():
  return LaunchDescription([
    DeclareLaunchArgument("scenario"),
    DeclareLaunchArgument("out", default_value="/out"),
    OpaqueFunction(function=setup),
  ])
