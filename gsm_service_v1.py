#!/usr/bin/python3
import os
import serial
import time
import yaml
from datetime import datetime

#Enable Serial Communication
# port = serial.Serial('/dev/ttyUSB0', 
# 					baudrate=115200, 
# 					bytesize=8, 
# 					parity='N',
# 					stopbits=1, 
# 					timeout=1)

port = serial.Serial('COM11', baudrate=115200, timeout=1)

#with open('/home/pi/sentinel/configs/options.yaml') as file:
with open(os.path.join(os.getcwd(), 'options.yaml')) as file:
	global opt
	opt = yaml.load(file, Loader=yaml.FullLoader)

def fileChanged(lastupload, queue):
	newTime = os.path.getmtime(queue)
	return newTime != lastupload

def timeout(sec=60):
	to = time.time() + sec
	return to > time.time()

def wrPort(command, nread=100, sleep=0.5):	
	port.write(str.encode(command+'\r\n'))
	time.sleep(0.5)
	port.flush()
	time.sleep(sleep)
	#Espera a que devuelva algo el módulo y lee (depende de la función)
	#Leo 100 bytes más del largo del mensaje original (quizás es medio exagerado que sean 100)
	rcv = port.read(len(command)+nread)
	time.sleep(0.5)
	port.flush()
	rcv= rcv.decode('utf-8')
	print(rcv)
	return rcv

def slowRead(command, expectedString, nread=100, sec=60):
	port.write(str.encode(command+'\r\n'))
	time.sleep(0.5)
	port.flush()
	rcv=""
	while timeout(sec):
		rcvTest = port.read(nread)
		time.sleep(0.5)
		rcvTest=rcvTest.decode('utf-8')
		print("rcvTest:",rcvTest)
		if rcvTest:
			rcv=rcvTest
			if expectedString in rcv:
				return True, rcv
		time.sleep(0.5)
	return False, rcv

def isOn(sec=60):
	on, AT = slowRead("AT", 'OK')
	print(AT)
	return on, AT

def checkSignal():
	AT = wrPort('AT+CREG?')
	return '0,1' in AT

def connectAPN(APN):
	wrPort('AT+SAPBR=3,1,"APN",'+APN)
	AT = wrPort('AT+SAPBR=1,1')
	time.sleep(5)
	return 'OK' in AT

def checkIP():
	AT = wrPort('AT+SAPBR=2,1')
	return '"0.0.0.0"' not in AT	

def initHTTP():
	wrPort('AT+HTTPINIT')
	wrPort('AT+HTTPPARA="CID",1')
	wrPort('AT+HTTPPARA="REDIR",0')
	wrPort('AT+HTTPSSL=1')
	return 'HTTP config OK'

def termHTTP():
	wrPort('AT+HTTPTERM')
	return 'HTTP service terminated'

def sendData(url, data):
	if data.endswith('\n'):
		data=data[:-1]
	wrPort('AT+HTTPPARA="URL","'+url+data+'"')
	time.sleep(1)
	#AT = wrPort('AT+HTTPACTION=0', sleep=10)
	#upload = '0,302' in AT
	#return upload, AT
	upload, AT = slowRead('AT+HTTPACTION=0','0,302')
	return upload, AT


def uploadQueue(url, queue, offset):
	file=open(queue, mode='r+')
	file.seek(offset)
	line = file.readline()
	upload = False
	while line:
		upload, AT = sendData(url, line)
		print(f'upload: {upload}')
		print('Esto guardé en AT:\n'+AT, 'Fin de AT')
		if upload:
			offset=file.tell()
		else:
			file.close()
			return offset, upload
		line = file.readline()
	file.close()
	return offset, upload

def restartModule():
	wrPort('AT+CFUN=1,1')
	print('Restarting Module')
	time.sleep(5)

def disconnect():
	wrPort('AT+SAPBR=0,1')

def shutDown():
	wrPort('AT+CPOWD=1')

def main():

	#offset_file = opt['GSM']['offset_file']
	#with open(offset_file) as fp:
	#	global offset
	#	offset = int(fp.readline())
	with open(os.path.join(os.getcwd(), 'offset.tmp')) as file:
		global offset
		offset = int(file.readline())
	apn = opt['GSM']['apn']
	url = opt['GSM']['url']
	queue = opt['GSM']['queue']
	#timeout = time.time() + opt['GSM']['timeout']
	lastupload = 0
	while True:
		if isOn():
			if checkSignal():
				connectAPN(apn)
				if checkIP():
					initHTTP()

					while checkIP():
						if fileChanged(lastupload, queue):
							print('Uploading')
							offset,success = uploadQueue(url, queue, offset)
							lastupload = os.path.getmtime(queue)
						else:
							print("File hasn't changed")
							time.sleep(60)

					#with open(offset_file, 'w') as file:
					with open(os.path.join(os.getcwd(), 'offset.tmp'), 'w') as file:	    
						file.write(str(offset))
				else:
					print('I have signal but can\'t connect to the Internet')
				termHTTP()

			else:
				print('No signal. Reconnecting')
				time.sleep(1)

		else:
			raise AssertionError('No response from Module')
	

if __name__ == "__main__":
	try:
		main()
	except AssertionError as e:
		raise
	except KeyboardInterrupt:
		print('shutting down')
		time.sleep(2)
		wrPort('AT')
		with open(os.path.join(os.getcwd(), 'offset.tmp'), 'w') as file:	    
			file.write(str(offset))
		termHTTP()
		time.sleep(1)
		#shutDown()