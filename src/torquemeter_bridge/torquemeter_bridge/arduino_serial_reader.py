import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import glob

class SerialReader(Node):

    def __init__(self):
        super().__init__('serial_reader')

        self.publisher_ = self.create_publisher(
            String,
            '/torque_raw',
            10
        )

        ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')

        if not ports:
            self.get_logger().error("No serial device found")
            return

        self.serial_port = serial.Serial(
            ports[0],
            115200,
            timeout=1
        )

        self.timer = self.create_timer(
            0.05,
            self.read_serial
        )

    def read_serial(self):

        if self.serial_port.in_waiting:

            line = self.serial_port.readline().decode(
                errors='ignore'
            ).strip()

            msg = String()
            msg.data = line

            self.publisher_.publish(msg)

            self.get_logger().info(
                f"Received: {line}"
            )

def main(args=None):

    rclpy.init(args=args)

    node = SerialReader()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':
    main()