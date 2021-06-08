#!/usr/bin/python3
import os
import serial
import time
import yaml
from datetime import datetime

#Enable Serial Communication
port = serial.Serial('/dev/ttyUSB0', 
					baudrate=115200, 
					bytesize=8, 
					parity='N',
					stopbits=1, 
					timeout=3)

with open('/home/pi/sentinel/configs/options.yaml') as file:
	global opt
	opt = yaml.load(file, Loader=yaml.FullLoader)

def fileChanged(lastupload, queue):
	newTime = os.path.getmtime(queue)
	return newTime != lastupload

def wrPort(command, nread=100, sleep=0.5):	
	port.write(str.encode(command+'\r\n'))
	time.sleep(0.5+sleep)
	port.flush()
	rcv = port.read(len(command)+nread)
	time.sleep(0.5)
	try:
		rcv=rcv.decode('utf-8')
		print("rcv:",rcv)
		time.sleep(0.1)
	except UnicodeDecodeError:
		time.sleep(0.1)
		print('UnicodeDecodeError', rcv)
		port.flushInput()
		port.flushOutput()
		rcv=""
	return rcv

def slowRead(command, expectedStringOK='OK', expectedStringERROR='ERROR', nread=100, sec=60):
	port.write(str.encode(command+'\r\n'))
	time.sleep(1)
	port.flush()
	rcv=""
	to = time.time() + sec
	while to > time.time():
		rcvTest = port.read(nread)
		time.sleep(1)
		try:
			rcvTest=rcvTest.decode('utf-8')
			print("rcvTest:",rcvTest)
			time.sleep(0.5)
		except UnicodeDecodeError:
			time.sleep(0.5)
			print('UnicodeDecodeError', rcvTest)
			port.flushInput()
			port.flushOutput()
			rcvTest=""
		if rcvTest:
			rcv=rcvTest
			if expectedStringOK in rcv:
				return True, rcv
			elif expectedStringERROR in rcv:
				return False, rcv
		time.sleep(0.5)
	return False, rcv

def slowWrite(command, expectedStringOK='OK', expectedStringERROR='ERROR', nread=100, sec=60)
	nparts=80
	parts = [command[i:i+nparts] for i in range(0, len(command), nparts)]
	for part in parts:
		print('Input chunk:' part)
		port.write(str.encode(part))
		time.sleep(0.5)
	port.write(str.encode('\r\n'))
	time.sleep(1)
	port.flush()
	rcv=""
	to = time.time() + sec
	while to > time.time():
		rcvTest = port.read(nread)
		time.sleep(1)
		try:
			rcvTest=rcvTest.decode('utf-8')
			print("rcvTest:",rcvTest)
			time.sleep(0.5)
		except UnicodeDecodeError:
			time.sleep(0.5)
			print('UnicodeDecodeError', rcvTest)
			port.flushInput()
			port.flushOutput()
			rcvTest=""
		if rcvTest:
			rcv=rcvTest
			if expectedStringOK in rcv:
				return True, rcv
			elif expectedStringERROR in rcv:
				return False, rcv
		time.sleep(0.5)
	return False, rcv

def isOn(sec=60):
	on, AT = slowRead("AT")
	print(AT)
	return on, AT

def checkSignal():
	AT = wrPort('AT+CREG?')
	return '0,1' in AT

def connectAPN(APN):
	okApn,atApn = slowRead('AT+SAPBR=3,1,"APN",'+APN)
	if not okApn:
		print("APN config failed: "+atApn)
		return okApn
	okConn, atConn = slowRead('AT+SAPBR=1,1')
	return okConn

def checkIP():
	AT = wrPort('AT+SAPBR=2,1')
	#comparar string vacia
	return '"0.0.0.0"' not in AT	

def initHTTP():
	wrPort('AT+HTTPINIT')
	wrPort('AT+HTTPPARA="CID",1')
	wrPort('AT+HTTPPARA="REDIR",0')
	wrPort('AT+HTTPSSL=1')
	return 'HTTP config OK'

def termHTTP():
	time.sleep(0.5)
	port.flushInput()
	time.sleep(0.5)
	slowRead('AT+HTTPTERM')
	return 'HTTP service terminated'

def sendData(url, data):
	upload=False
	if data.endswith('\n'):
		data=data[:-1]
	print("Uploading: "+data+'\n')
	time.sleep(0.5)
	okUrl, AT=slowWrite('AT+HTTPPARA="URL","'+url+data+'"', sec=30)
	time.sleep(0.5)
	if okUrl:	
		upload, AT = slowRead('AT+HTTPACTION=0','0,302')
	else:
		print("HTTPPARA failed")
	return upload, AT


def uploadQueue(url, queue, offset):
	file=open(queue, mode='r+')
	file.seek(offset)
	line = file.readline()
	upload = False
	while line:
		upload, AT = sendData(url, line)
		print('upload:',upload)
		print('Saved in AT:\n'+AT, 'End of AT')
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

	offset_file = opt['GSM']['offset_file']
	global offset
	if os.path.isfile(offset_file):
		with open(offset_file) as fp:			
			offset = int(fp.readline())
	else:
		with open(offset_file, 'w') as file:
			offset = 0
			file.write(str(offset))

	queue = opt['GSM']['queue']
	if not os.path.isfile(queue):
		open(queue,'w').close()

	apn = opt['GSM']['apn']
	url = opt['GSM']['url']
	
	lastupload = 0
	while True:
		if isOn():
			if checkSignal():
				connectAPN(apn)
				if checkIP():
					initHTTP()
					while isOn() and checkIP():
						if fileChanged(lastupload, queue):
							print('Uploading')
							offset,success = uploadQueue(url, queue, offset)
							lastupload = os.path.getmtime(queue)
							if not success:
								termHTTP()
								initHTTP()
								success=True
						else:
							print("File hasn't changed")
							time.sleep(60)

					termHTTP()
					with open(offset_file, 'w') as file:					
						file.write(str(offset))
				else:
					print('I have signal but can\'t connect to the Internet')			
			else:
				print('No signal. Reconnecting')
				#Aca va gsm_startup	
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