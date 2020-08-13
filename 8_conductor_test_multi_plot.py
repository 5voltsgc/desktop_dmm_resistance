#!/usr/bin/python
import RPi.GPIO as GPIO
import datetime
import pyvisa
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

y_range = [8, 11]  # Range of possible Y values to display
ax.set_ylim(8, 11)

xs = []
y1 = []
y2 = []
y3 = []
y4 = []
UL = []
LL = []


GPIO.setmode(GPIO.BCM)

pinList = [4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 21, 20, 16, 12]
for r in pinList:
    GPIO.setup(r,GPIO.OUT)
    GPIO.output(r,GPIO.HIGH)
    
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

SleepTimeL = 1

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


rm = pyvisa.ResourceManager()
my_instrument = rm.open_resource('TCPIP0::192.168.000.43::inst0::INSTR')
my_instrument.read_termination = '\n'

with open(filename, 'a') as f:
    f.write(res_readings)
    f.write('\n')
    f.close
    res_readings =  str(datetime.datetime.now()) + "," + str(loop_count)+ ","


# turn off all relays, even ones not turned on to simplify functions 
def relays_off():
    for j in pinList:
        GPIO.output(j,GPIO.HIGH)

# This function is called periodically from FuncAnimation
def animate(i, xs, y1):
    global y4
    global y2
    global y3
    global LL
    global UL
    
    # Draw x and y lists
    ax.clear()
    LL.append(9.5)
    UL.append(10)

    
    
    #     print("Test#1 - continuity")
    GPIO.output(Cable_1A_Black, GPIO.LOW)  
    GPIO.output(Cable_1B_Black,GPIO.LOW) 
    my_instrument.write('MEAS:FRES? 100 OHM')
    res = float(my_instrument.read_bytes(15))
    xs.append(i)
    y1.append(res)
    ax.plot(xs, y1)
    
    relays_off()
    
    ax.plot(xs, LL)
    ax.plot(xs, UL)
    
    # Draw x and y lists
    ax.plot(xs, y1)
    
    #     print("Test#3 - continuity")
    GPIO.output(Cable_1A_White,GPIO.LOW)  
    GPIO.output(Cable_1B_White,GPIO.LOW)
    my_instrument.write('MEAS:FRES? 100 OHM')
    res = float(my_instrument.read_bytes(15))
    y2.append(res)
    ax.plot(xs, y2)
    relays_off()
    
    #     print("Test#5 - continuity")
    GPIO.output(Cable_1A_Red,GPIO.LOW)  
    GPIO.output(Cable_1B_Red,GPIO.LOW) 
    my_instrument.write('MEAS:FRES? 100 OHM')
    res = float(my_instrument.read_bytes(15))
    y3.append(res)
    ax.plot(xs, y3)
    relays_off()
    
    
    #     print("Test#7 - continuity")
    GPIO.output(Cable_1A_Green,GPIO.LOW)  
    GPIO.output(Cable_1B_Green,GPIO.LOW)
    my_instrument.write('MEAS:FRES? 100 OHM')
    res = float(my_instrument.read_bytes(15))
    y4.append(res)
    ax.plot(xs, y4)
    relays_off()

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Resistance')
    plt.ylabel('OHMS')
    xs = xs[-200:]
    y1 = y1[-200:]
    y2 = y2[-200:]
    y3 = y3[-200:]
    y4 = y4[-200:]
    


#open desktop multimeter - change ip address as needed, for different networks

ani = animation.FuncAnimation(fig, animate, fargs=(xs, y1), interval=1000)

plt.show()
