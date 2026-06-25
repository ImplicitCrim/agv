import os

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    slam_config_path = os.path.expanduser(
        '~/slam_toolbox_config.yaml'
    )

    # LiDAR Driver
    lidar_node = Node(
        package='sllidar_ros2',
        executable='sllidar_node',
        name='sllidar_node',
        output='screen',
        parameters=[{
            'serial_port': '/dev/ttyUSB0',
            'serial_baudrate': 115200,
            'frame_id': 'laser_frame',
            'inverted': False,
            'angle_compensate': True
        }]
    )

    # RF2O Odometry
    rf2o_node = Node(
        package='rf2o_laser_odometry',
        executable='rf2o_laser_odometry_node',
        name='rf2o_laser_odometry',
        output='screen',
        parameters=[{
            'laser_scan_topic': '/scan',
            'odom_topic': '/odom_rf2o',
            'publish_tf': True,
            'base_frame_id': 'base_link',
            'odom_frame_id': 'odom',
            'freq': 10.0,
            'init_pose_from_topic': ''
        }]
    )

    # Static TF
    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_tf',
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'base_link',
            'laser_frame'
        ],
        output='screen'
    )

    # SLAM Toolbox
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config_path]
    )

    # Serial Bridge
    cmd_vel_bridge_node = Node(
        package='turtlebot_serial_bridge',
        executable='cmd_vel_bridge',
        name='cmd_vel_bridge',
        output='screen'
    )

    return LaunchDescription([
        lidar_node,
        rf2o_node,
        static_tf_node,
        slam_toolbox_node,
        cmd_vel_bridge_node
    ])