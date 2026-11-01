#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务1 订阅者：订阅 /ball_pos 并打印 id / x / y"""

import rclpy
from rclpy.node import Node

from ball_msgs.msg import BallPos


class BallSubscriber(Node):
    def __init__(self):
        super().__init__('ball_subscriber')

        self.sub = self.create_subscription(
            BallPos, 'ball_pos', self.on_msg, 10
        )
        self.count = 0
        self.get_logger().info('订阅者启动，等待 /ball_pos ...')

    def on_msg(self, msg):
        self.count += 1
        self.get_logger().info(
            f'第 {self.count} 条 | 收到 id={msg.id} x={msg.x:.2f} y={msg.y:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = BallSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
