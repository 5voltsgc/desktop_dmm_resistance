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
import numpy as np

#setup reading Desktop DMM change ip address as needed, for different networks
rm = pyvisa.ResourceManager()
my_instrument = rm.open_resource('TCPIP0::192.168.000.43::inst0::INSTR')
my_instrument.read_termination = '\n'

#Set up the GPIO on the Raspberry Pi
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Relay # [0   1   2   3   4   5   6  7  8   9  10  11  12  13  14  15]
# Relay # [1   2   3   4   5   6   7  8  9  10  11  12  13  14  15  16]
pin_list = [4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12]
for i in pin_list:
    GPIO.setup(i,GPIO.OUT)
    GPIO.output(i,GPIO.HIGH)

#varibles
num_conductors = 8 # must be 8 or less, starts at 1 for 1 relay
SleepTimeL = 1
units_under_test = "testing "+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
test_count = 0

uut_name = input("Please enter name of sample to be tested:")
filename =  uut_name + "-" + datetime.datetime.now().strftime("%y%m%d-%H%M%S") + ".csv"

res_reading = np.empty(num_conductors)
ins_reading = np.empty(num_conductors)
base_line = np.empty(num_conductors)
print_var = ""

#Create log file header
log_header = "time, count, "

for j in range(0, num_conductors):
    log_header = log_header + "Resistance Conductor-" + str(j+1) + ","

log_header = log_header + "Pass/Fail ,"

for k in range(0, num_conductors):
    log_header = log_header + "insulation-Conductor" + str(k+1) + ","
    
log_header = log_header + "Pass/Fail"


# turn off all relays, even ones not turned on to simplify functions 
def relays_off():
    for e in pin_list:        
        GPIO.output(e,GPIO.HIGH)

# turn off all relays, even ones not turned on to simplify functions 
def relays_on():
    for l in pin_list:
        GPIO.output(pin_list[l],GPIO.LOW)


#ResTest()
        
def res_test():
    global test_count
    global print_var
    
    res_test_pass = True
    test_count += 1
    print_var = str(datetime.datetime.now()) + "," + str(test_count)+ ","
    
    for m in range(num_conductors):
        GPIO.output(pin_list[m],GPIO.LOW)
        GPIO.output(pin_list[15-m] ,GPIO.LOW)
        time.sleep(SleepTimeL)
        my_instrument.write('MEAS:FRES? 100 OHM')
        res_reading[m] = round(float(my_instrument.read_bytes(15)), 4)
        print_var = print_var + str(res_reading[m]) + ","
        
        #add the pass fail when base line is done
#         if 2 , (res_reading[m] - base_line[m]):
#             res_test_pass = False
            
        relays_off()
    print_var = print_var + str(res_test_pass) +  ","
    print(print_var)



def cross_talk():
    for d in range(num_conductors):
        #Turn on A side relay
        GPIO.output(pin_list[j],GPIO.LOW)
        print(pin_list[d+8])
        
        #Turn on all B side relays except for matching relay
        for r in range(8, 16):
            GPIO.output(pin_list[r],GPIO.LOW)
        
        # Turn off matching relay for Cross talk check
        GPIO.output(pin_list[15-d],GPIO.HIGH)
        
        time.sleep(SleepTimeL)
        relays_off() 

def turn_on_relays (relay_pin):    

    if not GPIO.input(pin_list[relay_pin]): #True is relay off low level
        GPIO.output(pin_list[relay_pin],GPIO.HIGH)
    else:
        GPIO.output(pin_list[relay_pin],GPIO.LOW)

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

res_test()
