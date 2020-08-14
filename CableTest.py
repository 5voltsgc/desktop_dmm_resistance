#!/usr/bin/python
# This program is for testing cable conductors for resistance
# with a Agilent Desktop DMM, with SCIPI via TCPIP
# A log file is generated during the resistance testing
# This is for use on a Raspberry Pi, using it's GPIO
# Jeff Watts - Aug 18, 2020
# Rev 1


import RPi.GPIO as GPIO
import datetime
import pyvisa
import matplotlib.pyplot as plt

#Set up the GPIO on the Raspberry Pi
GPIO.setmode(GPIO.BCM)
pinList = [4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12]
#          1   2   3   4   5   6  7   8  9  10  11 12  13  14  15  16a            
for r in pinList:
    GPIO.setup(r,GPIO.OUT)
    GPIO.output(r,GPIO.HIGH)

Cable_A1 = 4
Cable_A2 = 17
Cable_A3 = 27
Cable_A4 = 22
Cable_A5 = 10
Cable_A6 = 9
Cable_A7 = 11
Cable_A8 = 5
Cable_B1 = 6
Cable_B2 = 13
Cable_B3 = 19
Cable_B4 = 26
Cable_B5 = 21
Cable_B6 = 20
Cable_B7 = 16
Cable_B8 = 12
    