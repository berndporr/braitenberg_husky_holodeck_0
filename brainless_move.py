import hbp_nrp_cle.tf_framework as nrp
from hbp_nrp_cle.robotsim.RobotInterface import Topic
import geometry_msgs.msg

@nrp.MapRobotSubscriber("camera", Topic('/husky/husky/camera', sensor_msgs.msg.Image))
@nrp.Neuron2Robot(Topic('/husky/husky/cmd_vel', geometry_msgs.msg.Twist))
def move_square(t, camera):
    image_results = hbp_nrp_cle.tf_framework.tf_lib.detect_red(image=camera.value)
    if image_results.left > 0.2:
        return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=11, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=0))

    return geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0, y=0, z=2))


