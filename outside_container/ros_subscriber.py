#!/usr/bin/env python
'''
This file is to be run outside the docker container on the host machine prior to starting the experiment.
It sets the ROS environment variables to the values found inside the container.
It subscribes to the topic "/plot_data" from the simulation and calls the plot function when interrupted.
ROS must be installed on the host machine to run this program.
'''

import rospy
from std_msgs.msg import String
from rosgraph_msgs.msg import Clock
import pylab as pl
import os
import plotter


def callback(data):
    f.write(data.data + '\n')
    print(data.data)

def listener():
    # anonymous=True allows multiple listeners at once 
    rospy.init_node('plot_listener', anonymous=True)
    rospy.Subscriber('plot_data', String, callback)
    rospy.spin()

if __name__ == '__main__':
    f = open("plot_data.log", "w+")
    os.environ["ROS_IP"] = "172.19.0.3"
    os.environ["ROS_MASTER_URI"] = "http://172.19.0.3:11311"
    listener()
    f.close()
    plotter.plot()