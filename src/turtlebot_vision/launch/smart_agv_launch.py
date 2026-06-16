from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    camera_node = Node(
        package='v4l2_camera',
        executable='v4l2_camera_node',
        name='camera_node',
        output='screen'
    )

    serial_node = Node(
        package='turtlebot_serial_bridge',
        executable='cmd_vel_bridge',
        name='serial_bridge',
        output='screen'
    )

    line_follower_node = Node(
        package='turtlebot_vision',
        executable='smart_line_follower',
        name='smart_line_follower',
        output='screen'
    )

    lidar_node = Node(
        package='sllidar_ros2',
        executable='sllidar_node',
        name='sllidar_node',
        output='screen',
        parameters=[
            {'serial_port': '/dev/ttyUSB0'},
            {'serial_baudrate': 256000},
            {'frame_id': 'laser'}
        ]
    )

    return LaunchDescription([
        camera_node,
        lidar_node,
        serial_node,
        line_follower_node
    ])
