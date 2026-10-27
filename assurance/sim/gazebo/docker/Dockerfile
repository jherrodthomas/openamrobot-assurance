# Scenario-test image: ROS 2 Jazzy, Gazebo Harmonic and the system dependencies of the pinned Nav2 image; the collision
# monitor with its Nav2 dependencies and laser_filters in a shared layer; then the software under test of one target
# (../pins.yaml). Build context is this folder after ../prepare.sh has filled context/; the build needs no network.
#   docker build --build-arg TARGET=bl-001 -t openamr-scenarios:bl-001 .
ARG BASE=ghcr.io/ros-navigation/navigation2:jazzy@sha256:243dec3ba8c7d7af47c27bd87056e8271c3a894d578d7860919e2d395a43724c
FROM ${BASE}
SHELL ["/bin/bash", "-c"]
COPY context/deps /ws/deps/src
RUN source /opt/ros/jazzy/setup.bash && source /opt/underlay_ws/install/setup.bash \
 && cd /ws/deps && colcon build --cmake-args -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release --event-handlers console_cohesion- \
 && rm -rf build log
ARG TARGET
COPY context/targets/${TARGET}/src /ws/sw/src
COPY context/targets/${TARGET}/software_commit /ws/software_commit
RUN source /opt/ros/jazzy/setup.bash && source /opt/underlay_ws/install/setup.bash && source /ws/deps/install/setup.bash \
 && cd /ws/sw && colcon build --cmake-args -DBUILD_TESTING=OFF --event-handlers console_cohesion- \
 && rm -rf build log
ENV SCENARIO_TARGET=${TARGET}
ENV SCENARIO_SETUP="/opt/ros/jazzy/setup.bash /opt/underlay_ws/install/setup.bash /ws/deps/install/setup.bash /ws/sw/install/setup.bash"
WORKDIR /harness
