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
NumConductors = 4 # must be 8 or less, starts at 1 for 1 relay
SleepTimeL = 20

# turn off all relays, even ones not turned on to simplify functions 
def relays_off():
    for j in pin_list:        
        GPIO.output(j,GPIO.HIGH)

# turn off all relays, even ones not turned on to simplify functions 
def relays_on():
    for j in range(NumConductors):
        if GPIO.input(pin_list[j]): #if true - which means off 
            GPIO.output(pin_list[j],GPIO.LOW)
        else:
            GPIO.output(pin_list[j],GPIO.HIGH)

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
        print(pin_list[j+8])
        
        #Turn on all B side relays except for matching relay
        for k in range(8, 16):
            GPIO.output(pin_list[k],GPIO.LOW)
        
        # Turn off matching relay for Cross talk check
        GPIO.output(pin_list[15-j],GPIO.HIGH)
        
        time.sleep(SleepTimeL)
        relays_off() 

def turn_on_relays (relay_pin):    

    if not GPIO.input(pin_list[relay_pin]): #True is relay off low level
        GPIO.output(pin_list[relay_pin],GPIO.HIGH)
    else:
        GPIO.output(pin_list[relay_pin],GPIO.LOW)
    
#Testing loop of vaibles
# res_test()
# cross_talk()

def relay_check():
    x = True


    while x == True:
         # add error handling for letters purhaps exit infinate loop
         
        pin_relay = input("Enter a relay to turn on or off (between 0 - 15):")
        
        if pin_relay.isalpha():
          x = False
          print("exit relay check mode")
          relays_off() 
          GPIO.cleanup()
        else:
            if int(pin_relay) < 16 and int(pin_relay) > -1:
                turn_on_relays(int(pin_relay))
            else:
                print("Please enter a number between 0 - 15")

    