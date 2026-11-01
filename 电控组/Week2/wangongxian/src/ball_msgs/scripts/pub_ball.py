#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务1 发布者：每 0.5 秒（2 Hz）把 3 个球的坐标发到 /ball_pos"""

import rclpy
from rclpy.node import Node

from ball_msgs.msg import BallPos


class BallPublisher(Node):
    def __init__(self):
        super().__init__('ball_publisher')

        self.declare_parameter('rate', 2.0)
        rate = self.get_parameter('rate').value
        if rate <= 0.0:
            rate = 2.0

        self.balls = [
            (1, 2.0, 3.0),
            (2, 5.5, 8.0),
            (3, 9.0, 4.0),
        ]

        self.pub = self.create_publisher(BallPos, 'ball_pos', 10)
        self.timer = self.create_timer(1.0 / rate, self.tick)

        self.count = 0
        self.get_logger().info(f'发布者启动 | {rate} Hz | 话题 /ball_pos')

    def tick(self):
        self.count += 1
        for ball_id, x, y in self.balls:
            msg = BallPos()
            msg.id = ball_id
            msg.x = float(x)
            msg.y = float(y)
            self.pub.publish(msg)
            self.get_logger().info(
                f'第 {self.count} 轮 | 发送 id={msg.id} x={msg.x:.2f} y={msg.y:.2f}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = BallPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
