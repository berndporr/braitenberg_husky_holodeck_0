import hbp_nrp_cle.tf_framework as nrp
from hbp_nrp_cle.robotsim.RobotInterface import Topic
import geometry_msgs.msg 
from gazebo_msgs.srv import SetModelState, GetModelState, SetVisualProperties
from gazebo_msgs.msg import ContactsState, ModelStates
import rospy
import sys
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
import logging

rospy.wait_for_service('/gazebo/set_visual_properties', 1)
set_visual_props = rospy.ServiceProxy('/gazebo/set_visual_properties', SetVisualProperties, persistent=True)
service_proxy_set_state = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState, persistent=True)
constants = {"distance_to_left_landmark": None, "distance_to_right_landmark": None, "model_state": None}

@nrp.MapVariable("set_visual_properties", initial_value=set_visual_props)
@nrp.MapVariable("set_model_state_srv", initial_value=service_proxy_set_state)
@nrp.MapVariable("constants", global_key="constants", initial_value=constants)
@nrp.MapVariable("limbic_system", global_key="limbic_system", initial_value=None)
@nrp.MapRobotSubscriber('contacts', Topic('/gazebo/contact_point_data', ContactsState))
@nrp.MapRobotSubscriber("position", Topic('/gazebo/model_states', gazebo_msgs.msg.ModelStates))
@nrp.MapRobotSubscriber("camera", Topic('/husky/husky/camera', sensor_msgs.msg.Image))
@nrp.MapRobotPublisher("plot_data", Topic("plot_data", std_msgs.msg.String ))
@nrp.Neuron2Robot(Topic('/husky/husky/cmd_vel', geometry_msgs.msg.Twist))
def brainless_move(t, camera, position, set_model_state_srv, contacts, limbic_system, set_visual_properties, constants, plot_data):   
    import math
    import random
    import Limbic_system
    reload(Limbic_system)
    import helper
    from helper import Results, Coordinates, detect_white
    reload(helper)
    from hbp_nrp_cle.tf_framework.tf_lib import detect_red
    import inspect
    import os
    import tf
    from tf.transformations import euler_from_quaternion, quaternion_from_euler
    import re
    import rqt_plot
    
    # centre coordinates of field areas
    GREEN_PLACEFIELD_POS = (-6.5, -4.7, 0.03)
    BLUE_PLACEFIELD_POS = (-6.5, 4.7, 0.03)
    LEFT_SPHERE_POS  = (-7, -5, 0.5)
    RIGHT_SPHERE_POS = (-7, 5, 0.5)
    PLACEFIELD_LENGTH = 5
    ROBOT_ID = 'husky'


    def get_position(object_name):
        return position.value.pose[position.value.name.index(object_name)].position

    def get_yaw(object_name):
        quaternions = position.value.pose[position.value.name.index(object_name)].orientation
        angles = euler_from_quaternion((quaternions.x, quaternions.y, quaternions.z, quaternions.w))
        return angles[2]

    # assumes centre position is given for placefield
    def on_placefield(object_name, placefield_position, x_length, y_length):
        object_position = get_position(object_name)
        max_x = placefield_position[0] + x_length / 2
        min_x = placefield_position[0] - x_length / 2
        max_y = placefield_position[1] + y_length / 2
        min_y = placefield_position[1] - y_length / 2  
        return (min_x < object_position.x < max_x) and (min_y < object_position.y < max_y)
        

    def move_to(current_pos, target_pos, current_angle=0, speed=1):    
        x_diff = target_pos.x - current_pos.x 
        y_diff = target_pos.y - current_pos.y 
        target_angle = (math.atan2(y_diff, x_diff)*180)/math.pi
        current_angle = (current_angle*180)/math.pi
        direction = 0
        upper_angle = target_angle + 180
        if (upper_angle > 180):
            upper_angle = upper_angle - 360
        if (target_angle < 0):
            if ((current_angle < upper_angle) and (current_angle > target_angle + 1)): 
                direction = -3
            elif (current_angle > target_angle -0.5):
                direction = 0
            else: 
                direction = 3
        else: 
            if ((current_angle > upper_angle) and (current_angle < target_angle -1)):
                direction = -3
            elif (current_angle > target_angle + 0.5):
                direction = 0

            else:
                direction = 3

        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=direction))

            
    def explore(direction, speed=0.5):
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=speed, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=direction)) 


    def move_to_colour(colour, speed=1):
        tf = hbp_nrp_cle.tf_framework.tf_lib
        if (colour == 'red'): 
            lower_threshold = [0, 100, 100]
            upper_threshold = [10, 255, 255]
        if (colour == 'blue'):
            lower_threshold = [100,150,0]
            upper_threshold = [140,255,255]
        if  (colour == 'green'):
            lower_threshold = [50, 150, 200]
            upper_threshold = [60, 180, 240]
        if (colour == 'white'): 
            lower_threshold = np.array([0, 0, 252])
            upper_threshold = np.array([45, 13, 255])
        position = tf.find_centroid_hsv(camera.value, lower_threshold, upper_threshold) or (160, 120)
        azimuth, elevation = tf.cam.pixel2angle(position[0], position[1]) 
        angle_to_colour = float(azimuth) * math.pi / 180
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=speed, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z= 10 * angle_to_colour))  


    def reset_robot_position(new_position):
        ms_msg = gazebo_msgs.msg.ModelState()
        ms_msg.reference_frame = 'world'
        ms_msg.model_name = ROBOT_ID
        ms_msg.scale.x = ms_msg.scale.y = ms_msg.scale.z = 1
        ms_msg.pose.orientation.x = 0
        ms_msg.pose.orientation.y = 0
        ms_msg.pose.orientation.z = 1
        ms_msg.pose.position = new_position
        response = set_model_state_srv.value(ms_msg)
        return response


    def hide_food():
        sphere_position = position.value.pose[position.value.name.index('sphere_0')].position
        sphere_position.z = -1
        change_position('sphere_0', sphere_position, scale=0.2)

    
    def show_food():
        sphere_position = position.value.pose[position.value.name.index('sphere_0')].position
        sphere_position.z = 0.3
        change_position('sphere_0', sphere_position, scale=0.2)

    
    def sees_reward(image):
        return nrp.tf_lib.detect_red(image).left > 0.001 or nrp.tf_lib.detect_red(image).right > 0.001

    def sees_reward_left(image): 
        return nrp.tf_lib.detect_red(image).left > 0.001 
  
  
    def sees_reward_right(image):
        return nrp.tf_lib.detect_red(image).right > 0.001
    

    def sees_landmark_left(image):
        return detect_white(image).left > 0.001


    def sees_landmark_right(image): 
        return detect_white(image).right > 0.001


    def is_touching_landmark(landmark_name):
        try:
            collision1 = contacts.value.states[0].collision1_name
            collision2 = contacts.value.states[0].collision2_name
            if landmark_name in collision1 or landmark_name in collision2:
                return True
            return False
        except IndexError:
            return False


    def collision():
        for collision in contacts.value.states:
            return bool(re.search("box_[0,1,3,4]|high_concrete_wall", collision.collision1_name) or 
                        re.search("box_[0,1,3,4]|high_concrete_wall", collision.collision2_name))


    def got_reward():
        if sees_reward(camera.value) and is_touching_landmark('left_sphere'):
            clientLogger.info("Got Reward!")
            return True
        return False


    def distance_between_objects(object1, object2):
        pos1 = get_position(object1)
        pos2 = get_position(object2)
        return math.sqrt((pos2.x - pos1.x)**2 + (pos2.y - pos1.y)**2)
    

    def distance_between_points(point1, point2):
        # -0.6 for robot length
        return math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2) -0.6


    def normalise_distance(distance, maximum, minimum=0):
        try: 
            result = 1 - ((distance - minimum) / (maximum - minimum))
            return max(0, result)
        except ZeroDivisionError:
            return None 

    def reset_reward():
        try:
            set_visual_properties.value(model_name='left_sphere', link_name='link',
                                        visual_name='visual',
                                        property_name='material:script:name',
                                        property_value='Gazebo/White')
        except:
            clientLogger.info("ROSPY ERROR")

    distance_to_right_landmark = 0
    distance_to_left_landmark  = 0
    norm_distance_to_left_landmark  = 0
    norm_distance_to_right_landmark = 0
    left_landmark_pos  = Coordinates(LEFT_SPHERE_POS[0], LEFT_SPHERE_POS[1], LEFT_SPHERE_POS[2])
    right_landmark_pos = Coordinates(RIGHT_SPHERE_POS[0], RIGHT_SPHERE_POS[1], RIGHT_SPHERE_POS[2])
    robot_pos = get_position(ROBOT_ID)
    robot_angle = get_yaw(ROBOT_ID)

    if (constants.value["model_state"] is None):
        constants.value["model_state"] = position.value
        constants.value["distance_to_left_landmark"] = distance_between_points(robot_pos, left_landmark_pos)   
        constants.value["distance_to_right_landmark"] = distance_between_points(robot_pos, right_landmark_pos)  
    if (limbic_system.value is None):
        limbic_system.value = Limbic_system.Limbic_system()

    initial_robot_position = constants.value["model_state"].pose[position.value.name.index(ROBOT_ID)].position
    distance_to_left_landmark  = distance_between_points(robot_pos, left_landmark_pos)
    distance_to_right_landmark = distance_between_points(robot_pos, right_landmark_pos)
    norm_distance_to_left_landmark  = normalise_distance(distance_to_left_landmark, constants.value["distance_to_left_landmark"] )
    norm_distance_to_right_landmark = normalise_distance(distance_to_right_landmark, constants.value["distance_to_right_landmark"] )

    limbic_system = limbic_system.value
    reward = int(got_reward()) 
    placefield_green = int(on_placefield(ROBOT_ID, GREEN_PLACEFIELD_POS, PLACEFIELD_LENGTH, PLACEFIELD_LENGTH))
    placefield_blue = int(on_placefield(ROBOT_ID, BLUE_PLACEFIELD_POS, PLACEFIELD_LENGTH, PLACEFIELD_LENGTH))
    touching_landmark_green = int(is_touching_landmark('left_sphere') )
    touching_landmark_blue  = int(is_touching_landmark('right_sphere'))
    sees_landmark_green = min(1, norm_distance_to_left_landmark*2) 
    sees_landmark_blue  = min(1, norm_distance_to_right_landmark*2)
    visual_reward_green = int(sees_reward(camera.value) and placefield_green)
    visual_reward_blue  = int(sees_reward(camera.value) and placefield_blue)

    # clientLogger.info("INPUT : ", reward,
    #                   placefield_green,
    #                   placefield_blue,
    #                   touching_landmark_green,
    #                   touching_landmark_blue,             
    #                   sees_landmark_green,
    #                   sees_landmark_blue,
    #                   visual_reward_green,
    #                   visual_reward_blue)

    limbic_output = limbic_system.doStep(reward,
                        placefield_green,
                        placefield_blue,
                        touching_landmark_green,
                        touching_landmark_blue,             
                        sees_landmark_green,
                        sees_landmark_blue,
                        visual_reward_green,
                        visual_reward_blue)

    plot_msg = str(sees_landmark_green) + ',' + \
                str(sees_landmark_blue) + ',' +\
                str(placefield_green) + ',' +\
                str(placefield_blue) + ',' +\
                str(limbic_system.mPFC_Green) + ',' +\
                str(limbic_system.DRN) + ',' +\
                str(limbic_system.core_weight_lg2lg) + ',' +\
                str(limbic_system.VTA) + ',' +\
                str(limbic_system.CoreGreenOut)
    plot_data.send_message(plot_msg)

    if reward:
        reset_robot_position(initial_robot_position)
        
    clientLogger.info("OUTPUT: ", limbic_output)
    if collision():
        reset_robot_position(initial_robot_position)
        reset_reward()
    if (limbic_output[0] > 0):
        return move_to(robot_pos, right_landmark_pos, robot_angle, speed=limbic_output[0])
    elif (limbic_output[1] > 0):
        return move_to(robot_pos, left_landmark_pos, robot_angle, speed=limbic_output[1])
    else: 
        direction = limbic_output[2] - limbic_output[3]
        direction = min(2, direction*10)
        return explore(direction, speed=1)    
