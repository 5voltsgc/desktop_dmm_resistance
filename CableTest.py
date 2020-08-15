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
import time

#setup reading Desktop DMM change ip address as needed, for different networks
rm = pyvisa.ResourceManager()
my_instrument = rm.open_resource('TCPIP0::192.168.000.43::inst0::INSTR')
my_instrument.read_termination = '\n'

#Set up the GPIO on the Raspberry Pi
GPIO.setmode(GPIO.BCM)

# Relay # [0   1   2   3   4   5   6  7  8   9  10  11  12  13  14  15]
# Relay # [1   2   3   4   5   6   7  8  9  10  11  12  13  14  15  16]
pin_list = [4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12]
for i in pin_list:
    GPIO.setup(i,GPIO.OUT)
    GPIO.output(i,GPIO.HIGH)

#varibles
NumConductors = 8 # must be 8 or less, starts at 1 for 1 relay
SleepTimeL = 1

# turn off all relays, even ones not turned on to simplify functions 
def relays_off():
    for j in pin_list:        
        GPIO.output(j,GPIO.HIGH)

# turn off all relays, even ones not turned on to simplify functions 
def relays_on():
    for j in range(NumConductors):
        GPIO.output(pin_list[j],GPIO.LOW)

#ResTest()
def res_test():
    for u in range(5):
        for j in range(NumConductors):
            GPIO.output(pin_list[j],GPIO.LOW)

            GPIO.output(pin_list[15-j] ,GPIO.LOW)
            time.sleep(SleepTimeL)
            relays_off() 

#ResTest()
def cross_talk():
    for j in range(NumConductors):
        #Turn on A side relay
        GPIO.output(pin_list[j],GPIO.LOW)
        
        #Turn on all B side relays except for matching relay
        for k in range(8, 16):
                GPIO.output(pin_list[k],GPIO.LOW)
                print(k)
        time.sleep(SleepTimeL)
        relays_off() 
            

#Testing loop of vaibles
cross_talk()
time.sleep(SleepTimeL)
relays_off()        


#before ending program cleanup GPIO 
GPIO.cleanup()
    