import roslib; roslib.load_manifest('novela_actionlib')
import rospy

import actionlib
import pr2_controllers_msgs.msg
import geometry_msgs.msg
import action

###############################################################################
###############################################################################

@action.action
def look_at(target):

        """ Create the client and the goal.

        :param reqs:
	- a dictionnary name which contains object position parameters
        """

	x = target['x']
	y = target['y']
	z = target['z']


        # Creates the SimpleActionClient, passing the type of the action
        # (MoveBaseAction) to the constructor.
	client = actionlib.SimpleActionClient('/head_traj_controller/point_head_action', pr2_controllers_msgs.msg.PointHeadAction)

	# Waits for the action server to come up
	client.wait_for_server()
        ok = client.wait_for_server()
        if not ok:
                print("Could not connect to the ROS client! Aborting action")
                return

        # Creates a goal to send to the action server.  
	goal = pr2_controllers_msgs.msg.PointHeadGoal()

        # Definition of the goal
	point = geometry_msgs.msg.PointStamped()
	point.header.frame_id = 'map'
	point.point.x = x
	point.point.y = y
	point.point.z = z

	goal.target = point
	goal.pointing_frame = 'high_def_frame'
	goal.min_duration = rospy.Duration(0.5)
	goal.max_velocity = 1.0

	return [action.ros_request(client, goal)]

###############################################################################
