import hbp_nrp_cle.tf_framework as nrp
from hbp_nrp_cle.robotsim.RobotInterface import Topic
import geometry_msgs.msg 
from gazebo_msgs.srv import SetModelState, GetModelState
from gazebo_msgs.msg import ContactsState, ModelStates
import rospy 
import sys
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
import logging 

rospy.wait_for_service("/gazebo/set_model_state")
service_proxy_set_state = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState, persistent=True)
@nrp.MapRobotSubscriber('contacts', Topic('/gazebo/contact_point_data', ContactsState))
@nrp.MapRobotSubscriber("position", Topic('/gazebo/model_states', gazebo_msgs.msg.ModelStates))
@nrp.MapRobotSubscriber("camera", Topic('/husky/husky/camera', sensor_msgs.msg.Image))
@nrp.MapVariable("init_distance_to_left_landmark", global_key="init_distance_to_left_landmark", initial_value=None)
@nrp.MapVariable("init_distance_to_right_landmark", global_key="init_distance_to_right_landmark", initial_value=None)
@nrp.MapVariable("set_model_state_srv", initial_value=service_proxy_set_state)

@nrp.Neuron2Robot(Topic('/husky/husky/cmd_vel', geometry_msgs.msg.Twist))
def brainless_move(t, camera, position, set_model_state_srv, contacts,
                   init_distance_to_left_landmark, init_distance_to_right_landmark):   
    import math
    import random
    import Limbic_system
    from helper import Results, Coordinates, detect_white
    from hbp_nrp_cle.tf_framework.tf_lib import detect_red

    # centre coordinates of landmarks
    GREEN_PLACEFIELD_POS = (-2.5, -1.9, 0.03)
    BLUE_PLACEFIELD_POS = (-2.5, 1.95, 0.03)
    LEFT_SPHERE_POS  = (-2.595, -2.085, 0.225)
    RIGHT_SPHERE_POS = (-2.5, 1.9, 0.4)
    PLACEFIELD_LENGTH = 2.0
    ROBOT_ID = 'husky'

    def get_position(object_name):
        return position.value.pose[position.value.name.index(object_name)].position


    # assumes centre position is given for placefield
    def on_placefield(object_name, placefield_position, x_length, y_length):
        object_position = get_position(object_name)
        max_x = placefield_position[0] + x_length / 2
        min_x = placefield_position[0] - x_length / 2
        max_y = placefield_position[1] + y_length / 2
        min_y = placefield_position[1] - y_length / 2  
        return (min_x < object_position.x < max_x) and (min_y < object_position.y < max_y)


    def move_to(current_position, target_position):
        x_diff = target_position.x - current_position.x
        y_diff = target_position.y - current_position.y
        angle_to_target = math.atan2(y_diff, x_diff)
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=angle_to_target)) 


    def explore_left():
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=2)) 


    def explore_right():
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=2))


    def move_to_colour(colour):
        tf = hbp_nrp_cle.tf_framework.tf_lib
        if (colour == 'red'): 
            lower_threshold = [0, 100, 100]
            upper_threshold = [10, 255, 255]
        if (colour == 'blue'):
            lower_threshold = [100,150,0]
            upper_threshold = [140,255,255]
        if  (colour == 'green'):
            lower_threshold = [50, 160, 220]
            upper_threshold = [60, 175, 240]
        if (colour == 'white'): 
            lower_threshold = [0, 0, 252]
            upper_threshold = [0, 0, 255]
        position = tf.find_centroid_hsv(camera.value, lower_threshold, upper_threshold) or (160, 120)
        azimuth, elevation = tf.cam.pixel2angle(position[0], position[1]) 
        angle_to_colour = float(azimuth) * math.pi / 180
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z= 10 * angle_to_colour))  


    def change_position(object_name, new_position, scale=1):
        ms_msg = gazebo_msgs.msg.ModelState()
        ms_msg.reference_frame = 'world'
        ms_msg.model_name = object_name
        ms_msg.scale.x = ms_msg.scale.y = ms_msg.scale.z = scale
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
         return math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2)


    def normalise_distance(distance, maximum, minimum=0):
        try: 
            result = 1 - ((distance - minimum) / (maximum - minimum))
            return max(0, result)
        except ZeroDivisionError:
            return None 


    distance_to_right_landmark = 0
    distance_to_left_landmark  = 0
    norm_distance_to_left_landmark  = 0
    norm_distance_to_right_landmark = 0
    left_landmark_pos  = Coordinates(LEFT_SPHERE_POS[0], LEFT_SPHERE_POS[1], LEFT_SPHERE_POS[2])
    right_landmark_pos = Coordinates(RIGHT_SPHERE_POS[0], RIGHT_SPHERE_POS[1], RIGHT_SPHERE_POS[2])
    robot_pos = get_position(ROBOT_ID)
    if init_distance_to_left_landmark.value is None:
        init_distance_to_left_landmark.value = distance_between_points(robot_pos, left_landmark_pos)   
    if init_distance_to_right_landmark.value is None:
        init_distance_to_right_landmark.value = distance_between_points( robot_pos, right_landmark_pos)  
    if sees_landmark_left(camera.value):
        distance_to_left_landmark = distance_between_points(robot_pos, left_landmark_pos)
        norm_distance_to_left_landmark = normalise_distance(distance_to_left_landmark, init_distance_to_left_landmark.value)
    if sees_landmark_right(camera.value):
        distance_to_right_landmark = distance_between_points(robot_pos, right_landmark_pos)
        norm_distance_to_right_landmark = normalise_distance(distance_to_right_landmark, init_distance_to_right_landmark.value)

    reward = got_reward()
    placefield_green = on_placefield(ROBOT_ID, GREEN_PLACEFIELD_POS, PLACEFIELD_LENGTH, PLACEFIELD_LENGTH)
    placefield_blue = on_placefield(ROBOT_ID, BLUE_PLACEFIELD_POS, PLACEFIELD_LENGTH, PLACEFIELD_LENGTH)
    touching_landmark_green = is_touching_landmark('left_sphere')
    touching_landmark_blue  = is_touching_landmark('right_sphere')
    sees_landmark_green = norm_distance_to_left_landmark
    sees_landmark_blue  = norm_distance_to_right_landmark
    visual_reward_green = sees_reward_left(camera.value)
    visual_reward_blue  = sees_reward_right(camera.value)

    clientLogger.info(reward,
                      placefield_green,
                      placefield_blue,
                      touching_landmark_green,
                      touching_landmark_blue,             
                      sees_landmark_green,
                      sees_landmark_blue,
                      visual_reward_green,
                      visual_reward_blue)

                        
    limbic_system = Limbic_system.Limbic_system()
    limbic_output = limbic_system.doStep(reward,
                        placefield_green,
                        placefield_blue,
                        touching_landmark_green,
                        touching_landmark_blue,             
                        sees_landmark_green,
                        sees_landmark_blue,
                        visual_reward_green,
                        visual_reward_blue)

    clientLogger.info(limbic_output)
    return move_to_colour('white')
