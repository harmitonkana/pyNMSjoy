'''
pyNMSjoy
Version: 1.0
Author: xå.dev
Date: 20 July 2020

Enabled smoother H.O.T.A.S. control in No Mans Sky.
Tested on Saitek X52 Flight Control System.

'''

import pygame
import os
import win32api
import threading
import pydirectinput
import time
import math

# Initial values for global variables
ROLL_VALUE = 0
THRUST_VALUE = 0
XMOVE = 0
YMOVE = 0

# You can change these by following the naming convention.
# Some joystick functions are not supported.
# Buttons and hats should be ok for now.
KEYMAP = [
	['fire', False, 'mouse_left', 'button_0'],
	['zoom', False, 'mouse_right', 'button_2'],
	['scan', False, 'c', 'button_3'],
	['changeweapon', False, 'g', 'button_4'],
	['boost', False, 'shift', 'button_6'],
	['pulsenegine', False, 'space', 'button_7'],
	['land', False, 'e', 'button_9'],
	['previoustarget', False, ',', 'hat_0_left'],
	['nexttarget', False, '.', 'hat_0_right'],
	['closesttarget', False, 'mouse_middle', 'hat_0_up']
]


def initJoystick(joyNum):
	pygame.joystick.Joystick(joyNum).init()
	return pygame.joystick.Joystick(joyNum)


# Holds the corresponding keys down for desired amount of time, repeating for every period.
def rollLoop(pwm_period, roll_deadzone):
	# Access global variable for read
	global ROLL_VALUE
	while True:
		rollValueScaled = (abs(ROLL_VALUE) - roll_deadzone) / (1 - roll_deadzone)	# If within deadzone, return negative.
		if rollValueScaled < 0:
			rollValueScaled = 0
		ON_period = pwm_period * rollValueScaled
		OFF_period = pwm_period - ON_period
		if rollValueScaled > 0 and ROLL_VALUE < 0:
			pydirectinput.keyDown('a')
			time.sleep(ON_period)
			pydirectinput.keyUp('a')
		elif rollValueScaled > 0 and ROLL_VALUE > 0:
			pydirectinput.keyDown('d')
			time.sleep(ON_period)
			pydirectinput.keyUp('d')
		time.sleep(OFF_period)


def thrustLoop(pwm_period, thrust_deadzone):
	global THRUST_VALUE
	while True:
		thrustValueScaled = (abs(THRUST_VALUE) - thrust_deadzone) / (1 - thrust_deadzone)
		if thrustValueScaled < 0:
			thrustValueScaled = 0
		ON_period = pwm_period * thrustValueScaled
		OFF_period = pwm_period - ON_period
		if thrustValueScaled > 0 and THRUST_VALUE < 0:
			pydirectinput.keyDown('w')
			time.sleep(ON_period)
			pydirectinput.keyUp('w')
		elif thrustValueScaled > 0 and THRUST_VALUE > 0:
			pydirectinput.keyDown('s')
			time.sleep(ON_period)
			pydirectinput.keyUp('s')
		time.sleep(OFF_period)


def axisToMouse(value, deadzone, sensitivity):
	valueScaled = (abs(value) - deadzone) / (1 - deadzone)
	mMove = 0
	if valueScaled > 0:
		mMove = valueScaled * (value / abs(value))
		# Movement value needs to be rounded up before conversion to integer. Otherwise values below 1 return 0 resulting in extra deadzones
		# If we didn't do this, yaw and pitch deadzones in main() would have no effect if they were smaller than singular sensitivity step
		mMove = int(math.ceil(mMove * sensitivity))
	return mMove


def yawPitchLoop(interval, invert):
	global XMOVE
	global YMOVE
	if invert:
		yMul = -1
	else:
		yMul = 1
	while True:
		if XMOVE != 0 or YMOVE != 0:
			pydirectinput.move(XMOVE, YMOVE * yMul)
		time.sleep(interval)


