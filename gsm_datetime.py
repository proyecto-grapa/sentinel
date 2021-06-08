#!/usr/bin/python3
import os
import serial
import time
from datetime import datetime,timedelta

import subprocess

#Enable Serial Communication
port = serial.Serial('/dev/ttyUSB0', 
 					baudrate=115200, 
 					bytesize=8, 
 					parity='N',
 					stopbits=1, 
					timeout=1)

#port = serial.Serial('COM11', baudrate=115200, timeout=1)

def wrPort(command, nread=100):	
	port.write(str.encode(command+'\r\n'))
	time.sleep(0.5)
	port.flush()
	#Espera a que devuelva algo el módulo y lee (depende de la función)
	#Leo 100 bytes más del largo del mensaje original
	rcv = port.read(len(command)+nread)
	port.flush()
	rcv= rcv.decode('utf-8')
	print(rcv)
	return rcv

def checkTime():
	return wrPort("AT+CCLK?")

def main():
	wrPort('AT')
	time.sleep(0.5)
	gsmTime = checkTime()

	dateStr = gsmTime = gsmTime.split('"')[1]
	gmtOffset= timedelta(hours=int(dateStr[-3:])/4) #Te lo mide en cuartos de hora
	dt = datetime.strptime(dateStr[:-3],"%y/%m/%d,%H:%M:%S") 
	#Para utilizar UTC:
	#dt = dt + gmtOffset
	print('Date and time (UTC): ' + dt.strftime('%Y/%m/%d %H:%M:%S'))
	subprocess.call(['sudo date -s '+'"'+dt.strftime('%Y/%m/%d %H:%M:%S')+'"'], shell=True)

	port.close()
if __name__ == "__main__":
	try:
		main()
	except AssertionError as e:
		raise
	except KeyboardInterrupt:
		print('Interrupted')
