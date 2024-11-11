import threading
import struct
import time
import socket
import os
import signal
import datetime

from utils import Lane, Simulator


def sim_oslink(devList, host_ip=('172.30.112.1', 10006), freq=1, loop=1):

    interrupt = True

    def heartBeat(sk):
        threading.Thread(target=start, args=(sk,)).start()

    sim = Simulator(loop=loop)
    for i in devList:
        sim.append_lane(i[0], i[1])

    def start(sk):
        dirct = 0
        while (interrupt):
            a = sim.next_gps()
            if (a == []):
                os.system('kill %d' % os.getpid())
            for i in a:
                now = datetime.datetime.now()
                packet = struct.pack("!IIIfI", i[0][2], now.hour, now.minute, float(
                    now.second + now.microsecond/1000000), 1)
                packet = packet + \
                    struct.pack("!ddI", i[0][0], i[0][1], int(i[1]))
                sk.sendto(packet, ('172.30.114.34', 12346))
                print("lat:{}, long:{}, speed:{}".format(
                    i[0][0], i[0][1], i[1]))
                dirct = (dirct + 1) % 2

            time.sleep(7 / 100)

    def signal_handler(signum, frame):
        interrupt = False
        os.system('kill %d' % os.getpid())

    signal.signal(signal.SIGINT, signal_handler)

    host_sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_sk.bind(host_ip)
    host_sk.sendto(b"hello world", ("172.30.114.34", 12346))

    heartBeat(host_sk)


if __name__ == '__main__':
    freq = 1
    devList = [
        (('172.30.112.1', 10006), Lane(((250, 0),
         (0, 0)), speed=50, freq=14)),
        (('172.30.112.1', 10006), Lane(((180, 0),
         (0, 0)), speed=30, freq=14)),
    ]
    sim_oslink(devList, freq=freq, loop=1)