def checkButtons(joystick):
	global KEYMAP
	for binding in KEYMAP:
		keyTo = binding[2].split("_")
		keyFrom = binding[3].split("_")

		if keyFrom[0] == "button":
			if joystick.get_button(int(keyFrom[1])):
				if binding[1] == False:
					binding[1] = True
					if keyTo[0] == "mouse":
						pydirectinput.mouseDown(button=keyTo[1])
					else:
						pydirectinput.keyDown(keyTo[0])
			else:
				if binding[1]:
					binding[1] = False
					if keyTo[0] == "mouse":
						pydirectinput.mouseUp(button=keyTo[1])
					else:
						pydirectinput.keyUp(keyTo[0])

		elif keyFrom[0] == "hat":
			if keyFrom[2] == "left":
				if joystick.get_hat(int(keyFrom[1]))[0] == -1:
					if binding[1] == False:
						binding[1] = True
						if keyTo[0] == "mouse":
							pydirectinput.mouseDown(button=keyTo[1])
						else:
							pydirectinput.keyDown(keyTo[0])
				else:
					if binding[1]:
						binding[1] = False
						if keyTo[0] == "mouse":
							pydirectinput.mouseUp(button=keyTo[1])
						else:
							pydirectinput.keyUp(keyTo[0])

			elif keyFrom[2] == "right":
				if joystick.get_hat(int(keyFrom[1]))[0] == 1:
					if binding[1] == False:
						binding[1] = True
						if keyTo[0] == "mouse":
							pydirectinput.mouseDown(button=keyTo[1])
						else:
							pydirectinput.keyDown(keyTo[0])
				else:
					if binding[1]:
						binding[1] = False
						if keyTo[0] == "mouse":
							pydirectinput.mouseUp(button=keyTo[1])
						else:
							pydirectinput.keyUp(keyTo[0])

			elif keyFrom[2] == "up":
				if joystick.get_hat(int(keyFrom[1]))[1] == -1:
					if binding[1] == False:
						binding[1] = True
						if keyTo[0] == "mouse":
							pydirectinput.mouseDown(button=keyTo[1])
						else:
							pydirectinput.keyDown(keyTo[0])
				else:
					if binding[1]:
						binding[1] = False
						if keyTo[0] == "mouse":
							pydirectinput.mouseUp(button=keyTo[1])
						else:
							pydirectinput.keyUp(keyTo[0])

			elif keyFrom[2] == "down":
				if joystick.get_hat(int(keyFrom[1]))[1] == 1:
					if binding[1] == False:
						binding[1] = True
						if keyTo[0] == "mouse":
							pydirectinput.mouseDown(button=keyTo[1])
						else:
							pydirectinput.keyDown(keyTo[0])
				else:
					if binding[1]:
						binding[1] = False
						if keyTo[0] == "mouse":
							pydirectinput.mouseUp(button=keyTo[1])
						else:
							pydirectinput.keyUp(keyTo[0])


def displayJoysticks():
	joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
	print("Following devices were found:")
	for i in range(0, len(joysticks)):
		print(" " + joysticks[i].get_name() + " (joynum=" + str(i) +")")
	print(" ")


def main():
	# Access global variables for modifying them
	global ROLL_VALUE
	global THRUST_VALUE
	global XMOVE
	global YMOVE

	# For how long should we press the keys for roll and thrust when applying full power
	pwm_period = 1 / 5

	# Joystick axes are from -1 to 1, 0 being center. Deadzone of 0.1 means 10% deadzone to either direction
	roll_deadzone = 0.01
	thrust_deadzone = 0.1
	yaw_deadzone = 0.01
	pitch_deadzone = 0.01

	# Sensitivity also defines how many levels of movement can be applied
	# Larger values allow for finer control but also increase sensitivity beyond desired point
	yaw_sensitivity = 10
	pitch_sensitivity = 50
	# As pydirectinput only accepts integer values for mouse movement, controls can be made less sensitive by applying yaw and pitch only after set intervals
	# Therefore yaw and pitch are applied in a loop in a separate thread
	yawPitchInterval = 0.01
	pitchInverted = True

	print("pyNMSjoy\n")
	pydirectinput.FAILSAFE = False # Otherwise moving mouse/joystick to top left corner of the screen will crash the program
	pydirectinput.PAUSE = 0.001	# Decrease pause time after keypress
	pygame.display.init()
	pygame.joystick.init()
	
	displayJoysticks()

	joystickNumber = 0
	print("Using device with joynum " + str(joystickNumber) + ".")
	print("(Edit variable joystickNumber if you wish to use another device.)\n")
	joystick = initJoystick(joystickNumber)

	# Run roll and thrust routine in their own threads
	rollThread = threading.Thread(target=rollLoop, args=(pwm_period, roll_deadzone,))
	rollThread.start()
	thrustThread = threading.Thread(target=thrustLoop, args=(pwm_period, thrust_deadzone,))
	thrustThread.start()
	yawPitchThread = threading.Thread(target=yawPitchLoop, args=(yawPitchInterval, pitchInverted,))
	yawPitchThread.start()

	print("Listening to input...")
	print("(You may now leave the script running in background.)")

	while True:
		# Exit if this key is pressed. You can change this to whatever you like
		if (win32api.GetAsyncKeyState(ord('J'))):
			print("Exited")
			os._exit(1)
		
		pygame.event.pump()

		# Read axis data
		ROLL_VALUE = joystick.get_axis(0)
		THRUST_VALUE = joystick.get_axis(2)
        # Translate joystick yaw and pitch to relative mouse movement
		XMOVE = axisToMouse(joystick.get_axis(3), yaw_deadzone, yaw_sensitivity)
		YMOVE = axisToMouse(joystick.get_axis(1), pitch_deadzone, pitch_sensitivity)
		checkButtons(joystick) # Determine whether buttons are pressed and perform action


if __name__ == "__main__":
	main()