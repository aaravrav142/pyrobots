import logging; logger = logging.getLogger("robot." + __name__)
logger.setLevel(logging.DEBUG)

import random

from robots.action import *

from robots.helpers import postures
from robots.helpers.cb import *

from robots.actions import configuration, nav, look_at

used_plan_id = []

@tested("22/02/2012")
@action
def release_gripper(robot, gripper = "RIGHT"):
    """
    Opens the gripper to release something.

    Like gripper_open, except it waits until it senses some effort on the gripper force sensors.

    :see: open_gripper

    :param gripper: "RIGHT" (default) or "LEFT"
    """
    if gripper == "RIGHT":
        return [genom_request("pr2SoftMotion", "GripperGrabRelease", ["RRELEASE"])]
    else:
        return [genom_request("pr2SoftMotion", "GripperGrabRelease", ["LRELEASE"])]

@tested("22/02/2012")
@action
def grab_gripper(robot, gripper = "RIGHT"):
    """
    Closes the gripper to grab something.

    Like gripper_close, except it waits until it senses some effort on the gripper force sensors.

    :see: close_gripper
    :param gripper: "RIGHT" (default) or "LEFT"
    """
    if gripper == "RIGHT":
        return [genom_request("pr2SoftMotion", "GripperGrabRelease", ["RGRAB"])]
    else:
        return [genom_request("pr2SoftMotion", "GripperGrabRelease", ["LGRAB"])]

@tested("22/02/2012")
@action
def open_gripper(robot, gripper = "RIGHT", callback = None):
    """
    Opens the right gripper.

    :see: release_gripper
    :param gripper: "RIGHT" (default) or "LEFT"
    :param callback: if set, the action is non-blocking and the callback is invoked upon completion
    """
    if gripper == "RIGHT":
        return [genom_request("pr2SoftMotion", 
                "GripperGrabRelease", 
                ["ROPEN"],
                wait_for_completion = False if callback else True,
                callback = callback)]

    else:
        return [genom_request("pr2SoftMotion", 
                "GripperGrabRelease", 
                ["LOPEN"],
                wait_for_completion = False if callback else True,
                callback = callback)]

@tested("22/02/2012")
@action
def close_gripper(robot, gripper = "RIGHT", callback = None):
    """ Closes the right gripper.
    
    :see: grab_gripper
    :param gripper: "RIGHT" (default) or "LEFT"
    :param callback: if set, the action is non-blocking and the callback is invoked upon completion
    """
    if gripper == "RIGHT":
        return [genom_request("pr2SoftMotion", 
                "GripperGrabRelease", 
                ["RCLOSE"],
                wait_for_completion = False if callback else True,
                callback = callback)]
    else:
        return [genom_request("pr2SoftMotion", 
                "GripperGrabRelease", 
                ["LCLOSE"],
                wait_for_completion = False if callback else True,
                callback = callback)]

@tested("23/02/2012")
@action
def configure_grippers(robot, grab_acc = 8.0, grab_slip = 0.2, release_acc = 4.0, release_slip = 0.05, force = 25):
    """ Sets the grippers thresholds.
    
    :param grab_acc: threshold for grab detection
    :param grab_slip: threshold for grab detection
    :param release_acc: threshold for release detection
    :param release_slip: threshold for release detection
    :param force: hold force
    """
    return [genom_request("pr2SoftMotion", 
            "SetGripperTresholds", 
            [grab_acc, grab_slip, release_acc, release_slip, force])]


def getplanid():
    """ Returns a random plan id (for Amit planification routines) which is
    guaranteed to be 'fresh'.
    """
    plan_id = random.randint(1, 1000)
    while plan_id in used_plan_id:
        plan_id = random.randint(1, 1000)
    used_plan_id.append(plan_id)
    return plan_id

