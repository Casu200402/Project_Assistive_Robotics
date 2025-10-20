import os
import time
import socket
import tkinter as tk
from tkinter import messagebox
from math import radians, degrees, pi
import numpy as np
from robodk.robolink import *
from robodk.robomath import *

# Define relative path to the .rdk file
relative_path = "src/roboDK/Pick&Place_UR5e.rdk"
absolute_path = os.path.abspath(relative_path)

# Start RoboDK with the project file
RDK = Robolink()
time.sleep(3)
RDK.AddFile(absolute_path)
time.sleep(2)

# Robot setup
robot = RDK.Item("UR5e")
base = RDK.Item("UR5e Base")
tool = RDK.Item("2FG7")
Init_target = RDK.Item("Init")
App_pick_target = RDK.Item("App_Pick")
Pick_target = RDK.Item("Pick")
App_place_target = RDK.Item("App_Place")
Place_target = RDK.Item("Place")
table = RDK.Item("Table")
cube = RDK.Item("Cube")

cube.setVisible(False)
cube_POSE = Pick_target.Pose()
cube.setParent(table)  # Do not maintain the actual absolute POSE
cube.setPose(cube_POSE)
cube.setVisible(True)

robot.setPoseFrame(base)
robot.setPoseTool(tool)
robot.setSpeed(80)

def Init():
    print("Init")
    robot.MoveL(Init_target, True)
    print("Init_target REACHED")

def Pick():
    print("Pick")
    robot.MoveL(App_pick_target,True)
    robot.setSpeed(10)
    robot.MoveL(Pick_target,True)
    cube.setParentStatic(tool)  # Maintain the actual absolute POSE
    robot.MoveL(App_pick_target, True)
    print("Pick FINISHED")

def Place():
    print("Place")
    robot.setSpeed(40)
    robot.MoveL(App_place_target, True)
    robot.setSpeed(10)
    robot.MoveL(Place_target, True)
    cube.setParentStatic(table)  # Suelta el cubo en la mesa
    robot.MoveL(App_place_target, True)
    print("Place FINISHED")

# Main function
def main():
    Init()
    Pick()
    Place()

if __name__ == "__main__":
    main()
