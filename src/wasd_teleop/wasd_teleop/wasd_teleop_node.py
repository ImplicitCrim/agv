import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import tty
import termios

class WasdTeleop(Node):

    def __init__(self):
        super().__init__('wasd_teleop')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear_speed = 0.10
        self.angular_speed = 0.30

        print("\n=== WASD TELEOP ===")
        print("W/S : Forward/Backward")
        print("A/D : Left/Right")
        print("SPACE : Stop")
        print("Q/E : Increase/Decrease linear speed")
        print("Z/C : Increase/Decrease angular speed")
        print("CTRL+C to quit\n")

    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return key

    def run(self):

        while rclpy.ok():

            key = self.get_key()

            msg = Twist()

            if key == 'w':
                msg.linear.x = self.linear_speed

            elif key == 's':
                msg.linear.x = -self.linear_speed

            elif key == 'a':
                msg.angular.z = self.angular_speed

            elif key == 'd':
                msg.angular.z = -self.angular_speed

            elif key == ' ':
                pass

            elif key == 'q':
                self.linear_speed += 0.05
                print(f"\nLinear Speed: {self.linear_speed:.2f}")

            elif key == 'e':
                self.linear_speed = max(
                    0.05,
                    self.linear_speed - 0.05
                )
                print(f"\nLinear Speed: {self.linear_speed:.2f}")

            elif key == 'z':
                self.angular_speed += 0.10
                print(f"\nAngular Speed: {self.angular_speed:.2f}")

            elif key == 'c':
                self.angular_speed = max(
                    0.10,
                    self.angular_speed - 0.10
                )
                print(f"\nAngular Speed: {self.angular_speed:.2f}")

            self.pub.publish(msg)

def main(args=None):

    rclpy.init(args=args)

    node = WasdTeleop()

    try:
        node.run()

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
