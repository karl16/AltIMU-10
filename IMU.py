#acutal program for IMU readings v1.0

import csv
import functions
import time
import sys
from smbus import SMBus

busNum = 1
b = SMBus(busNum)
LSM = 0x1d #address on the raspberry pi
LSM_WHOAMI = 0b1001001 #Device self-id

LPS = 0x5d #address on the raspberry pi
LPS_WHOAMI = 0b10111101 #Device self-id

L3G = 0x6b #address on the raspberry pi
L3G_WHOAMI = 0b11010111 #Device self-id

if b.read_byte_data(LSM, 0x0f) == LSM_WHOAMI:
    print 'LSM303D detected successfully.'
else:
    print 'No LSM303D detected on bus '+str(busNum)+'.'
	sys.exit()
	
if b.read_byte_data(LPS, 0x0f) == LPS_WHOAMI:
    print 'LPS25H detected successfully.'
else:
    print 'No LPS25H detected on bus '+str(busNum)+'.'
	sys.exit()
	
if b.read_byte_data(L3G, 0x0f) == L3G_WHOAMI:
    print 'L3GD20H detected successfully.'
else:
    print 'No L3GD20H detected on bus '+str(busNum)+'.'
	sys.exit()

#the functions used
twosCompCombine = functions.twos_comp_combine	#takes two arguments
twosCompCombine12Bit = functions.twos_comp_combine_12	#takes two arguments
celsiusToFahrenheit = functions.c_to_f	#takes one argument
convertMag = functions.convert_mag	#takes one argument
convertAcc = functions.convert_acc	#takes one argument
convertGyro = functions.convert_gyro	#takes one argument
convertBarometer = functions.convert_barometer	#takes one argument
convertTemp = functions.convert_temp	#takes one argument
convertTempLPS = functions.convert_temp_LPS # takes one argument
pressureToAltitude = functions.pressure_to_atlitude_meters	#takes one argument	
vectorLength = functions.vector_length	#takes three agruments

#Control register addresses -- from LSM303D datasheet(acc and mag)
LSM_CTRL_0 = 0x1F #General settings
LSM_CTRL_1 = 0x20 #Turns on accelerometer and configures data rate
LSM_CTRL_2 = 0x21 #Self test accelerometer, anti-aliasing accel filter
LSM_CTRL_3 = 0x22 #Interrupts
LSM_CTRL_4 = 0x23 #Interrupts
LSM_CTRL_5 = 0x24 #Turns on temperature sensor
LSM_CTRL_6 = 0x25 #Magnetic resolution selection, data rate config
LSM_CTRL_7 = 0x26 #Turns on magnetometer and adjusts mode

#Control register addresses -- from L3GD20H datasheet (GYRO)
L3G_CTRL_1 = 0x20 #Turns on Gyro and configures data rate
L3G_CTRL_2 = 0x21 #Filter mode and edge or level sensitive enable 
L3G_CTRL_3 = 0x22 #Interrupts
L3G_CTRL_4 = 0x23 #Interrupts and also self test
L3G_CTRL_5 = 0x24 #General settings

#Control register addresses -- from LPS25H datasheet (barometer/altimeter)
LPS_CTRL_1 = 0x20 #
LPS_CTRL_2 = 0x21 #General settings
LPS_CTRL_3 = 0x22 #
LPS_CTRL_4 = 0x23 #
LPS_CTRL_5 = 0x24 #Interrupts called INTERRUPT_CFG
LPS_CTRL_6 = 0x25 #Interrupt called INT_SOURCE

#LSM303D
#Registers holding twos-complemented MSB and LSB of magnetometer readings -- from LSM303D datasheet
MAG_X_LSB = 0x08 # x
MAG_X_MSB = 0x09
MAG_Y_LSB = 0x0A # y
MAG_Y_MSB = 0x0B
MAG_Z_LSB = 0x0C # z
MAG_Z_MSB = 0x0D
#Registers holding twos-complemented MSB and LSB of magnetometer readings -- from LSM303D datasheet
ACC_X_LSB = 0x28 # x
ACC_X_MSB = 0x29
ACC_Y_LSB = 0x2A # y
ACC_Y_MSB = 0x2B
ACC_Z_LSB = 0x2C # z
ACC_Z_MSB = 0x2D
#Registers holding 12-bit right justified, twos-complemented temperature data -- from LSM303D datasheet
TEMP_MSB = 0x05
TEMP_LSB = 0x06

#LPS25H
#Registers holding the 12-bit two's complemented pressure data-- from datasheet LPS25H
PRESS_XL = 0x28 #lowest part of the pressure
PRESS_L = 0x29 #middle part of the pressure
PRESS_H = 0x2A # highest part of the pressure 
#registers holding 12-bit twos-complemented temperature data-- from datasheet LPS25H
TEMP_L = 0x2B #low part of temperature
TEMP_H = 0x2C #high part of the temperature

#L3GD20H
#Registers holding twos-complemented gyro readings -- L3GD20H datasheet
GYRO_X_L = 0x28 #X
GYRO_X_H = 0x29 
GYRO_Y_L = 0x2A #Y
GYRO_Y_H = 0x2B 
GYRO_Z_L = 0x2C #Z 
GYRO_Z_H = 0x2D 

#setting the IMU to the correct settings
b.write_byte_data(LSM, LSM_CTRL_1, 0b01010111) # enable accelerometer, 50 hz sampling
b.write_byte_data(LSM, LSM_CTRL_2, 0x00) #set +/- 2g full scale
b.write_byte_data(LSM, LSM_CTRL_5, 0b11100100) #high resolution mode, thermometer on, 6.25hz ODR
b.write_byte_data(LSM, LSM_CTRL_7, 0b00010000) #get magnetometer out of low power mode, and enables thermometer to take readings

