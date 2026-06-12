from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='camera',
            parameters=[
                {'video_device': '/dev/video0'}
            ],
            output='screen'
        ),

        Node(
            package='turtlebot_serial_bridge',
            executable='cmd_vel_bridge',
            name='cmd_vel_bridge',
            output='screen'
        ),

        Node(
            package='turtlebot_vision',
            executable='blue_test',
            name='blue_line_follower',
            output='screen'
        )

    ])
