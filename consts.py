import os
import pathlib

DEFAULT_DELAY = 5.0
DEFAULT_TURNTABLE_PERIOD = 31
DEFAULT_PHOTOS_PER_SCAN = 18
DEFAULT_TURNTABLE_PIN = 6
DEFAULT_CAM_1_PIN = 31
DEFAULT_CAM_2_PIN = 10
DEFAULT_CAM_3_PIN = 11
DEFAULT_CAM_4_PIN = 31
DEFAULT_FTP_HOST = 'FTPPartner.wayfair.com'

CONFIG_FILE = os.path.join(str(pathlib.Path.home()), '.quickcapture.conf')

app = None
