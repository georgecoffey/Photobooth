import serial

port = serial.Serial("/dev/serial0", baudrate=57600, timeout=3.0)

while True:
	port.write(255)


