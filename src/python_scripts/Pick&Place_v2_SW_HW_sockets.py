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

# Robot Constants
ROBOT_IP = '192.168.1.4'
ROBOT_PORT = 30002
accel_mss = 1.2
speed_ms = 0.75
blend_r = 0.0
timej = 6
timel = 4

# URScript commands
set_tcp = "set_tcp(p[0.000000, 0.000000, 0.050000, 0.000000, 0.000000, 0.000000])"


# Check robot connection
def check_robot_port(ip, port):
    global robot_socket
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.settimeout(1)
        robot_socket.connect((ip, port))
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
# Send URScript command
def send_ur_script(command):
    robot_socket.send((command + "\n").encode())
# Wait for robot response
def receive_response(t):
    try:
        print("Waiting time:", t)
        time.sleep(t)
    except socket.error as e:
        print(f"Error receiving data: {e}")
        exit(1)

def Init():
    print("Init")
    
    if robot_is_connected and ur5e_execution:
        print("Init REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        j1, j2, j3, j4, j5, j6 = np.radians(Init_target.Joints()).tolist()[0]
        movel_init = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{timel},{blend_r})"
        send_ur_script(movel_init)
        receive_response(timel)
    else:
        print("UR5e not connected. Simulation only.")
        robot.MoveL(Init_target, True)
    print("Init_target REACHED")

def Pick():
    print("Pick")
    
    if robot_is_connected and ur5e_execution:
        print("Init REAL UR5e")
        j1, j2, j3, j4, j5, j6 = np.radians(App_pick_target.Joints()).tolist()[0]
        movel_app_pick = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{timel},{blend_r})"
        send_ur_script(movel_app_pick)
        receive_response(timel)
        j1, j2, j3, j4, j5, j6 = np.radians(Pick_target.Joints()).tolist()[0]
        movel_pick = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{timel},{blend_r})"
        send_ur_script(movel_pick)
        receive_response(timel)
        send_ur_script(movel_app_pick)
        receive_response(timel)
    else:
        print("UR5e not connected. Simulation only.")
        robot.MoveL(App_pick_target,True)
        robot.setSpeed(10)
        robot.MoveL(Pick_target,True)
        cube.setParentStatic(tool)  # Maintain the actual absolute POSE
        robot.MoveL(App_pick_target, True)
    print("Pick FINISHED")

def Place():
    print("Place")
    
    if robot_is_connected and ur5e_execution:
        print("Init REAL UR5e")
        j1, j2, j3, j4, j5, j6 = np.radians(App_place_target.Joints()).tolist()[0]
        movel_app_place = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{timel},{blend_r})"
        send_ur_script(movel_app_place)
        receive_response(timel)
        j1, j2, j3, j4, j5, j6 = np.radians(Place_target.Joints()).tolist()[0]
        movel_place = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{timel},{blend_r})"
        send_ur_script(movel_place)
        receive_response(timel)
        send_ur_script(movel_app_place)
        receive_response(timel)
    else:
        print("UR5e not connected. Simulation only.")
        robot.setSpeed(40)
        robot.MoveL(App_place_target, True)
        robot.setSpeed(10)
        robot.MoveL(Place_target, True)
        cube.setParentStatic(table)  # Suelta el cubo en la mesa
        robot.MoveL(App_place_target, True)
    print("Place FINISHED")
        

# Main function
def main():
    global robot_is_connected, ur5e_execution
    ur5e_execution = True # Flag for UR5e execution. Only one group at True at a time.
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)
    Init()
    Pick()
    Place()
    Init()
    if robot_is_connected:
        robot_socket.close()

if __name__ == "__main__":
    main()
