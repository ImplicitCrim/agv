import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class CameraViewer(Node):

    def __init__(self):
        super().__init__('camera_viewer')

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self.image_callback,
            10
        )

        self.image_saved = False

    def image_callback(self, msg):

        if self.image_saved:
            return

        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        cv2.imwrite('/home/learn/camera_view.jpg', frame)

        self.get_logger().info(
            'Image saved to /home/learn/camera_view.jpg'
        )

        self.image_saved = True

        rclpy.shutdown()


def main(args=None):

    rclpy.init(args=args)

    node = CameraViewer()

    rclpy.spin(node)

    node.destroy_node()


if __name__ == '__main__':
    main()