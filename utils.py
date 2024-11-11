from math import radians, cos, sin, asin, sqrt
import math
import datetime
import numpy


def distance(p1, p2):
    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    return (x ** 2 + y ** 2) ** 0.5


def haversine(start, end):
    lon1, lat1 = start
    lon2, lat2 = end
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


class Lane:
    speed = 30
    num = 1
    trace = numpy.array([[0, 0, 0]])
    sleep = 0
    dirct = 0

    def __init__(self, trace_point, speed=30, freq=1, sleep=0,dirct = 0):
        self.speed = speed
        speed = speed * 1000 / (3600.0 * freq)

        self.sleep = sleep
        self.dirct = dirct

        for i in range(len(trace_point) - 1):
            dist = distance(trace_point[i], trace_point[i + 1])

            t = dist / speed
            lonstep, latstep = self.calc_step(
                trace_point[i], trace_point[i + 1], t)
            self.trace = numpy.concatenate([self.trace, self.calc_trace(
                trace_point[i], trace_point[i + 1], lonstep, latstep)])

    def calc_step(self, p1, p2, t):
        s1 = p1[0] - p2[0]
        s2 = p1[1] - p2[1]
        return (s1 / t, s2 / t)

    def calc_trace(self, start, end, lonstep, latstep):
        trace = []
        s1, s2 = start
        e1, e2 = end

        def r(a, b): return a < b
        def t(a, b): return a > b
        def c(x, y): return r if (x < y) else t

        l1 = c(s1, e1)
        l2 = c(s2, e2)

        while l1(s1, e1) or l2(s2, e2):
            trace.append([s1, s2, 0])
            if l1(s1, e1):
                s1 -= lonstep
            if l2(s2, e2):
                s2 -= latstep
        return numpy.array(trace)

    def get_max_run(self):
        return self.trace.shape[0] - 1

    def simulate(self, run):
        if run < 1:
            run = 1
        if run > self.trace.shape[0] - 1:
            return (0.0, 0.0, 0.0)

        return (self.trace[run][0], self.trace[run][1], self.dirct)


class Simulator:
    lanes = []
    run = 0
    max_run = 0

    # loop : repeat time, -1 is not repeat.
    def __init__(self, loop=-1):
        self.loop = loop

    def append_lane(self, ip, lane):
        self.lanes.append({'ip': ip, 'lane': lane, 'last_post': (0.0, 0.0, 0.0),
                           'time': datetime.datetime.now().timestamp()})
        if (lane != 0):
            self.max_run = max(self.max_run, lane.get_max_run())

    def next_gps(self):
        r = []
        for i in self.lanes:
            if i['lane'] == 0:
                r.append(((0.0, 0.0, 0.0), 0, 0))
                continue

            t = i['lane'].simulate(self.run)
            if i['last_post'] == (0, 0, 0):
                i['last_post'] = t
                r.append((t, 0.0))
                continue

            d = distance(t, i['last_post'])
            n = datetime.datetime.now().timestamp() - i['time']
            speed = d / n  # m/s

            i['last_post'] = t
            i['time'] = datetime.datetime.now().timestamp()
            r.append((t, speed))

        self.run += 1
        if self.run > self.max_run and self.loop > 1:
            self.loop -= 1
            self.run = 0

        return r


if __name__ == '__main__':
    import time

    freq = 1
    lines1 = [Lane(((250, 0),
                    (0, 0)), speed=50, freq=14,dirct = 0), Lane(((180, 0),
                                                       (0, 0)), speed=30, freq=14,dirct=1)
              ]

    loop = -1  # negative = unlimited
    wait = 1 / freq
    packet_max = 11  # negative = unlimited
    ip = ('172.30.112.1', 10006)

    sim = Simulator()
    for i in lines1:
        sim.append_lane(ip, i)

    for i in range(100):
        a = sim.next_gps()
        for i in a:
            print(i)
        print("//////")
        time.sleep(0.1)