#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务2：订阅 /ball_pos，收齐 3 个球后按 1->2->3 顺序闭环走过去"""

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from ball_msgs.msg import BallPos


class BallNav(Node):
    def __init__(self):
        super().__init__('ball_nav')

        # ---------- 参数：调参不用改代码 ----------
        self.declare_parameter('max_linear', 0.8)    # 最大线速度 m/s
        self.declare_parameter('max_angular', 1.5)   # 最大角速度 rad/s
        self.declare_parameter('goal_tol', 0.20)     # 到点阈值（评分要求 <=0.5）
        self.declare_parameter('align_tol', 0.30)    # 对准阈值 rad

        self.max_linear = self.get_parameter('max_linear').value
        self.max_angular = self.get_parameter('max_angular').value
        self.goal_tol = self.get_parameter('goal_tol').value
        self.align_tol = self.get_parameter('align_tol').value

        # ---------- 状态 ----------
        self.balls = {}          # {id: (x, y)}
        self.order = [1, 2, 3]   # 顺序：必须 1 -> 2 -> 3
        self.idx = 0             # 当前走到第几个
        self.started = False     # 收齐 3 个球才开始
        self.finished = False    # 全部走完
        self.pose = None         # 最新位姿
        self.reached = []        # 各点实际误差

        # ---------- 通信 ----------
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(BallPos, 'ball_pos', self.on_ball, 10)
        self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)

        # 控制循环 10 Hz
        self.create_timer(0.1, self.control)

        self.get_logger().info('导航节点启动，等待 3 个球坐标 ...')

    # ================= 回调 =================
    def on_ball(self, msg):
        self.balls[msg.id] = (msg.x, msg.y)
        if not self.started and len(self.balls) >= 3:
            self.started = True
            self.get_logger().info(f'收齐 3 个球：{self.balls}，开始导航')
            self._log_target()

    def on_pose(self, msg):
        self.pose = msg

    # ================= 控制 =================
    def control(self):
        if self.finished or not self.started or self.pose is None:
            return

        b_id = self.order[self.idx]
        tx, ty = self.balls[b_id]
        x, y, theta = self.pose.x, self.pose.y, self.pose.theta

        dx = tx - x
        dy = ty - y
        dist = math.hypot(dx, dy)          # 到目标的距离

        # ---------- 到点判定 ----------
        if dist < self.goal_tol:
            self.get_logger().info(
                f'到达第 {b_id} 个球，实际坐标 ({x:.3f}, {y:.3f})，误差 {dist:.3f}')
            self.reached.append(dist)
            self.idx += 1

            if self.idx >= len(self.order):
                self.pub.publish(Twist())          # 全零 = 停车
                self.finished = True
                self.get_logger().info('=' * 45)
                self.get_logger().info('三点全部到达，任务完成')
                for i, e in enumerate(self.reached, start=1):
                    self.get_logger().info(f'球 {i} 最终误差: {e:.3f}')
                return

            self._log_target()
            return

        # ---------- 算方位误差 ----------
        target_angle = math.atan2(dy, dx)
        err = target_angle - theta
        # 归一化到 [-pi, pi]，不做这步乌龟会原地画圈
        err = math.atan2(math.sin(err), math.cos(err))

        tw = Twist()
        if abs(err) > self.align_tol:
            # 角度差太大：原地转，先对准
            tw.linear.x = 0.0
            tw.angular.z = self._clamp(2.0 * err, self.max_angular)
        else:
            # 对准了：边走边微调，越近越慢
            tw.linear.x = min(self.max_linear, 1.2 * dist)
            tw.angular.z = self._clamp(2.0 * err, self.max_angular)
        self.pub.publish(tw)

    # ================= 工具 =================
    @staticmethod
    def _clamp(v, m):
        return max(-m, min(m, v))

    def _log_target(self):
        b_id = self.order[self.idx]
        tx, ty = self.balls[b_id]
        self.get_logger().info(f'目标 {b_id} 号球：({tx:.2f}, {ty:.2f})')


def main(args=None):
    rclpy.init(args=args)
    node = BallNav()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.pub.publish(Twist())      # 退出前停车
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
