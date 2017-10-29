import os
import glob
import time
from datetime import datetime
 
# Misc Variables
coolCount = 0
lastTemp = [0,0,0,0]
count = 0
day = 0
printToScreen = 1
on = 1
highFlag = 0  	#Indicates if the system has gone .5 degree over limit and recycled back on
fanInterval = 10
delayInterval = 0.1
probeInterval = 30
# Nightime temp limits
if day == 0:
    high = 72.0
    low = 71.1
# Daytime temp limits
else:
    high = 72.9
    low = 71.5

# AC UNIT COMMANDS
#VOLUMEUP: Fan Slow
#VOLUMEDOWN: Fan Fast
#UP: Temp Up
#DOWN: Temp Down
#POWER: Power
#PLAY: Cool
#SAVE: Energy Saver
#PAUSE: Fan only
#SLEEP: Sleep
#TIME: Timer
#SHUFFLE: Automatic Fan

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

# Remove existing log file if it exists
os.system('rm temp.log')
# Initial AC system setup
os.system('irsend SEND_ONCE fridgidaire_ac KEY_POWER')
time.sleep(delayInterval)
os.system('irsend SEND_ONCE fridgidaire_ac KEY_PLAY')
time.sleep(delayInterval)
os.system('irsend SEND_ONCE fridgidaire_ac KEY_VOLUMEUP')
if printToScreen:
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ', Starting AC with hi fan')
with open("temp.log", "a") as myfile:
    myfile.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ', Turning on AC to cool and hi fan\n')
	
while True:
	#myTime = datetime.now().hour + (datetime.now().minute / 60)
	#print('mytime:' + str(myTime))
	#if myTime > 9.5 and time < 6.5:
	#    high = highNight
	#    low = lowNight
	#else:
	#    high = highDay
	#    low = lowDay
	temps = read_temp()
	if printToScreen:
	    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', high=' + str(high) + ', low=' + str(low))

	# If temp is high and ac has been on, then make sure set to cool
	if temps[1] > high and on == 1:
            if coolCount == 0:
	        os.system('irsend SEND_ONCE fridgidaire_ac KEY_PLAY')
	        coolCount = 1

	# If temp is higher than +0.5 degrees and ac is on, then system is actually off and needs to be turned on
	if temps[1] >= high + 0.5 and on == 1 and highFlag == 0:
	    os.system('irsend SEND_ONCE fridgidaire_ac KEY_POWER')
	    time.sleep(delayInterval)
	    os.system('irsend SEND_ONCE fridgidaire_ac KEY_PLAY')
	    time.sleep(delayInterval)
	    highFlag = 1

	# If system is off and temp is above high limit, need to turn on 
	if temps[1] > high and on == 0:
	    os.system('irsend SEND_ONCE fridgidaire_ac KEY_POWER')
	    time.sleep(delayInterval)
	    os.system('irsend SEND_ONCE fridgidaire_ac KEY_PLAY')
	    time.sleep(delayInterval)
	    coolCount = 0
	    if day == 1:
	        os.system('irsend SEND_ONCE fridgidaire_ac KEY_VOLUMEUP')
            else:
	        os.system('irsend SEND_ONCE fridgidaire_ac KEY_VOLUMEDOWN')
	    on = 1
	    count = count + 1
	    if printToScreen:
	        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', Turning on AC to cool and hi fan' + ' count=' + str(count))
            with open("temp.log", "a") as myfile:
	        myfile.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', Turning on AC to cool and hi fan\n')

	# If system is on and goes below low limit then need to perform shutdown process
	if temps[1] < low and on == 1:
	    os.system("irsend SEND_ONCE fridgidaire_ac KEY_PAUSE")
	    if printToScreen:
	    	print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', Changing AC to fan only')
            with open("temp.log", "a") as myfile:
	    	print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', Changing AC to fan only')
	    if day == 1:
	        os.system("irsend SEND_ONCE fridgidaire_ac KEY_VOLUMEDOWN")
	    	if printToScreen:
	    	    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', Day mode: changing to low fan')
            	with open("temp.log", "a") as myfile:
	    	    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', Day mode: changing to low fan')
	    time.sleep(fanInterval)
	    os.system('irsend SEND_ONCE fridgidaire_ac KEY_POWER')
	    on = 0
	    highFlag = 0
	    if printToScreen:
	        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', Turning AC off')
            with open("temp.log", "a") as myfile:
	        myfile.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Temp: ' + str(temps[1]) + 'F' + ', Turning AC off\n')
	lastTemp[2] = lastTemp[1]
	lastTemp[1] = lastTemp[0]
	lastTemp[0] = temps[1]
	time.sleep(probeInterval)
