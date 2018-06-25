import time


class Turntable():
    def __init__(self, period=31, photos_per_scan=18, delay=5):
        self.period = period
        self.photos_per_scan = photos_per_scan
        self.enable_rotation_duration = self.period / photos_per_scan
        self.delay = delay

    def rotate_slice(self):
        print('Rotating table for {} seconds'.format(self.enable_rotation_duration))
        time.sleep(self.enable_rotation_duration)
        print('Delay for {} seconds'.format(self.delay))
        time.sleep(self.delay)
