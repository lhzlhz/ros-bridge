#!/usr/bin/env python

#
# Copyright (c) 2018 Intel Labs.
#
# authors: Frederik Pasch (frederik.pasch@intel.com)
#
"""
Classes to handle Carla gnsss
"""

import numpy

import tf

from sensor_msgs.msg import NavSatFix

from carla_ros_bridge.sensor import Sensor
import carla_ros_bridge.transforms as trans


class Gnss(Sensor):

    """
    Actor implementation details for gnss sensor
    """

    def __init__(self, carla_actor, parent, topic_prefix=None, append_role_name_topic_postfix=True):
        """
        Constructor

        :param carla_actor: carla actor object
        :type carla_actor: carla.Actor
        :param parent: the parent of this
        :type parent: carla_ros_bridge.Parent
        :param topic_prefix: the topic prefix to be used for this actor
        :type topic_prefix: string
        :param append_role_name_topic_postfix: if this flag is set True,
            the role_name of the actor is used as topic postfix
        :type append_role_name_topic_postfix: boolean
        """
        if topic_prefix is None:
            topic_prefix = 'gnss'
        super(Gnss, self).__init__(carla_actor=carla_actor,
                                   parent=parent,
                                   topic_prefix=topic_prefix,
                                   append_role_name_topic_postfix=append_role_name_topic_postfix)

    def get_tf_msg(self):
        """
        Function (override) to modify the tf messages sent by this gnss.

        The gnss transformation has to be altered:
        for some reasons gnss sends already a rotated cloud,
        so herein, we need to ignore pitch and roll

        :return: the filled tf message
        :rtype: geometry_msgs.msg.TransformStamped
        """
        tf_msg = super(Gnss, self).get_tf_msg()
        rotation = tf_msg.transform.rotation
        quat = [rotation.x, rotation.y, rotation.z, rotation.w]
        dummy_roll, dummy_pitch, yaw = tf.transformations.euler_from_quaternion(
            quat)
        # set roll and pitch to zero
        quat = tf.transformations.quaternion_from_euler(0, 0, yaw)
        tf_msg.transform.rotation = trans.numpy_quaternion_to_ros_quaternion(
            quat)
        return tf_msg

    def sensor_data_updated(self, carla_gnss_event):
        """
        Function to transform a received gnss event into a ROS NavSatFix message

        :param carla_gnss_event: carla gnss event object
        :type carla_gnss_event: carla.GnssEvent
        """
        navsatfix_msg = NavSatFix()
        navsatfix_msg.header = self.get_msg_header(use_parent_frame=False)
        navsatfix_msg.latitude = carla_gnss_event.latitude
        navsatfix_msg.longitude = carla_gnss_event.longitude
        navsatfix_msg.altitude = carla_gnss_event.altitude
        self.publish_ros_message(
            self.topic_name() + "/gnss", navsatfix_msg)
