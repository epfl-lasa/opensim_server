#!/usr/bin/env python
import rospy
import rospkg
import tf
import threading
from multiprocessing import Lock
from os.path import join
from os.path import exists
from os import makedirs
import csv


class Recorder(object):
    def __init__(self):
        rospack = rospkg.RosPack()
        self.data_dir = join(rospack.get_path("opensim_server"), "data")
        if not exists(self.data_dir):
            makedirs(self.data_dir)

        self.recording = False
        self.header = []
        self.recorded_data = []
        self.lock = Lock()
        self.listener = tf.TransformListener()

    def init_header(self, tf_list):
        for name in tf_list:
            self.header.append(name + ".x")
            self.header.append(name + ".y")
            self.header.append(name + ".z")

    def start_recording(self):
        with self.lock:
            self.recording = True
            self.recorded_data = []

    def stop_recording(self, savefile):
        savefile = join(self.data_dir, savefile + ".csv")
        with self.lock:
            self.recording = False
            with open(savefile, 'w') as f:
                writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(self.header)
                for row in self.recorded_data:
                    writer.writerow(row)
        return savefile

    def record_transforms(self, tf_list, base_frame):
        rate = rospy.Rate(30)
        while not rospy.is_shutdown():
            with self.lock:
                if self.recording:
                    data = []
                    for name in tf_list:
                        try:
                            (trans,rot) = self.listener.lookupTransform(name, base_frame, rospy.Time(0))
                            data.append(trans[0])
                            data.append(trans[1])
                            data.append(trans[2])
                        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                            rospy.logwarn(name + " not visible")
                            data = []
                            break
                    if data:
                        self.recorded_data.append(data)
            rate.sleep()

    def run(self, tf_list, base_frame):
        self.init_header(tf_list)
        thread = threading.Thread(target=self.record_transforms, args=(tf_list, base_frame,))
        thread.start()
            