"""This script is used to grasp an object from a point cloud."""

from __future__ import annotations

"""This script is used to test the static scene."""


from typing import Literal

try:
    import isaacgym  # noqa: F401
except ImportError:
    pass

import math
import os

import rootutils
import torch
import tyro
from loguru import logger as log
from rich.logging import RichHandler

rootutils.setup_root(__file__, pythonpath=True)
log.configure(handlers=[{"sink": RichHandler(), "format": "{message}"}])

import rootutils
from loguru import logger as log
from rich.logging import RichHandler

rootutils.setup_root(__file__, pythonpath=True)
log.configure(handlers=[{"sink": RichHandler(), "format": "{message}"}])
from scipy.spatial.transform import Rotation as R

from metasim.scenario.cameras import PinholeCameraCfg
from metasim.constants import PhysicStateType
from metasim.scenario.objects import (
    ArticulationObjCfg,
    PrimitiveCubeCfg,
    PrimitiveSphereCfg,
    RigidObjCfg,
)
from metasim.scenario.scenario import ScenarioCfg
from metasim.utils import configclass
from metasim.utils.obs_utils import ObsSaver
from metasim.utils.setup_util import get_handler

import numpy as np


@configclass
class Args:
    """Arguments for the static scene."""

    robot: str = "franka"

    ## Handlers
    sim: Literal["isaacsim", "isaacgym", "genesis", "pybullet", "sapien2", "sapien3", "mujoco"] = "mujoco"

    ## Others
    num_envs: int = 1
    headless: bool = False
    solver: Literal["curobo", "pyroki"] = "pyroki"
    asset_dir: str = "roboverse_data/assets/rack_ycb"

    def __post_init__(self):
        """Post-initialization configuration."""
        log.info(f"Args: {self}")


args = tyro.cli(Args)

from metasim.utils.ik_solver import setup_ik_solver

