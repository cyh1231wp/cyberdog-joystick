import struct
from devices import detectJoystick


def joystickLoop(eventFile):
    FORMAT = "llHHI"
    EVENT_SIZE = struct.calcsize(FORMAT)
    with open(eventFile, "rb") as infile:
        while True:
            event = infile.read(EVENT_SIZE)
            _, _, t, c, v = struct.unpack(FORMAT, event)
            # print('---event---')
            print("t=%s,c=%s,v=%s" % (t, c, v))


def main():
    print('search joystick...')
    joystickEvent = None
    while joystickEvent == None:
        joystickEvent = detectJoystick(["T-3"])
    print('find joystick and start loop')
    joystickLoop(joystickEvent)


main()
