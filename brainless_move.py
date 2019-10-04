import hbp_nrp_cle.tf_framework as nrp
from hbp_nrp_cle.robotsim.RobotInterface import Topic
import geometry_msgs.msg 

@nrp.MapRobotSubscriber("position", Topic('/gazebo/model_states', gazebo_msgs.msg.ModelStates))
@nrp.MapRobotSubscriber("camera", Topic('/husky/husky/camera', sensor_msgs.msg.Image))
#@nrp.MapVariable("initial_pose", global_key="initial_pose", initial_value=None)
@nrp.Neuron2Robot(Topic('/husky/husky/cmd_vel', geometry_msgs.msg.Twist))
def brainless_move(t, camera, position):   
    import Limbic_system 
    import math
    import random

    LEFT_LANDMARK_POS = (-1.8, -1.8, 0.1)
    RIGHT_LANDMARK_POS = (-1.8, 1.9, 0.1)

    # TODO
    def on_landmark(current_position, landmark_position, x_length, y_length):
        x_in_range = abs(landmark_position[0]) <= abs(current_position.x) <= (abs(landmark_position[0]) + x_length)
        y_in_range = abs(landmark_position[1]) <= abs(current_position.y) <= (abs(landmark_position[1]) + y_length))
        return x_in_range and y_in_range

    robot_position = position.value.pose[0].position
    clientLogger(on_landmark(robot_position, LEFT_LANDMARK_POS, 1, 1))

    def move_to(current_position, target_position):
        x_diff = target_position.x - current_position.x
        y_diff = target_position.y - current_position.y
        angle_to_target = math.atan2(y_diff, x_diff)
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=angle_to_target)) 

    def explore_left():
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=2)) 

    def explore_right():
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=2)) 


    # uses HSV (Hue Saturation Value) to detect the color.
    # 0 to 10 in the hue values represents Red.
    # The centre position of this colour is then detected.
    def move_to_colour(colour):
        tf = hbp_nrp_cle.tf_framework.tf_lib
        if (colour == 'red'): 
            lower_threshold = [0, 100, 100]
            upper_threshold = [10, 255, 255]
        if (colour == 'blue'):
            lower_threshold = [100,150,0]
            upper_threshold = [140,255,255]
        position = tf.find_centroid_hsv(camera.value, lower_threshold, upper_threshold) or (160, 120)
        azimuth, elevation = tf.cam.pixel2angle(position[0], position[1]) 
        angle_to_colour = float(azimuth) * math.pi / 180
        clientLogger.info(angle_to_colour)
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z= 10 * angle_to_colour))  

    return move_to_colour('red')

    image_results = hbp_nrp_cle.tf_framework.tf_lib.detect_red(image=camera.value)

    limbic_system = Limbic_system.Limbic_system()
    clientLogger.info(limbic_system.doStep(limbic_system.reward,
        limbic_system.placefieldGreen,
        limbic_system.placefieldBlue,
        limbic_system.on_contact_direction_Green,
        limbic_system.on_contact_direction_Blue,
        image_results.left,
        image_results.right,
        limbic_system.visual_reward_Green,
        limbic_system.visual_reward_Blue ))


    # if image_results.left > 0.05:
    #     return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=image_results.left * 10))
    # if image_results.right > 0.05:
    #     return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=2, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=image_results.right * 10))
