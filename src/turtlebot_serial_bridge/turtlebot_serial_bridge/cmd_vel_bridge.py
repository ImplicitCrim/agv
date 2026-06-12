import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial


class CmdVelBridge(Node):

    def __init__(self):
        super().__init__('cmd_vel_bridge')

        self.ser = serial.Serial(
            '/dev/ttyUSB0',
            115200,
            timeout=1
        )

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        self.get_logger().info(
            "CMD_VEL Bridge Started"
        )

    def cmd_callback(self, msg):

        linear = msg.linear.x
        angular = msg.angular.z

        left = int(
            (linear - angular) * 70
        )

        right = int(
            (linear + angular) * 70
        )

        left = max(
            min(left, 100),
            -100
        )

        right = max(
            min(right, 100),
            -100
        )

        command = f"{left},{right}\n"

        self.ser.write(
            command.encode()
        )

    def stop_robot(self):

        for _ in range(20):

            self.ser.write(
                b"0,0\n"
            )

        self.get_logger().warn(
            "EMERGENCY STOP SENT"
        )

    def destroy_node(self):

        self.stop_robot()

        self.ser.close()

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = CmdVelBridge()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        node.get_logger().warn(
            "CTRL+C PRESSED"
        )

        node.stop_robot()

    finally:

        node.stop_robot()

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()