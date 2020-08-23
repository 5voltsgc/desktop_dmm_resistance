import sys
import time
import pyvisa
from pyvisa import Resource
import datetime
import numpy as np

# Add system path to find relay_ Python packages
# sys.path.append('.')
# sys.path.append('..')

import relay_modbus
import relay_boards

# Required: Configure serial port, for example:
#   On Windows: 'COMx'
#   On Linux:   '/dev/ttyUSB0'
SERIAL_PORT = 'COM20'

# Optional: Configure board address with 6 DIP switches on the relay board
# Default address: 1
address = 1

# Optional: Give the relay board a name
board_name = '16 Relays'

# Create relay_modbus object
_modbus = relay_modbus.Modbus(serial_port=SERIAL_PORT, verbose=False)

# Open serial port
try:
    _modbus.open()
except relay_modbus.SerialOpenException as err:
    print(err)
    sys.exit(1)

# Create relay board object
board = relay_boards.R421A08(_modbus,
                             address=address,
                             board_name=board_name,
                             verbose=False)

rm = pyvisa.ResourceManager()

try:
    my_instrument: Resource = rm.open_resource('TCPIP::A-34461A-04348::inst0::INSTR')
except pyvisa.errors.VisaIOError as err:
    print(err)
    print("This might happen when the DMM is NOT turned on, or NOT on the network.")
    sys.exit(1)
# my_instrument = rm.open_resource('TCPIP0::192.168.000.43::inst0::INSTR')
my_instrument.read_termination = '\n'

# variables
NUM_CONDUCTORS = 8  # must be 8 or less, starts at 1 for 1 relay
sleep_time_DMM = .5  # Add a settling time for the relays, before DMM reading
sleep_time_relay = .025
units_under_test = "testing " + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
test_count = 0
INSULATION_LIMIT = 5.0e+6  # 5Meg or 5,000,000 ohms
RESISTANCE_LIMIT = 2  # Ohms
base_line_samples = 2  # Number of samples to be taken for base line 10 = 10 samples of each relay


uut_name = "hardcoded"
# uut_name = input("Please enter name of sample to be tested (Will be used in file name):")
filename = uut_name + "-" + datetime.datetime.now().strftime("%y%m%d-%H%M%S") + ".csv"

# Create numpy arrays and print
res_reading = np.empty(NUM_CONDUCTORS)
ins_reading = np.empty(NUM_CONDUCTORS)
base_line_resistance = np.empty(NUM_CONDUCTORS)
average_base_line_resistance = np.empty(NUM_CONDUCTORS)
print_var = ""
# Create log file header
log_header = "time, count, "
for j in range(0, NUM_CONDUCTORS):
    log_header = log_header + "Resistance Conductor-" + str(j + 1) + ","

log_header = log_header + "Pass/Fail ,"

for k in range(0, NUM_CONDUCTORS):
    log_header = log_header + "insulation-Conductor" + str(k + 1) + ","

log_header = log_header + "Pass/Fail"

# def relay_on(relay_number):
#     time.sleep(SleepTimeL)
#     try:
#         board.on(relay_number)
#     except pyvisa.errors.VisaIOError :


def relays_off():
    for p in range(1, 17):
        board.off(p)


def establish_base_line():
    baseline_sample = np.empty([NUM_CONDUCTORS, base_line_samples])
    relays_off()
    for o in range(0, base_line_samples):

        for n in range(0, NUM_CONDUCTORS):
            # print(str(n+1) + "-" + str(16-n))
            time.sleep(sleep_time_relay)
            board.on(n+1)
            time.sleep(sleep_time_relay)
            board.on(16-n)

            my_instrument.write('MEAS:FRES? 100 OHM')
            baseline_sample[n, o] = float(my_instrument.read_bytes(15))

            board.off(n+1)

            time.sleep(sleep_time_relay)
            board.off(16-n)

    # Insulation Test for the base line
    # Turn on all B side relays
    for r in range(9, 19):
        board.on(r)
        # time.sleep(SleepTimeL)

    for e in range(0, NUM_CONDUCTORS):

        # Turn on A side relay
        board.on(e + 1)
        time.sleep(sleep_time_relay)

        # Turn off matching relay for insulation check
        board.off(16 - e)

        time.sleep(sleep_time_DMM)
        my_instrument.write('MEAS:FRES? 100000000 OHM')  # 100M Ohms
        ins_reading[e] = float(my_instrument.read_bytes(15))

        board.on(16 - e)
        time.sleep(sleep_time_relay)
        board.off(e + 1)
        time.sleep(sleep_time_relay)

    relays_off()
    global average_base_line_resistance
    average_base_line_resistance = baseline_sample.mean(axis=1)


