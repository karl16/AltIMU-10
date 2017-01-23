#functions.py
#functions used by the IMU

import math

def twos_comp_combine(msb, lsb): 	#16 bit
    twos_comp = 256*msb + lsb
    if twos_comp >= 32768:
        return twos_comp - 65536
    else:
        return twos_comp
		
def twos_comp_combine_12(msb, lsb);		#12 bit
	twos_comp = 16*msb + lsb
	if twos_comp >=2048:
		return twos_comp - 4096
	else:
		return twos_comp
		
def c_to_f(x):		#converts celsius to fahrenheit
	return(x*9/5+32)
		
def convert_mag(x):		#converts raw magnetic readings to usable data (gauss)
	sensitivity = .000080
	return x*sensitivity
def convert_acc(x):		#converts raw acceleration readings to usable data (g)
	sensitivity = .000061
	return x*sensitivity 
def convert_gyro(x):	#converts raw gyro readings to usable data(degrees/ second)
	sensitivity = 1/131.0
	return x*sensitivity
def convert_barometer(x)	#converts raw pressure readings to usable data (hPa)
	sensitivity = 1/4096.0
	return x*sensitivity
def convert_temp(x)		#converts raw temperature readings to usable data for the LSM sensor(C). this one is not as percise as the LPS sensor
	return x/8
def convert_temp_LPS(x):	#converts raw temperature readings to usable data for the LPS sensor (C)
	sensitivity = 1/480.0
	return x * sensitivity
	
	
def pressure_to_altitude_meters(pressure):	#converts pressure(hPa) to meters above sea level
	return ((1 - math.pow(pressure / 1013.25, 0.190263)) * 44330.8)
	

def vector_length(x, y, z)	#converts xyz axis readings into a single reading
	num = math.sqrt(math.pow(x,2) + math.pow(y, 2) + math.pow(z,2))
	return num
	