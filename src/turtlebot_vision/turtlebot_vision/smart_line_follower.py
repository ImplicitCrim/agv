#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image, LaserScan
from cv_bridge import CvBridge
import cv2
import numpy as np
import time

class SmartPathFollower(Node):
    def __init__(self):
        super().__init__('smart_line_follower')

        self.bridge = CvBridge()
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscriptions
        self.image_sub = self.create_subscription(
            Image,
            '/image_raw',
            self.camera_callback,
            10
        )

        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10
        )

        # LiDAR Safety Watchdog
        self.obstacle_blocked = False
        self.stop_distance = 0.30
        self.slow_distance = 0.60
        self.speed_multiplier = 1.0
        self.last_lidar_time = 0.0

        # Path Following Settings
        self.max_forward_speed = 0.12
        self.min_forward_speed = 0.06
        self.safe_path_bound = 0.25

        self.get_logger().info(
            'Smart Path-Follower Active: Enforced Fail-Safe System.'
        )

    def lidar_callback(self, msg):
        """Monitor front arc and apply obstacle safety"""

        self.last_lidar_time = time.time()

        num_readings = len(msg.ranges)
        if num_readings == 0:
            return

        angle_window = int(num_readings * (30.0 / 360.0))

        front_right = msg.ranges[0:angle_window]
        front_left = msg.ranges[-angle_window:]
        front_arc = list(front_right) + list(front_left)

        valid_front_ranges = [
            r for r in front_arc
            if r > 0.12 and not np.isnan(r) and not np.isinf(r)
        ]

        if valid_front_ranges:
            closest_front_object = min(valid_front_ranges)

            self.get_logger().info(
                f"[FRONT LIDAR] Clear path: {closest_front_object:.2f} meters ahead"
            )

            if closest_front_object <= self.stop_distance:
                self.obstacle_blocked = True
                self.speed_multiplier = 0.0

                self.get_logger().warn(
                    "!!! STOP TRIGGERED: OBSTACLE INSIDE 30CM ZONE !!!"
                )

            elif closest_front_object < self.slow_distance:
                self.obstacle_blocked = False

                self.speed_multiplier = (
                    (closest_front_object - self.stop_distance)
                    / (self.slow_distance - self.stop_distance)
                )

            else:
                self.obstacle_blocked = False
                self.speed_multiplier = 1.0

        else:
            self.obstacle_blocked = False
            self.speed_multiplier = 1.0

    def camera_callback(self, data):
        twist = Twist()

        # LiDAR watchdog
        if (
            self.last_lidar_time == 0.0
            or (time.time() - self.last_lidar_time) > 0.5
        ):
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            self.publisher_.publish(twist)

            self.get_logger().error(
                "[CRITICAL SAFETY] No active LiDAR stream detected on /scan! Holding position."
            )

            return

        if self.obstacle_blocked:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            self.publisher_.publish(twist)
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except Exception:
            return

        blurred = cv2.GaussianBlur(cv_image, (5, 5), 0)

        h, w, _ = blurred.shape

        search_top = int(h * 0.40)
        search_bot = int(h * 0.70)

        roi = blurred[search_top:search_bot, 0:w]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([90, 50, 40])
        upper_blue = np.array([135, 255, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        M = cv2.moments(mask)

        if M['m00'] > 200:

            cx = int(M['m10'] / M['m00'])

            center_of_frame = w / 2.0

            normalized_error = (
                (cx - center_of_frame)
                / center_of_frame
            )

            abs_norm_error = abs(normalized_error)

            if abs_norm_error <= self.safe_path_bound:
                target_angular = 0.0

            else:
                sign = 1.0 if normalized_error >= 0 else -1.0

                steering_need = (
                    (abs_norm_error - self.safe_path_bound)
                    / (1.0 - self.safe_path_bound)
                )

                target_angular = -sign * (steering_need * 0.8)

            speed_drop = (
                abs_norm_error
                * (self.max_forward_speed - self.min_forward_speed)
            )

            target_linear = max(
                self.max_forward_speed - speed_drop,
                self.min_forward_speed
            )

            twist.linear.x = target_linear * self.speed_multiplier
            twist.angular.z = target_angular

        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)

    node = SmartPathFollower()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        stop_twist = Twist()
        stop_twist.linear.x = 0.0
        stop_twist.angular.z = 0.0

        node.publisher_.publish(stop_twist)

    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
