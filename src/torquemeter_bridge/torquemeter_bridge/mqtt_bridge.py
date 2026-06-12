import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import json
import paho.mqtt.client as mqtt

class MQTTBridge(Node):

    def __init__(self):

        super().__init__('mqtt_bridge')

        self.client = mqtt.Client()

        self.client.connect(
            "localhost",
            1883,
            60
        )

        self.sequence = 0

        self.subscription = self.create_subscription(
            String,
            '/torque_raw',
            self.callback,
            10
        )

    def callback(self,msg):

        self.sequence += 1

        payload = {
            "deviceId":"torque01",
            "sequence":self.sequence,
            "torque":msg.data,
            "unit":"Nm"
        }

        self.client.publish(
            "factory/sensor/torque",
            json.dumps(payload)
        )

def main(args=None):

    rclpy.init(args=args)

    node = MQTTBridge()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':
    main()