@action
def pick(robot, obj, use_cartesian = "GEN_FALSE"):
    """ Picks an object that is reachable by the robot.

    :param object: the object to pick.
    """

    # Open gripper
    actions = open_gripper(robot)

    # Plan trajectory to object and execute it
    actions += [
    genom_request("mhp", "ArmPlanTask",
            [0,
            'GEN_TRUE',
            'MHP_ARM_PICK_GOTO',
            0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            obj,
            'NO_NAME',
            'NO_NAME',
            use_cartesian,
            0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        genom_request("mhp", "ArmSelectTraj", [0]),
        genom_request("pr2SoftMotion", "TrackQ", ['mhpArmTraj', 'PR2SM_TRACK_POSTER', 'RARM'])
    ]

:spark::SetInferrenceForObject "LOTR_TAPE" 1 "JIDOKUKA_ROBOT" 0 SPARK_PRECISE_ROBOT_HAND 1.0 

    # Close gripper
    actions += close_gripper(robot)

    # create link between the robot and the object
    actions += [
        genom_request("spark","SetGraspedObject", [obj, 1, 0]),
        genom_request("spark","SetInferrenceForObject", [obj, 1, robot.id, 0, 
            "SPARK_PRECISE_ROBOT_HAND", 1.0]) 
    ]
    return actions

@tested("22/02/2012")
@action
def basicgive(robot):
    """ The ultra stupid basic GIVE: simply hand the object in front of the
    robot.
    
    After handing the object, the robot waits for someone to take it, and
    stay in this posture. 
    """

    posture = postures.read()
    
    actions = configuration.setpose(robot, posture["GIVE"])
    actions += release_gripper(robot)
    actions += [wait(2)]
    actions += close_gripper(nop)
        
    return actions

@tested("22/02/2012")
@action
def basicgrab(robot):
    """ The ultra stupid basic GRAB: simply take the object in front of the
    robot.
    
    After handing its gripper, the robot waits for someone to put an object in
    it, and stay in this posture.
    """

    posture = postures.read()
    
    actions = open_gripper(nop)
    actions += configuration.setpose(robot, posture["GIVE"])
    actions += grab_gripper(robot)
        
    return actions

@tested("15/06/2012")
@action
def handover(robot, human, mobility = 0.0):
    actions = look_at.look_at(robot, human)
    actions += configuration.tuckedpose(robot, nop)
    actions += look_at.look_at(robot, [1,0,0.7,"base_link"])
    res = robot.planning.handover(human, mobility = mobility)

    if not res:
        logger.warning("OTP planning failed. Retrying.")
        robot.sorry()
        res = robot.planning.handover(human, mobility=mobility)
        if not res:
            logger.error("OTP planning failed again. Giving up.")
            return []

    wps, pose = res
    print(res)
    actions += nav.waypoints(robot, wps)
    actions += look_at.look_at(robot, human,nop)

    # Collision avoidance
    #pose_rarm = {'RARM':pose['RARM']}
    #actions += configuration.settorso(pose['TORSO'][0], nop)
    #actions += configuration.setpose(robot, pose_rarm, collision_avoidance = True, callback=nop)

    # No collision avoidance
    actions += configuration.setpose(robot, pose)

    actions += release_gripper(robot)
    actions += [wait(1)]
    actions += close_gripper(robot, nop)
    actions += configuration.tuckedpose(robot)

    return actions


@action
def amit_give(robot, performer, obj, receiver):
    """ The 'Amit' GIVE.
    """
    plan_id = getplanid()
    actions = [
        genom_request("mhp",
            "Plan_HRI_Task",
            [plan_id, "GIVE_OBJECT", obj, performer,  receiver, 0, 0, 0]
        ),
        genom_request(	"mhp",
            "Get_SM_Traj_HRI_Task",
            [plan_id]
        ),
        genom_request(	"pr2SoftMotion",
            "GripperGrabRelease",
            ["OPEN"]
        ),
        genom_request(	"mhp",
            "Write_this_SM_Traj_to_Poster",
            [0]
        ),
        genom_request(	"pr2SoftMotion",
            "TrackQ",
            ["mhpArmTraj", "PR2SM_TRACK_POSTER", "RARM"]
        ),
        genom_request(	"mhp",
            "Write_this_SM_Traj_to_Poster",
            [1]
        ),
        genom_request(	"pr2SoftMotion",
            "TrackQ",
            ["mhpArmTraj", "PR2SM_TRACK_POSTER", "RARM"]
        ),
        genom_request(	"pr2SoftMotion",
            "GripperGrabRelease",
            ["CLOSE"]
        ),
        genom_request(	"mhp",
            "Write_this_SM_Traj_to_Poster",
            [3]
        ),
        genom_request(	"pr2SoftMotion",
            "TrackQ",
            ["mhpArmTraj", "PR2SM_TRACK_POSTER", "RARM"]
        ),
        genom_request(	"mhp",
            "Write_this_SM_Traj_to_Poster",
            [4]
        ),
        genom_request(	"pr2SoftMotion",
            "TrackQ",
            ["mhpArmTraj", "PR2SM_TRACK_POSTER", "RARM"]
        ),
        genom_request(	"pr2SoftMotion",
            "GripperGrabRelease",
            ["RELEASE"]
        )
    ]

    return actions