#sleep while it is being put into rocket
time.sleep(15) #sleeps for 15 seconds before taking readings


#take initial readings
accx = twosCompCombine(b.read_byte_data(LSM, ACC_X_MSB), b.read_byte_data(LSM, ACC_X_LSB))
accy = twosCompCombine(b.read_byte_data(LSM, ACC_Y_MSB), b.read_byte_data(LSM, ACC_Y_LSB))
accz = twosCompCombine(b.read_byte_data(LSM, ACC_Z_MSB), b.read_byte_data(LSM, ACC_Z_LSB))
#convert to usable values
accx = convertAcc(accx)
accy = convertAcc(accy)
accz = convertAcc(accz)
#make into a single value
overallAcc = vectorLength(accx, accy, accz)

#waits until the acceleration is higher than 1 g
while(overallAcc <= 1):
	accx = twosCompCombine(b.read_byte_data(LSM, ACC_X_MSB), b.read_byte_data(LSM, ACC_X_LSB))
	accy = twosCompCombine(b.read_byte_data(LSM, ACC_Y_MSB), b.read_byte_data(LSM, ACC_Y_LSB))
	accz = twosCompCombine(b.read_byte_data(LSM, ACC_Z_MSB), b.read_byte_data(LSM, ACC_Z_LSB))
	#convert to usable values
	accx = convertAcc(accx)
	accy = convertAcc(accy)
	accz = convertAcc(accz)
	#make into a single value
	overallAcc = vectorLength(accx, accy, accz)

#after exiting loop it prints the acceleration
#print(overallAcc)

#for barometer/altimeter(LPS25H)
b.write_byte_data(LPS, LPS_CTRL_1, 0b11000000) #enables barometer/altimeter sets data rate to 25HZ 


#for Gyro(L3GD20H)
b.write_byte_data(L3G, 0x39, 0b00001) #sets ODR to 1
b.write_byte_data(L3G, L3G_CTRL_1, 0b11101111) #enables gyro 50HZ sampling ODR and 16.6 HZ cut-off 
b.write_byte_data(L3G, L3G_CTRL_2, 0x00) #set high pass filter cut off frequency to 4 HZ

#writing to a file
with open ('imu.csv', 'w') as file:
	fileScan = csv.writer(file, delimiter = ',')
	fileScan.writerow(['Reading Number', 'Acceleration', 'Gyro', 'Pressure', 'Altitude', 'Temperature'])
	readingNumber = 0

	endTime = time.time() + 5 	#gets current time then adds 5 seconds to it
	while time.time() < endTime:	#while loop will execute for 5 seconds
		#increase the reading number by one
		readingNumber += 1
		
		#takes acceleration readings and then converts them to usable values in one line
		accxLoop = convertAcc(twosCompCombine(b.read_byte_data(LSM, ACC_X_MSB), b.read_byte_data(LSM, ACC_X_LSB)))
		accyLoop = convertAcc(twosCompCombine(b.read_byte_data(LSM, ACC_Y_MSB), b.read_byte_data(LSM, ACC_Y_LSB)))
		acczLoop = convertAcc(twosCompCombine(b.read_byte_data(LSM, ACC_Z_MSB), b.read_byte_data(LSM, ACC_Z_LSB)))
		#make into a single value
		overallAccLoop = vectorLength(accxLoop, accyLoop, acczLoop)
		
		#takes Gyro readings then converts to usable values in one line
		gyroxLoop = convertGyro(twosCompCombine(b.read_byte_data(L3G, GYRO_X_H), b.read_byte_data(L3G, GYRO_X_L)))
		gyroyLoop = convertGyro(twosCompCombine(b.read_byte_data(L3G, GYRO_Y_H), b.read_byte_data(L3G, GYRO_Y_L)))
		gyrozLoop = convertGyro(twosCompCombine(b.read_byte_data(L3G, GYRO_Z_H), b.read_byte_data(L3G, GYRO_Z_L)))
		#make into a single value
		overallGyroLoop = vector_length(gyroxLoop, gyroyLoop, gyrozLoop)
		
		#takes pressure reading
		pressureTempLoop = twos_comp_combine(b.read_byte_data(LPS, PRESS_H), b.read_byte_data(LPS, PRESS_L))
		pressureLoop = twos_comp_combine(pressureTempLoop, b.read_byte_data(LPS, PRESS_XL))
		#converts to usable values
		pressureLoop = convert_barometer(pressureLoop)
		
		#Converts pressure to altitude (using the 1976 US Standard Atmosphere model)
		altitudeLoop = pressureToAltitude(pressureLoop)
		
		#This temperature data is from LPS25H
		#takes temperature readings and converts to usable data
		temperatureLoop = -1 * convertTempLPS(twosCompCombine(b.read_byte_data(LPS, TEMP_H), b.read_byte_data(LPS, TEMP_L)))
		#changes temperature from Celsius to Fahrenheit
		temperatureLoop = celsiusToFahrenheit(temperatureLoop)
		
		#writes to the file
		fileScan.writerow([readingNumber, overallAccLoop, overallGyroLoop, pressureLoop, altitudeLoop, temperatureLoop])
	
#Exits the loop
print("Done")

#Each take the same amount of readings
#But the amount varies it is about for every 5 seconds between 350-450 readings 

