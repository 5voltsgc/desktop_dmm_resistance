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
SleepTimeL = .75
units_under_test = "testing "+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
test_count = 0
insulation_limit = 5.0e+6  #5Meg or 5,000,000 ohms
base_line_samples = 2


uut_name = input("Please enter name of sample to be tested (Will be used in file name):")
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
    global bsline
    
    res_test_pass = True
    test_count += 1
    #print var is erased and the first two columns added
    print_var = str(datetime.datetime.now()) + "," + str(test_count)+ ","
    
    for m in range(num_conductors):
        GPIO.output(pin_list[m],GPIO.LOW)
        GPIO.output(pin_list[15-m] ,GPIO.LOW)
        time.sleep(SleepTimeL)
        my_instrument.write('MEAS:FRES? 100 OHM')
        res_reading[m] = float(my_instrument.read_bytes(15))
        
        print_var = print_var + str(round(res_reading[m],4)) + ","
        
        #add the pass fail when base line is done
        if 2 < (res_reading[m] - bsline[m]):
            res_test_pass = False
            
        relays_off()
    print_var = print_var + str(res_test_pass) +  ","


#Baseline Test()  
def establish_base_line():
    baseline_sample = np.empty([num_conductors,base_line_samples])

    for o in range(0,base_line_samples):
                
        for n in range(num_conductors):
            GPIO.output(pin_list[n],GPIO.LOW)
            GPIO.output(pin_list[15-n] ,GPIO.LOW)
            
            #setting time for relays
            time.sleep(SleepTimeL)
            my_instrument.write('MEAS:FRES? 100 OHM')
            baseline_sample[n,o] = float(my_instrument.read_bytes(15))
            
            relays_off()
        
        # Insulation Test    
    for e in range(num_conductors):
        #Turn on A side relay
        GPIO.output(pin_list[e],GPIO.LOW)
        
        #Turn on all B side relays
        for r in range(8, 16):
            GPIO.output(pin_list[r],GPIO.LOW)
        
        # Turn off matching relay for Cross talk check
        GPIO.output(pin_list[15-e],GPIO.HIGH)
        
        #give time for relays to make contact before measurment
        time.sleep(SleepTimeL)

        my_instrument.write('MEAS:FRES? 100000000 OHM') #100M Ohms
        ins_reading[e] = float(my_instrument.read_bytes(15))
    
        relays_off()
        

    global bsline
    bsline = baseline_sample.mean(axis=1)


def insulation_test():
    global print_var
    ins_test_pass = True
    
    for d in range(num_conductors):
        #Turn on A side relay
        GPIO.output(pin_list[d],GPIO.LOW)
        
        #Turn on all B side relays
        for r in range(8, 16):
            GPIO.output(pin_list[r],GPIO.LOW)
        
        # Turn off matching relay for Cross talk check
        GPIO.output(pin_list[15-d],GPIO.HIGH)
        
        #give time for relays to make contact before measurment
        time.sleep(SleepTimeL)

        my_instrument.write('MEAS:FRES? 100000000 OHM') #100M Ohms
        ins_reading[d] = float(my_instrument.read_bytes(15))
        
        #test if the insulation resistance is less then limit
        if ins_reading[d] < insulation_limit:
            ins_test_pass = False
               
        print_var = print_var + str(ins_reading[d]) + ","

        
        relays_off() 
    print_var = print_var + str(ins_test_pass)


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

def results():
   
    with open(filename, 'a') as f:
 
        if (test_count ==1):
            f.write(log_header)
            f.write('\n')
            
        f.write(print_var)
        f.write('\n')
        f.close
        print(print_var)
        
 
# here is where the testing loop begins 
try:
    establish_base_line()
    print(bsline)
    print(ins_reading)
    
    X = input("Are these baseline values expected? [y/n]: ")
    
    run = False
    if (X == "y" or X == "Y"):
        run = True
        
    print("Begining testing to stop press CTRL C")
    print("The log filename will be: " + str(filename))
    print(log_header)
    while run == True:
        res_test()
        insulation_test()
        results()


except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    GPIO.cleanup() # cleanup all GPIO    
    print("Log file name is: " + str(filename))
    
