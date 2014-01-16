import serial #pyserial-2.6
import struct
import time
import binascii

class BillAcceptor:
	"""
		configure the serial connections (the parameters differs on the device you are connecting to)
	"""
	def __init__(self):
		self.serial = serial.Serial(
		    port = '/dev/ttyUSB0',
		    baudrate = 9600,
		    parity = serial.PARITY_EVEN,
		    stopbits = serial.STOPBITS_ONE,
		    bytesize = serial.SEVENBITS
		)
		self.stacking = False
		self.escrowed = False
		self.totalInserted = 0
	def close(self):
		self.serial.flushInput()
		self.serial.flushOutput()
		self.serial.close()
	"""
		convert the status codes into human readable format
	"""
	def status(self, received):
		status = 'NOT DEFINED'
		if received[3] == 1:
			status = 'IDLE'
		elif received[3] == 2:
			status = 'ACCEPTING'
		elif received[3] == 4:
			status = 'ESCROWED'
			self.escrowed = True
		elif received[3] == 8:
			status = 'STACKING'
			self.stacking = True
		elif received[3] == '\x10':
			status = 'STACKED'
		elif received[3] == '\x20':
			status = 'RETURNING'
		elif received[3] == '\x40':
			status = 'RETURNED'
		elif received[4] == 1:
			status = 'CHEATED'
		elif received[4] == 2:
			status = 'REJECTED'
		elif received[4] == 4:
			status = 'JAMMED'
		elif received[4] == 8:
			status = 'FULL'
		elif received[4] == '\x10':
			status = 'CASSETTE'
		elif received[5] == 1:
			status = 'POWER'
		elif received[5] == 2:
			status = 'INVALID'
		elif received[5] == 4:
			status = 'FAILURE'
		return status;
	"""
		determine how much money was inserted, in increase order from 0-7, RM1, RM5, RM10, RM20, RM50, RM100
		depending on the configuration card used
	"""
	def receivedCredit(self, received):
		credit = 0
		if received[5] == 0:
			credit = 0	
		elif received[5] == 0x08:
			credit = 1
		elif received[5] == 0x10:
			credit = 5
		elif received[5] == 0x18:
			credit = 10
		elif received[5] == 0x20:
			credit = 20
		elif received[5] == 0x28:
			credit = 50
		elif received[5] == 0x30:
			credit = 100
		elif received[5] == 0x38:
			credit = 0 #unused
		if self.stacking:
			self.totalInserted += credit
			self.escrowed = False
			self.stacking = False
		return credit
	"""

	"""
	def verifyCheckSum(self, received):
		if(received[1] ^ received[2] ^ received[3] ^ received[4] ^ received[5] != received[10]):
			return False
		else:
			return True
	"""
		Construct the serial transmission messages and receipt of messages from the device
		IDLE message : '\x02\x08\x11\x7f\x10\x00\x03\x76' alternating with '\x02\x08\x10\x7f\x10\x00\x03\x77'
	"""
	def run(self, i, stacking):
		#stx 02h The start of a message is inidicated by one byte
		transmit = []
		transmit.insert(0,0x02)
		#length 08h One byte representation of the nuber of bytes in each message (binary), including the stc, etc and the checksum
		transmit.insert(1,0x08)
		#msg type and ack number msg type 1 for master to slave (acceptor) messages, ack number 0 or 1 used to identify the messages sent by the master
		if(i % 2 == 0) :
			transmit.insert(2, 0x10)
		else:
			transmit.insert(2, 0x11)
		#data portion of the message, the data
		#10 and 1 , bit 3 and bit 1
		transmit.insert(3, 0x05)
		if (self.escrowed and stacking == True):
			transmit.insert(4, 0x20) #x20 stack
		elif(self.escrowed and stacking == False):
			transmit.insert(4, 0x40) #x40 return
		else: #not in escrowed state
			transmit.insert(4, 0x10) #x10 escrow, idle behaviour
		transmit.insert(5, 0x00)
		#etx 03h end of the message byte
		transmit.insert(6, 0x03)
		#calculate checksum, xor(length, msg type and ack number, data fields...)
		transmit.insert(7, transmit[1] ^ transmit[2] ^ transmit[3] ^ transmit[4] ^ transmit[5])
		input = bytearray(transmit)
		self.serial.write(input)
		time.sleep(0.1) #very important to wait for data from the acceptor
		statusObj = None
#		j=0
		while self.serial.inWaiting() != 0:
#			print binascii.b2a_hex(self.serial.read() )
#			j += 1
#			print j
			data = self.serial.read(11)
			received = struct.unpack('11B', data)
			if(self.verifyCheckSum(received) ):
				statusObj = {'status': self.status(received), 'received': self.receivedCredit(received), 'total': self.totalInserted}
			else:
				statusObj = None
		return statusObj