# initialize scenario
scenario = ScenarioCfg(
    robots=[args.robot],
    simulator=args.sim,
    headless=args.headless,
    num_envs=args.num_envs,
    decimation=4,
)
# add objects
scenario.objects = [
    # PrimitiveCubeCfg(
    #     name="cube",
    #     size=(0.1, 0.1, 0.1),
    #     color=[1.0, 0.0, 0.0],
    #     physics=PhysicStateType.XFORM, #RIGIDBODY,
    # ),
    RigidObjCfg(
        name="rack_0",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, #RIGIDBODY,
        fix_base_link=True,
        usd_path=f"{args.asset_dir}/SM_PaperCase_Case.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
    RigidObjCfg(
        name="rack_1",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, #RIGIDBODY,
        fix_base_link=True,
        usd_path=f"{args.asset_dir}/SM_PaperCase_Case.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
    RigidObjCfg(
        name="_03_cracker_box_0",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_03_cracker_box.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
    RigidObjCfg(
        name="_03_cracker_box_1",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_03_cracker_box.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
    RigidObjCfg(
        name="_03_cracker_box_2",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_03_cracker_box.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
    RigidObjCfg(
        name="_06_mustard_bottle_0",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_06_mustard_bottle.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
    RigidObjCfg(
        name="_06_mustard_bottle_1",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_06_mustard_bottle.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),

    RigidObjCfg(
        name="_06_mustard_bottle_2",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_06_mustard_bottle.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
    RigidObjCfg(
        name="_02_master_chef_can_0",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_02_master_chef_can.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
    RigidObjCfg(
        name="_02_master_chef_can_1",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_02_master_chef_can.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),

    RigidObjCfg(
        name="_02_master_chef_can_2",
        scale=(1, 1, 1),
        physics=PhysicStateType.XFORM, # RIGIDBODY,
        usd_path=f"{args.asset_dir}/_02_master_chef_can.usd",
        # urdf_path=f"{data_dir}/demo_assets/table/result/table.urdf",
        # mjcf_path=f"{data_dir}/demo_assets/table/mjcf/table.mjcf",
    ),
]

if args.robot == "franka":
    robot_dict = {
            "franka": {
                "pos": torch.tensor([0.0, 0.0, 0.0]),
                "rot": torch.tensor([1.0, 0.0, 0.0, 0.0]),
                "dof_pos": {
                    "panda_joint1": 0.0,
                    "panda_joint2": -0.785398,
                    "panda_joint3": 0.0,
                    "panda_joint4": -2.356194,
                    "panda_joint5": 0.0,
                    "panda_joint6": 1.570796,
                    "panda_joint7": 0.785398,
                    "panda_finger_joint1": 0.04,
                    "panda_finger_joint2": 0.04,
                }
            }
    }
elif args.robot == "ur5e":
    robot_dict = {
        "ur5e": {
            "pos": torch.tensor([0.0, 0.0, 0.0]),
            "rot": torch.tensor([1.0, 0.0, 0.0, 0.0]),
            "dof_pos": {
                "shoulder_pan_joint": 0.0,
                "shoulder_lift_joint": -math.pi / 2,
                "elbow_joint": math.pi / 2,
                "wrist_1_joint": -math.pi / 2,
                "wrist_2_joint": -math.pi / 2,
                "wrist_3_joint": 0.0,
            },
        }
    }
else:
    robot_dict = {}

original_orientation = [1.0, 0.0, 0.0, 0.0]
front_orientation = [0.5, -0.5, 0.5, -0.5]

rack_bb_dims = [1.908914, 2.03912, 0.449513]

shelf_heights = [0.95, 1.325, 1.675]
shelf_depth = -0.5
shelf_width = 0.85 - 0.05 # shelf_width - margin

_03_cracker_box_bb_dims = [0.164036, 0.213438, 0.0718]
_06_mustard_bottle_bb_dims = [0.0960252, 0.1913, 0.0582494]


slot_width = _03_cracker_box_bb_dims[1]
slots = np.linspace(-(shelf_width/2)+(slot_width/2), +(shelf_width/2)-(slot_width/2), 4).tolist()

init_states = [
    {
        "objects": {
            # "cube": {
            #     "pos": torch.tensor([0.3, 0.0, 0.05]),
            #     "rot": torch.tensor([1.0, 0.0, 0.0, 0.0]),
            # },
            "rack_0": {
                "pos": torch.tensor([-0.8, (1/4)*rack_bb_dims[0], 0.0]),
                "rot": torch.tensor(original_orientation),
            },
            "rack_1": {
                "pos": torch.tensor([-0.8, -(3/4)*rack_bb_dims[0], 0.0]),
                "rot": torch.tensor(original_orientation),
            },
            "_03_cracker_box_0": {
                "pos": torch.tensor([shelf_depth, slots[0], shelf_heights[0]]),
                "rot": torch.tensor(front_orientation),
            },
            "_03_cracker_box_1": {
                "pos": torch.tensor([shelf_depth, slots[1], shelf_heights[0]]),
                "rot": torch.tensor(front_orientation),
            },
            "_03_cracker_box_2": {
                "pos": torch.tensor([shelf_depth, slots[2], shelf_heights[0]]),
                "rot": torch.tensor(front_orientation),
            },
            "_06_mustard_bottle_0": {
                "pos": torch.tensor([shelf_depth, slots[0], shelf_heights[1]]),
                "rot": torch.tensor(front_orientation),
            },
            "_06_mustard_bottle_1": {
                "pos": torch.tensor([shelf_depth, slots[1], shelf_heights[1]]),
                "rot": torch.tensor(front_orientation),
            },
            "_06_mustard_bottle_2": {
                "pos": torch.tensor([shelf_depth, slots[2], shelf_heights[1]]),
                "rot": torch.tensor(front_orientation),
            },
            "_02_master_chef_can_0": {
                "pos": torch.tensor([shelf_depth, slots[0], shelf_heights[2]]),
                "rot": torch.tensor(front_orientation),
            },
            "_02_master_chef_can_1": {
                "pos": torch.tensor([shelf_depth, slots[1], shelf_heights[2]]),
                "rot": torch.tensor(front_orientation),
            },
            "_02_master_chef_can_2": {
                "pos": torch.tensor([shelf_depth, slots[2], shelf_heights[2]]),
                "rot": torch.tensor(front_orientation),
            },
        },
        "robots": robot_dict,
        # "robots": {
        #     "franka": {
        #         "pos": torch.tensor([0.0, 0.0, 0.0]),
        #         "rot": torch.tensor([1.0, 0.0, 0.0, 0.0]),
        #         "dof_pos": {
        #             "panda_joint1": 0.0,
        #             "panda_joint2": -0.785398,
        #             "panda_joint3": 0.0,
        #             "panda_joint4": -2.356194,
        #             "panda_joint5": 0.0,
        #             "panda_joint6": 1.570796,
        #             "panda_joint7": 0.785398,
        #             "panda_finger_joint1": 0.04,
        #             "panda_finger_joint2": 0.04,
        #         },
        #     },
        # },
    }
    for _ in range(args.num_envs)
]

# add cameras
cam_pos = [2.0, 0.0, 1.4]
# cam_height = shelf_heights[1]
# cam_rack_dist = 1.0-0.35
# scenario.cameras = [PinholeCameraCfg(width=1024, height=1024, pos=(0.0, 0.0, 1.5), look_at=(1.0, 0.0, 0.0))]
scenario.cameras = [PinholeCameraCfg(width=1920, height=1080, pos=cam_pos, look_at=(0.0, 0.0, cam_pos[2]))]

log.info(f"Using simulator: {args.sim}")
handler = get_handler(scenario)

robot = scenario.robots[0]

# Setup IK solver, disable seed for pyroki
ik_solver = setup_ik_solver(robot, args.solver, use_seed=False)

handler.set_states(init_states)
obs = handler.get_states(mode="tensor")
os.makedirs("get_started/output", exist_ok=True)

## Main loop
# obs_saver = ObsSaver(video_path=f"get_started/output/motion_planning/0_franka_planning_{args.sim}_{args.robot}.mp4")
obs_saver = ObsSaver(image_dir=f"get_started/output/101_rack_ycb_{args.sim}_{args.robot}.png")

def move_to_pose(
    obs,
    obs_saver,
    ik_solver,
    robot,
    scenario,
    inverse_reorder_idx,
    ee_pos_target,
    ee_quat_target,
    steps=10,
    open_gripper=False,
):
    """Move the robot to the target pose."""
    # IK solver expects original joint order, but state uses alphabetical order
    curr_robot_q = obs.robots[robot.name].joint_pos[:, inverse_reorder_idx]

    # Solve IK using the unified interface
    q_solution, ik_succ = ik_solver.solve_ik_batch(ee_pos_target, ee_quat_target, curr_robot_q)

    # Process gripper command
    from metasim.utils.ik_solver import process_gripper_command

    gripper_open_tensor = torch.tensor([1.0 if open_gripper else 0.0] * scenario.num_envs, device=ee_pos_target.device)
    gripper_widths = process_gripper_command(gripper_open_tensor, robot, ee_pos_target.device)

    # Compose full joint command
    actions = ik_solver.compose_joint_action(q_solution, gripper_widths, current_q=curr_robot_q, return_dict=True)
    for i in range(steps):
        handler.set_dof_targets(actions)
        handler.simulate()
        obs = handler.get_states(mode="tensor")
        obs_saver.add(obs)
    return obs


# Calculate joint reordering once
# IK solver expects original joint order, but state uses alphabetical order
# reorder_idx = handler.get_joint_reindex(robot.name)
# inverse_reorder_idx = [reorder_idx.index(i) for i in range(len(reorder_idx))]

# step = 0
# robot_joint_limits = scenario.robots[0].joint_limits
# for step in range(4):
#     log.debug(f"Step {step}")
#     states = handler.get_states()
#     rotation_transform_for_franka = torch.tensor(
#         [
#             [0.0, 0.0, 1.0],
#             [0.0, -1.0, 0.0],
#             [1.0, 0.0, 0.0],
#         ],
#     )
#     if step == 0:
#         gripper_out = torch.tensor([0.0, 0.0, -1.0])
#         gripper_long = torch.tensor([0.0, 1.0, 0.0])
#         gripper_short = torch.tensor([1.0, 0.0, 0.0])
#     elif step == 1:
#         gripper_out = torch.tensor([1.0, 0.0, 0.0])
#         gripper_long = torch.tensor([0.0, 1.0, 0.0])
#         gripper_short = torch.tensor([0.0, 0.0, 1.0])
#     elif step == 2:
#         gripper_out = torch.tensor([0.0, -1.0, 0.0])
#         gripper_long = torch.tensor([1.0, 0.0, 0.0])
#         gripper_short = torch.tensor([0.0, 0.0, 1.0])
#     elif step == 3:
#         gripper_out = torch.tensor([0.0, 0.0, 1.0])
#         gripper_long = torch.tensor([0.0, 1.0, 0.0])
#         gripper_short = torch.tensor([-1.0, 0.0, 0.0])
#     log.info(f"gripper_out: {gripper_out}, gripper_long: {gripper_long}, gripper_short: {gripper_short}")
#     rotation_target = torch.stack(
#         [
#             gripper_out + 1e-4,
#             gripper_long + 1e-4,
#             gripper_short + 1e-4,
#         ],
#         dim=0,
#     ).float()
#     rotation = rotation_target @ rotation_transform_for_franka

#     quat = R.from_matrix(rotation).as_quat()
#     position = torch.tensor([0.6, 0.0, 0.6], device="cuda:0")

#     ee_pos_target = torch.zeros((args.num_envs, 3), device="cuda:0")
#     ee_quat_target = torch.zeros((args.num_envs, 4), device="cuda:0")

#     ee_pos_target[0] = torch.tensor(position, device="cuda:0")
#     ee_quat_target[0] = torch.tensor(quat, device="cuda:0")

#     obs = move_to_pose(
#         obs,
#         obs_saver,
#         ik_solver,
#         robot,
#         scenario,
#         inverse_reorder_idx,
#         ee_pos_target,
#         ee_quat_target,
#         steps=100,
#         open_gripper=True,
#     )
#     step += 1

log.info("Enter simulation loop")
step = 0
while True:
    # log.debug(f"Step {step}")
    if step == 100:
        obs = handler.get_states(mode="tensor")
        obs_saver.add(obs)
        obs_saver.save()

    if step <= 100:
        # Updates all including robot
        handler.simulate()
    else:
        # Update sim only
        handler.sim.step()

    step += 1

# Sim without physics
# log.info("Enter simulation loop")
# step = 0
# while True:
#     if step == 0:
#         handler.sim.pause()
#     handler.sim.step()
#     step += 1