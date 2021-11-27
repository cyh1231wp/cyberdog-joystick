import struct
import os
from devices import detectJoystick
import grpc
import cyberdog_app_pb2
import cyberdog_app_pb2_grpc
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="joystick.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s: %(message)s",
)


class Vector3:
    x: float = 0
    y: float = 0
    z: float = 0

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        pass


MAX_SPEED = 16

stub = None
cyberdog_ip = "127.0.0.1"
speed_lv = 1
linear = Vector3(0, 0, 0)
angular = Vector3(0, 0, 0)


def init():
    global cyberdog_ip, stub
    channel = grpc.insecure_channel(cyberdog_ip + ":50051")
    print("Wait connect")
    try:
        grpc.channel_ready_future(channel).result(timeout=10)
    except grpc.FutureTimeoutError:
        print("Connect error, Timeout")
    else:
        logging.debug("grpc connected")
        # Get stub from channel
        stub = cyberdog_app_pb2_grpc.CyberdogAppStub(channel)


def setMode(control_mode):
    global stub
    response = stub.setMode(
        cyberdog_app_pb2.CheckoutMode_request(
            next_mode=cyberdog_app_pb2.ModeStamped(
                header=cyberdog_app_pb2.Header(
                    stamp=cyberdog_app_pb2.Timestamp(
                        sec=0, nanosec=0  # seem not need  # seem not need
                    ),
                    frame_id="",  # seem not need
                ),
                mode=cyberdog_app_pb2.Mode(
                    control_mode=control_mode,  # cyberdog_app_pb2.CheckoutMode_request.MANUAL
                    mode_type=0,  # seem not need
                ),
            ),
            timeout=10,
        )
    )
    succeed_state = False
    for resp in response:
        succeed_state = resp.succeed
        print("Execute " + str(control_mode) + ", result:" + str(succeed_state))


def setOrder(order_id):
    response = stub.setExtmonOrder(
        cyberdog_app_pb2.ExtMonOrder_Request(
            order=cyberdog_app_pb2.MonOrder(
                id=order_id,  # cyberdog_app_pb2.MonOrder.MONO_ORDER_HI_FIVE
                para=0,  # seem not need
            ),
            timeout=50,
        )
    )
    for resp in response:
        succeed_state = resp.succeed
        print("Execute " + str(order_id) + " order, result:" + str(succeed_state))


def setGait(gait_id=8):
    global stub
    response = stub.setPattern(
        cyberdog_app_pb2.CheckoutPattern_request(
            patternstamped=cyberdog_app_pb2.PatternStamped(
                header=cyberdog_app_pb2.Header(
                    stamp=cyberdog_app_pb2.Timestamp(
                        sec=0, nanosec=0  # seem not need  # seem not need
                    ),
                    frame_id="",  # seem not need
                ),
                pattern=cyberdog_app_pb2.Pattern(
                    gait_pattern=gait_id  # cyberdog_app_pb2.Pattern.GAIT_TROT
                ),
            ),
            timeout=10,
        )
    )
    for resp in response:
        succeed_state = resp.succeed
        print("Change gait, result:" + str(succeed_state))


def SendData():
    global stub
    stub.sendAppDecision(
        cyberdog_app_pb2.Decissage(
            twist=cyberdog_app_pb2.Twist(
                linear=cyberdog_app_pb2.Vector3(x=linear.x, y=linear.y, z=linear.z),
                angular=cyberdog_app_pb2.Vector3(x=angular.x, y=angular.y, z=angular.z),
            )
        )
    )


def GoForward(v):
    linear.x = 0.1 * speed_lv
    linear.y = 0
    angular.z = 0
    SendData()


def GoBack(v):
    linear.x = -0.1 * speed_lv
    linear.y = 0
    angular.z = 0
    SendData()


def GoLeft(v):
    linear.x = 0
    linear.y = 0.1 * speed_lv
    angular.z = 0
    SendData()


def GoRight(v):
    linear.x = 0
    linear.y = -0.1 * speed_lv
    angular.z = 0
    SendData()


def TurnLeft(v):
    linear.x = 0
    linear.y = 0
    angular.z = 0.1 * speed_lv
    SendData()


def TurnRight(v):
    linear.x = 0
    linear.y = 0
    angular.z = -0.1 * speed_lv
    SendData()


def Stop(v):
    linear.x = 0
    linear.y = 0
    angular.z = 0
    SendData()


def SpeedUp():
    global speed_lv
    speed_lv += 1
    speed_lv = min(speed_lv, MAX_SPEED)


def SpeedDown():
    global speed_lv
    speed_lv -= 1
    speed_lv = max(speed_lv, 1)


def joystickLoop(eventFile):
    FORMAT = "llHHI"
    EVENT_SIZE = struct.calcsize(FORMAT)
    with open(eventFile, "rb") as infile:
        while True:
            event = infile.read(EVENT_SIZE)
            _, _, t, c, v = struct.unpack(FORMAT, event)
            # print('---event---')
            print("t=%s,c=%s,v=%s" % (t, c, v))
            if t == 1 and v == 1:  # 功能按键
                if c == 315:  # 站立
                    setMode(cyberdog_app_pb2.CheckoutMode_request.MANUAL)
                elif c == 314:  # 趴下
                    setMode(cyberdog_app_pb2.CheckoutMode_request.DEFAULT)
                elif c == 308:  # Y：握手
                    setOrder(cyberdog_app_pb2.MonOrder.MONO_ORDER_HI_FIVE)
                elif c == 307:  # X：跳舞
                    setOrder(cyberdog_app_pb2.MonOrder.MONO_ORDER_DANCE)
                elif c == 304:  # A：作揖
                    setOrder(cyberdog_app_pb2.MonOrder.MONO_ORDER_BOW)
                elif c == 305:  # B：坐下
                    setOrder(cyberdog_app_pb2.MonOrder.MONO_ORDER_SIT)
                elif c == 312:  # 速度+1
                    SpeedUp()
                elif c == 313:  # 速度-1
                    SpeedDown()
                elif c == 310:
                    setGait()
                elif c == 311:
                    Stop()
                elif c == 17:
                    if v == 1:  # 下
                        setGait(cyberdog_app_pb2.Pattern.GAIT_SLOW_TROT)
                    elif v > 1:  # 上
                        setGait(cyberdog_app_pb2.Pattern.GAIT_TROT)
                elif c == 16:
                    if v == 1:  # 右
                        setGait(cyberdog_app_pb2.Pattern.GAIT_BOUND)
                    elif v > 1:  # 左
                        setGait(cyberdog_app_pb2.Pattern.GAIT_WALK)
            elif t == 3:
                if c == 5:
                    if v < 127:  # 前进
                        GoForward(v)
                    elif v > 129:  # 后退
                        GoBack(v)
                elif c == 2:
                    if v < 127:
                        TurnLeft(v)
                    elif v > 129:
                        TurnRight(v)
                elif c == 0:
                    if v < 127:
                        GoLeft(v)
                    elif v > 129:
                        GoRight(v)


def ros2():
    topic_name = ""
    while topic_name.strip() == "":
        topic_name = os.system("ros2 topic list | grep ip_notify")
    os.system(
        "ros2 topic pub --once "
        + topic_name
        + ' std_msgs/msg/String "data: 127.0.0.1:127.0.0.1"'
    )
    logging.debug('ros2 topic sent')


def main():
    ros2()
    init()
    logging.debug("search joystick...")
    joystickEvent = None
    while joystickEvent == None:
        joystickEvent = detectJoystick(["T-3"])
    logging.debug("find joystick and start loop")
    joystickLoop(joystickEvent)


main()