def insulation_test():
    global print_var
    ins_test_pass = True
    relays_off()

    # Turn on all B side relays
    for r in range(9, 19):
        board.on(r)

    for e in range(0, NUM_CONDUCTORS):
        # Turn on A side relay
        time.sleep(sleep_time_relay)
        board.on(e + 1)

        # Turn off matching relay for insulation check
        time.sleep(sleep_time_relay)
        board.off(16 - e)

        time.sleep(sleep_time_DMM)
        my_instrument.write('MEAS:FRES? 100000000 OHM')  # 100M Ohms
        ins_reading[e] = float(my_instrument.read_bytes(15))

        # turn on B side relay that was turned off for the insulation test
        time.sleep(sleep_time_relay)
        board.on(16 - e)

        # Turn off the A side relay, preparing for loop to next relay
        time.sleep(sleep_time_relay)
        board.off(e + 1)

        # test if the insulation resistance is less then limit
        if ins_reading[e] < INSULATION_LIMIT:
            ins_test_pass = False

        print_var = print_var + str(ins_reading[e]) + ","

    time.sleep(sleep_time_relay)
    relays_off()
    print_var = print_var + str(ins_test_pass)


def resistance_test():
    # test resistance between two matching conductors, it should be less than 100 ohms, so set the DMM range to match
    global test_count

    global print_var
    global RESISTANCE_LIMIT

    resistance_test_pass = True
    test_count += 1

    # print var is erased and the first two columns added
    print_var = str(datetime.datetime.now()) + "," + str(test_count) + ","

    # Make sure all relays are off
    relays_off()

    for m in range(0, NUM_CONDUCTORS):
        time.sleep(sleep_time_relay)
        board.on(m + 1)
        time.sleep(sleep_time_relay)
        board.on(16 - m)

        time.sleep(sleep_time_DMM)
        my_instrument.write('MEAS:FRES? 100 OHM')
        res_reading[m] = float(my_instrument.read_bytes(15))

        time.sleep(sleep_time_relay)
        board.off(m + 1)
        time.sleep(sleep_time_relay)
        board.off(16 - m)

        print_var = print_var + str(round(res_reading[m], 4)) + ","

        #  pass fail based on base line
        if RESISTANCE_LIMIT < (res_reading[m] - average_base_line_resistance[m]):
            resistance_test_pass = False

    print_var = print_var + str(resistance_test_pass) + ","


def results():
    with open(filename, 'a') as f:
        if test_count == 1:
            f.write(log_header)
            f.write('\n')

        f.write(print_var)
        f.write('\n')
        f.close()
        print(print_var)


# this is where the testing loop begins
try:
    print("Welcome to the cable resistance tester")
    print("Checking connections and establishing base line resistance values - please wait ~2 minutes")
    establish_base_line()
    print(average_base_line_resistance)
    print(ins_reading)
    x = input("Are these base line values expected?  [Y/N]: ")

    run = False
    if x == "y" or x == "Y":
        run = True

    print("Beginning testing, to stop pre CTRL c")
    print("The log filename will be: " + str(filename))

    # The first test_count header has the header info for the CSV file
    print(log_header)

    while run:
        resistance_test()
        insulation_test()
        results()

except KeyboardInterrupt:
    relays_off()
    print("The log file name is: " + str(filename))
