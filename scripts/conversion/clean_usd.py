"""This script ensures the USD files are in a clean state.

Specifically, for rigid objects (non-articulation), this script ensures:
1. Remove articulation root API
2. Ensure collision API, with convexDecomposition by default
3. Remove fixed joints
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import tyro


@dataclass
class Args:
    # tasks: list[str] = None
    usd_path: str = None
    collision_mode: Literal["convexDecomposition", "convexHull", "meshSimplification"] = "convexDecomposition"
    object_mass: float = None


args = tyro.cli(Args)

########################################################
## Launch IsaacLab
########################################################
import argparse

# from omni.isaac.lab.app import AppLauncher
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args_isaaclab = parser.parse_args([])
args_isaaclab.headless = True
app_launcher = AppLauncher(args_isaaclab)
simulation_app = app_launcher.app

########################################################
## Normal Code
########################################################
from loguru import logger as log
from pxr import Usd, UsdPhysics, UsdGeom

from metasim.scenario.objects import RigidObjCfg
# from metasim.utils.setup_util import get_task


def is_articulation(usd_path: str):
    joint_count = 0
    stage = Usd.Stage.Open(usd_path)
    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.Joint) and not prim.IsA(UsdPhysics.FixedJoint):
            joint_count += 1
    return joint_count > 0


def remove_articulation_root_api(usd_path: str):
    stage = Usd.Stage.Open(usd_path)
    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            prim.RemoveAPI(UsdPhysics.ArticulationRootAPI)
    stage.Save()


def has_collision_api(usd_path: str):
    stage = Usd.Stage.Open(usd_path)
    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.CollisionAPI):
            return True
    return False


def ensure_collision_api(
    usd_path: str,
    collision_mode: Literal["convexDecomposition", "convexHull", "meshSimplification"] = "convexDecomposition",
):
    stage = Usd.Stage.Open(usd_path)
    if has_collision_api(usd_path):
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.CollisionAPI):
                meshCollisionAPI = UsdPhysics.MeshCollisionAPI.Apply(prim)
                meshCollisionAPI.CreateApproximationAttr().Set(collision_mode)
        stage.Save()
    else:
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                prim.ApplyAPI(UsdPhysics.CollisionAPI)
                meshCollisionAPI = UsdPhysics.MeshCollisionAPI.Apply(prim)
                meshCollisionAPI.CreateApproximationAttr().Set(collision_mode)
        stage.Save()


def remove_fixed_joint(usd_path: str):
    stage = Usd.Stage.Open(usd_path)
    prim_to_remove = []
    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.FixedJoint):
            prim_to_remove.append(prim)
    for prim in prim_to_remove:
        stage.RemovePrim(prim.GetPrimPath())
    stage.Save()

SKIP_PREFIXES = ("/Looks", "/materials", "/Material", "/Materials")

def _is_skippable_path(prim):
    p = prim.GetPath().pathString
    return any(p.startswith(prefix) for prefix in SKIP_PREFIXES)

def _has_rigidbody_api(stage: Usd.Stage) -> bool:
    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            return True
    return False

def _candidate_rigidbody_roots(stage: Usd.Stage):
    """Yield candidate Xform prims that contain collisions or meshes."""
    candidates = set()

    # Prefer parents of prims that already have CollisionAPI
    for prim in stage.Traverse():
        if _is_skippable_path(prim):
            continue
        if prim.HasAPI(UsdPhysics.CollisionAPI):
            # Walk up to the first Xform ancestor
            p = prim
            while p and not p.IsA(UsdGeom.Xform):
                p = p.GetParent()
            if p and p != stage.GetPseudoRoot():
                candidates.add(p)

    # If no collisions yet, fall back to parents of meshes
    if not candidates:
        for prim in stage.Traverse():
            if _is_skippable_path(prim):
                continue
            if prim.IsA(UsdGeom.Mesh):
                p = prim
                while p and not p.IsA(UsdGeom.Xform):
                    p = p.GetParent()
                if p and p != stage.GetPseudoRoot():
                    candidates.add(p)

    # If defaultPrim is a valid Xform, include it as a strong candidate
    dp = stage.GetDefaultPrim()
    if dp and dp.IsValid() and dp.IsA(UsdGeom.Xform) and not _is_skippable_path(dp):
        candidates.add(dp)

    # Return candidates ordered by how high they are (shallower = fewer elements)
    return sorted(
        candidates,
        key=lambda c: c.GetPath().pathElementCount
    )

def ensure_rigidbody_api(usd_path: str, mass: float = None):
    """
    Apply UsdPhysics.RigidBodyAPI to a single top-level Xform that contains the geometry.
    Optionally attach MassAPI with a default mass if none is present.
    """
    stage = Usd.Stage.Open(usd_path)

    # If the asset already has a rigid body, nothing to do.
    if _has_rigidbody_api(stage):
        stage.Save()
        return

    candidates = _candidate_rigidbody_roots(stage)
    if not candidates:
        raise RuntimeError(
            f"No suitable Xform prim found to apply RigidBodyAPI in '{usd_path}'. "
            "Ensure the asset has an Xform parent above its mesh/collision prims."
        )

    root = candidates[0]  # pick the highest suitable Xform
    UsdPhysics.RigidBodyAPI.Apply(root)

    if mass is not None:
        mass_api = UsdPhysics.MassAPI.Apply(root)
        # Only set if not authored yet
        mass_attr = mass_api.GetMassAttr()
        if not mass_attr.HasAuthoredValueOpinion():
            mass_attr.Set(mass)

    stage.Save()

def main():
    log.info("Start")
    usd_paths = []
    # if args.tasks is not None:
    #     for task in args.tasks:
    #         task_cfg = get_task(task)
    #         for obj_cfg in task_cfg.objects:
    #             if isinstance(obj_cfg, RigidObjCfg) and obj_cfg.usd_path is not None and obj_cfg.usd_path not in usd_paths:
    #                 usd_paths.append(obj_cfg.usd_path)
    
    if args.usd_path is not None:
        usd_paths.append(args.usd_path)
    
    for usd_path in usd_paths:
        log.info(f"Cleaning {usd_path}")
        assert not is_articulation(usd_path), f"{usd_path} is an articulation"
        remove_articulation_root_api(usd_path)
        ensure_rigidbody_api(usd_path, args.object_mass)
        ensure_collision_api(usd_path, args.collision_mode)
        remove_fixed_joint(usd_path)
    log.info("Done")

if __name__ == "__main__":
    main()
