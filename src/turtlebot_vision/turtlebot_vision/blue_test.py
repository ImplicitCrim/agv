import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np


class BlueLineFollower(Node):

    def __init__(self):
        super().__init__('blue_line_follower')

        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.bridge = CvBridge()

        # PD gains
        self.Kp = 0.0008
        self.Kd = 0.0008

        self.previous_error = 0.0

        self.max_forward_speed = 0.05
        self.min_forward_speed = 0.025

        self.get_logger().info(
            "AGV V1.1 Smooth Curve Follower Started"
        )

    def image_callback(self, msg):

        try:

            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

        except Exception:

            return

        # Smooth image
        blurred = cv2.GaussianBlur(
            frame,
            (5, 5),
            0
        )

        hsv = cv2.cvtColor(
            blurred,
            cv2.COLOR_BGR2HSV
        )

        lower_blue = np.array([85, 30, 30])
        upper_blue = np.array([135, 255, 255])

        mask = cv2.inRange(
            hsv,
            lower_blue,
            upper_blue
        )

        height, width = mask.shape

        screen_center = width // 2

        # Horizontal band ROI
        search_top = int(height * 0.40)
        search_bot = int(height * 0.70)

        mask[0:search_top, :] = 0
        mask[search_bot:height, :] = 0

        M = cv2.moments(mask)

        twist = Twist()

        # Ignore tiny detections
        if M["m00"] > 400:

            cx = int(M["m10"] / M["m00"])

            error = float(
                screen_center - cx
            )

            abs_error = abs(error)

            # ===== STRAIGHT LOCK =====
            if abs_error < 15:

                twist.linear.x = self.max_forward_speed
                twist.angular.z = 0.0

            else:

                derivative = (
                    error -
                    self.previous_error
                )

                angular = (
                    self.Kp * error +
                    self.Kd * derivative
                )

                self.previous_error = error

                angular = max(
                    min(angular, 0.12),
                    -0.12
                )

                # Adaptive speed
                speed_drop = (
                    abs_error /
                    screen_center
                ) * (
                    self.max_forward_speed -
                    self.min_forward_speed
                )

                twist.linear.x = max(
                    self.min_forward_speed,
                    self.max_forward_speed -
                    speed_drop
                )

                twist.angular.z = angular

            self.get_logger().info(
                f"Err={error:.1f} "
                f"Spd={twist.linear.x:.3f} "
                f"Ang={twist.angular.z:.3f}",
                throttle_duration_sec=0.5
            )

        else:

            twist.linear.x = 0.0
            twist.angular.z = 0.0

            self.get_logger().warn(
                "LINE LOST - STOPPING"
            )

        self.publisher.publish(
            twist
        )


def main(args=None):

    rclpy.init(args=args)

    node = BlueLineFollower()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()