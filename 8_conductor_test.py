#!/usr/bin/python
import RPi.GPIO as GPIO
import datetime
import pyvisa


GPIO.setmode(GPIO.BCM)

pinList = [4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12]
for i in pinList:
    GPIO.setup(i,GPIO.OUT)
    GPIO.output(i,GPIO.HIGH)
    
Cable_1A_Black = 4
Cable_1A_White = 17
Cable_1A_Red = 27
Cable_1A_Green = 22
Cable_1B_Black = 10
Cable_1B_White = 9
Cable_1B_Red = 11
Cable_1B_Green = 5
Cable_2A_Black = 6
Cable_2A_White = 13
Cable_2A_Red = 19
Cable_2A_Green = 26
Cable_2B_Black = 21
Cable_2B_White = 20
Cable_2B_Red = 16
Cable_2B_Green = 12

resistance_List=[]
for k in range(0,24):
    resistance_List.append(k)


filename =  "results1-8-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"
units_under_test = "testing"
# units_under_test =  input("Enter name of test samples or units under test:")
loop_count = 1

resistance_List=[]
for k in range(0,16):
    resistance_List.append(k)

#create string to hold resistance readings, and file

res_readings = units_under_test + "\n" + "Time, Counter, Test 1 - continuity,Test 2 - crosstalk,Test 3 - continuity,Test 4 - crosstalk, Test 5 - continuity, Test 6 - crosstalk, Test 7 - continuity, Test 8 - crosstalk \n"


with open(filename, 'a') as f:
    f.write(res_readings)
    f.write('\n')
    f.close
    res_readings =  str(datetime.datetime.now()) + "," + str(loop_count)+ ","


# turn off all relays, even ones not turned on to simplify functions 
def relays_off():
    for j in pinList:
        GPIO.output(j,GPIO.HIGH)

def read_resistance():
    my_instrument.write('MEAS:FRES? 100 OHM')
    
#     # the text from the meter is b'+9.77261930E+00'
    res = float(my_instrument.read_bytes(15))
    global res_readings 
    res_readings +=  str(res) + ","
    
    #add error checking like hard coded resitance upper and lower values


def read_crosstalk():
    my_instrument.write('MEAS:FRES? 100000000 OHM') #100M Ohms
    
    # the text from the meter is b'+9.77261930E+00'
    res = float(my_instrument.read_bytes(15))
    global res_readings 
    
    res_readings +=  str(res) + ","
    
#     #add error checking like hard coded resitance upper and lower values    

#open desktop multimeter - change ip address as needed, for different networks
rm = pyvisa.ResourceManager()
my_instrument = rm.open_resource('TCPIP0::192.168.000.43::inst0::INSTR')
my_instrument.read_termination = '\n'



for k in range(0,100):
        
#     print("Test#1 - continuity")
    GPIO.output(Cable_1A_Black, GPIO.LOW)  
    GPIO.output(Cable_1B_Black,GPIO.LOW) 
    read_resistance()
    relays_off()


#     print("Test#2 -  cross talk")
    GPIO.output(Cable_1A_Black,GPIO.LOW)  
    GPIO.output(Cable_1B_White,GPIO.LOW) 
    GPIO.output(Cable_1B_Red,GPIO.LOW) 
    GPIO.output(Cable_1B_Green,GPIO.LOW) 
    read_crosstalk()
    relays_off()


#     print("Test#3 - continuity")
    GPIO.output(Cable_1A_White,GPIO.LOW)  
    GPIO.output(Cable_1B_White,GPIO.LOW)
    read_resistance()
    relays_off()


#     print("Test#4 -  cross talk")
    GPIO.output(Cable_1A_White,GPIO.LOW)  
    GPIO.output(Cable_1B_Black,GPIO.LOW)
    GPIO.output(Cable_1B_Red,GPIO.LOW) 
    GPIO.output(Cable_1B_Green,GPIO.LOW) 
    read_crosstalk()
    relays_off()

#     print("Test#5 - continuity")
    GPIO.output(Cable_1A_Red,GPIO.LOW)  
    GPIO.output(Cable_1B_Red,GPIO.LOW) 
    read_resistance()
    relays_off()


#     print("Test#6 -  cross talk")
    GPIO.output(Cable_1A_Red,GPIO.LOW)  
    GPIO.output(Cable_1B_Black,GPIO.LOW)  
    GPIO.output(Cable_1B_White,GPIO.LOW) 
    GPIO.output(Cable_1B_Green,GPIO.LOW) 
    read_crosstalk()
    relays_off()

#     print("Test#7 - continuity")
    GPIO.output(Cable_1A_Green,GPIO.LOW)  
    GPIO.output(Cable_1B_Green,GPIO.LOW) 
    read_resistance()
    relays_off()


#     print("Test#8 -  cross talk")
    GPIO.output(Cable_1A_Green,GPIO.LOW)  
    GPIO.output(Cable_1B_Black,GPIO.LOW)  
    GPIO.output(Cable_1B_White,GPIO.LOW) 
    GPIO.output(Cable_1B_Red,GPIO.LOW) 
    read_crosstalk()
    relays_off()

    with open(filename, 'a') as f:
        
        loop_count += 1
        f.write(res_readings)
        f.write('\n')
        f.close
        print(res_readings)
        res_readings = str(datetime.datetime.now()) + "," + str(loop_count)+ ","
        


# Reset GPIO settings
GPIO.cleanup()