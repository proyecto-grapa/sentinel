#!/usr/bin/python3
import serial
import time

#Enable Serial Communication
# port = serial.Serial('/dev/ttyUSB0', 
# 					baudrate=115200, 
# 					bytesize=8, 
# 					parity='N',
# 					stopbits=1, 
# 					timeout=1)

port = serial.Serial('COM11', baudrate=115200, timeout=1)

def timeout(sec=60):
	to = time.time() + sec
	return to > time.time()

def wrPort(command, nread=100, sleep=0.5):	
	port.write(str.encode(command+'\r\n'))
	time.sleep(0.5)
	port.flush()
	time.sleep(sleep)
	#Espera a que devuelva algo el módulo y lee (depende de la función)
	#Leo 100 bytes más del largo del mensaje original
	rcv = port.read(len(command)+nread)
	time.sleep(0.5)
	port.flush()
	rcv= rcv.decode('utf-8')
	print(rcv)
	return rcv

def isOn(sec=60):
	while timeout(sec):
		at = wrPort("AT")
		if 'OK' in at:
			return True
		time.sleep(1)
	return False

def checkSignal():
	AT = wrPort('AT+CREG?')
	return '0,1' in AT

def fullPower():
	return ('OK' in wrPort('AT+CFUN=1')) and ('OK' in wrPort('AT+CGATT=1'))	

def shutDown():
	return wrPort('AT+CPOWD=1')

def connectManually(ID=0):
	cops = wrPort("AT+COPS=?", nread=200, sleep=5)
	copsIDs = [int(s) for s in cops.split('"') if s.isdigit()]
	wrPort("AT+COPS=0")
	time.sleep(5)
	wrPort('AT+COPS=4,2,"'+copsIDs[ID]+'"')
	while timeout(120):
		rcv = port.read(200)
		if 'PSUTTZ' in rcv:
			print('Succesfully connected to', copsIDs[ID])
			return True
	return False

def main():
	#Me fijo que el módulo esté activo durante un minuto
	while timeout(1800):
		if isOn(60):
			if checkSignal() and fullPower():
				print('Module is fully operational')
				return True
			else:
				######
				connectManually()
		else:
			raise AssertionError('No response from Module')

	print('Timeout...')
	print('Shutting Down Module')
	shutDown()

if __name__ == "__main__":
	try:
		main()
	except AssertionError as e:
		raise
	except KeyboardInterrupt:
		time.sleep(1)
		print('Interrupted')
		time.sleep(0.2)
		print('Shutting Down Module')
		shutDown()