import struct
import os, subprocess
from devices import detectJoystick
import grpc
import cyberdog_app_pb2
import cyberdog_app_pb2_grpc
import threading
import time
import logging


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
speed_lv = 0
linear = Vector3(0, 0, 0)
angular = Vector3(0, 0, 0)
attitude = 0


def init():
    global cyberdog_ip, stub
    channel = grpc.insecure_channel(cyberdog_ip + ":50051")
    print("Wait connect")
    try:
        grpc.channel_ready_future(channel).result(timeout=10)
    except grpc.FutureTimeoutError:
        print("Connect error, Timeout")
    else:
        print("grpc connected")
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
    global stub, linear, angular
    print("start send thread")
    while True:
        if linear.x != 0 or linear.y != 0 or angular.z != 0:
            try:
                stub.sendAppDecision(
                    cyberdog_app_pb2.Decissage(
                        twist=cyberdog_app_pb2.Twist(
                            linear=cyberdog_app_pb2.Vector3(
                                x=linear.x, y=linear.y, z=linear.z
                            ),
                            angular=cyberdog_app_pb2.Vector3(
                                x=angular.x, y=angular.y, z=angular.z
                            ),
                        )
                    )
                )
            except:
                print('err')
        time.sleep(0.5)


def GoForward():
    linear.x = 0.1 * speed_lv
    linear.y = 0
    angular.z = 0


def GoBack():
    linear.x = -0.1 * speed_lv
    linear.y = 0
    angular.z = 0


def GoLeft():
    linear.x = 0
    linear.y = 0.1 * speed_lv
    angular.z = 0


def GoRight():
    linear.x = 0
    linear.y = -0.1 * speed_lv
    angular.z = 0


def TurnLeft():
    linear.x = 0
    linear.y = 0
    angular.z = 0.1 * speed_lv


def TurnRight():
    linear.x = 0
    linear.y = 0
    angular.z = -0.1 * speed_lv


def Stop():
    linear.x = 0
    linear.y = 0
    angular.z = 0


def SpeedUp():
    global speed_lv
    if speed_lv == 0:
        setGait()
    speed_lv += 1
    speed_lv = min(speed_lv, MAX_SPEED)


def SpeedDown():
    global speed_lv
    speed_lv -= 1
    speed_lv = max(speed_lv, 1)


def changeAttitude():
    global attitude
    if attitude == 0:
        setMode(cyberdog_app_pb2.CheckoutMode_request.MANUAL)
        attitude = 1
    elif attitude == 1:
        setMode(cyberdog_app_pb2.CheckoutMode_request.DEFAULT)
        attitude = 0


def joystickLoop(eventFile):
    FORMAT = "llHHI"
    EVENT_SIZE = struct.calcsize(FORMAT)
    subprocess.getoutput("chmod 664 " + eventFile)
    with open(eventFile, "rb") as infile:
        while True:
            event = infile.read(EVENT_SIZE)
            _, _, t, c, v = struct.unpack(FORMAT, event)
            # print('---event---')
            # print("t=%s,c=%s,v=%s" % (t, c, v))
            if t == 1 and v == 1:  # 功能按键
                if c == 305:  # A: 站立 趴下 自切换
                    changeAttitude()
                elif c == 307:  # B：握手
                    setOrder(cyberdog_app_pb2.MonOrder.MONO_ORDER_HI_FIVE)
                elif c == 304:  # C：跳舞
                    setOrder(cyberdog_app_pb2.MonOrder.MONO_ORDER_DANCE)
                # elif c == 304:  # A：作揖
                #     setOrder(cyberdog_app_pb2.MonOrder.MONO_ORDER_BOW)
                elif c == 308:  # D：坐下
                    setOrder(cyberdog_app_pb2.MonOrder.MONO_ORDER_SIT)
                elif c == 311:  # 速度+1
                    SpeedUp()
                elif c == 310:  # 速度-1
                    SpeedDown()
            elif t == 3:
                if c == 1:
                    if v == 0:  # 前进
                        GoForward()
                    elif v == 2:  # 后退
                        GoBack()
                    else:
                        Stop()
                elif c == 0:
                    if v == 0:
                        TurnLeft()
                    elif v == 2:
                        TurnRight()
                    else:
                        Stop()


def ros2():
    topic_name = ""
    while topic_name.find("ip_notify") == -1:
        topic_name = subprocess.getoutput("ros2 topic list | grep ip_notify")
        print(topic_name)
    ret = subprocess.getoutput(
        "ros2 topic pub --once "
        + topic_name
        + ' std_msgs/msg/String "data: 127.0.0.1:127.0.0.1"'
    )
    print(ret)
    print("ros2 topic sent")


def main():
    ros2()
    init()
    print("search joystick...")
    joystickEvent = None
    while joystickEvent == None:
        joystickEvent = detectJoystick(["R1"])
        time.sleep(1)
    print("find joystick and start loop")
    sendThread = threading.Thread(target=SendData)
    sendThread.daemon = 1
    sendThread.start()
    joystickLoop(joystickEvent)


main()
