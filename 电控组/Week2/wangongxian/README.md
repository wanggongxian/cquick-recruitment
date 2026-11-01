# Week2 电控组 — wangongxian

## 一、三项任务完成情况

### 任务 1：BallPos 自定义消息 + 发布/订阅

- 包名 `ball_msgs`（ament_cmake），消息定义 `msg/BallPos.msg`：`int32 id` / `float32 x` / `float32 y`。
- 发布节点 `ball_publisher`，默认 2 Hz，频率由参数 `rate` 控制，可运行时改：

  ```bash
  ros2 run ball_msgs pub_ball.py --ros-args -p rate:=5.0
  ros2 param get /ball_publisher rate      # → Double value is: 5.0
  ```

- 订阅节点 `ball_subscriber`，收到一条打印一条。
- 验证命令：

  ```bash
  ros2 interface show ball_msgs/msg/BallPos
  ros2 topic info /ball_pos
  ros2 node list
  ```


### 任务 2：三个球依次导航

- 节点 `ball_nav`，订阅 `/ball_pos` 与 `/turtle1/pose`，发布 `/turtle1/cmd_vel`，10 Hz 闭环控制。
- 参数：`max_linear=0.8`、`max_angular=1.5`、`goal_tol=0.20`、`align_tol=0.30`。
- 三个球坐标：`(2.0, 3.0)`、`(5.5, 8.0)`、`(9.0, 4.0)`，按 1 → 2 → 3 顺序走。
- 实测到点误差：球 1 = 0.193，球 2 = 0.188，球 3 = 0.180（要求 ≤ 0.5）。
- 启动方式：

  ```bash
  ros2 run turtlesim turtlesim_node
  ros2 run ball_msgs pub_ball.py
  ros2 run ball_msgs nav_node.py
  ```

### 任务 3：串口与总线舵机笔记

- 见同目录 `03_串口与总线舵机笔记.md`。
- 回环测试未做：手上没有舵机硬件。


---

## 二、三种通信方式对比

| 通信方式 | 通信模型 | 特点 | 足球机器人里可能的用途 |
|---|---|---|---|
| 话题 Topic | 发布 / 订阅，异步 | 一对多，发完不管，持续流式 | 摄像头图像、雷达点云、`/cmd_vel` |
| 服务 Service | 请求 / 响应，同步 | 一问一答，调用方阻塞等待 | 清屏、切换模式、标定 |
| 动作 Action | 目标 / 反馈 / 结果 | 长时间任务，可中途取消 | 定点导航、抓球、回到起始位 |

我在任务 2 里实际用到的服务调用：

```bash
ros2 service call /clear std_srvs/srv/Empty {}
```

调一次、返回一次就结束，不像话题那样一直推数据。


---

## 三、差速底盘三公式

```
v = (vL + vR) / 2
w = (vR - vL) / L
r = v / w
```

- `vL`、`vR`：左右轮线速度；`L`：两轮间距；`v`：车体前进速度；`w`：转向角速度；`r`：转弯半径。
- 两轮同速 → `vR - vL = 0` → `w = 0` → 走直线。
- 右轮快左轮慢 → `w > 0` → 逆时针（左转）。
- 两轮反向等速 → `v = 0`、`w = 2vR / L` → 原地打转。



---

## 四、给下周自己的提醒

下周要更有积极性

---

## 五、截图说明

| 文件 | 内容 |
|---|---|
| `01_interface_show.png` | 编译成功 + `ros2 interface show ball_msgs/msg/BallPos` 输出三行字段 |
| `01_发布订阅分屏.png` | 左右分屏，发布端与订阅端同时刷屏 |
| `01_话题信息.png` | `ros2 topic info /ball_pos`，Publisher 1 / Subscription 1 |
| `01_改频率_5Hz.png` | `ros2 param get /ball_publisher rate` 返回 5.0 |
| `02_三个球轨迹.png` | 乌龟轨迹 + 导航日志 + 节点列表 + 姓名时间戳，一次截全 |
| `02_运行日志.png` | 同上，重点看 `到达第 N 个球 … 误差 x.xxx` 与「三点全部到达」 |

