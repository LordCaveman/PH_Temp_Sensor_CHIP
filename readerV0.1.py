import io
import fcntl  # used to access I2C parameters like addresses
import time  # used for sleep delay and timestamps
import string  # helps parse strings
import serial
import sys
from serial import SerialException

class AtlasI2C:
	long_timeout = 1.5  # the timeout needed to query readings and calibrations
	short_timeout = .5  # timeout for regular commands
	default_bus = 1  # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
	default_address = 98  # the default address for the sensor
	current_addr = default_address

	def __init__(self, address=default_address, bus=default_bus):
		# open two file streams, one for reading and one for writing
		# the specific I2C channel is selected with bus
		# it is usually 1, except for older revisions where its 0
		# wb and rb indicate binary read and write
		self.file_read = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
		self.file_write = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)

		# initializes I2C to either a user specified or default address
		self.set_i2c_address(address)

	def set_i2c_address(self, addr):
		# set the I2C communications to the slave specified by the address
		# The commands for I2C dev using the ioctl functions are specified in
		# the i2c-dev.h file from i2c-tools
		I2C_SLAVE = 0x703
		fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
		fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
		self.current_addr = addr

	def write(self, cmd):
		# appends the null character and sends the string over I2C
		cmd += "\00"
		self.file_write.write(cmd)

	def read(self, num_of_bytes=31):
		# reads a specified number of bytes from I2C, then parses and displays the result
		res = self.file_read.read(num_of_bytes)  # read from the board
		response = filter(lambda x: x != '\x00', res)  # remove the null characters to get the response
		if ord(response[0]) == 1:  # if the response isn't an error
			# change MSB to 0 for all received characters except the first and get a list of characters
			char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
			# NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
			return "Command succeeded " + ''.join(char_list)  # convert the char list to a string and returns it
		else:
			return "Error " + str(ord(response[0]))

	def query(self, string):
		# write a command to the board, wait the correct timeout, and read the response
		self.write(string)

		# the read and calibration commands require a longer timeout
		if ((string.upper().startswith("R")) or
				(string.upper().startswith("CAL"))):
			time.sleep(self.long_timeout)
		elif string.upper().startswith("SLEEP"):
			return "sleep mode"
		else:
			time.sleep(self.short_timeout)

		return self.read()

	def close(self):
		self.file_read.close()
		self.file_write.close()

	def list_i2c_devices(self):
		prev_addr = self.current_addr  # save the current address so we can restore it after
		i2c_devices = []
		for i in range(0, 128):
			try:
				self.set_i2c_address(i)
				self.read()
				i2c_devices.append(i)
			except IOError:
				pass
		self.set_i2c_address(prev_addr)  # restore the address we were using
		return i2c_devices

class AtlasUART:

	def __init__(self):

	def read_line(self,):
		"""
		taken from the ftdi library and modified to
		use the ezo line separator "\r"
		"""
		lsl = len('\r')
		line_buffer = []
		while True:
			next_char = ser.read(1)
			if next_char == '':
				break
			line_buffer.append(next_char)
			if (len(line_buffer) >= lsl and
						line_buffer[-lsl:] == list('\r')):
				break
		return ''.join(line_buffer)

	def read_lines():
		"""
		also taken from ftdi lib to work with modified readline function
		"""
		lines = []
		try:
			while True:
				line = read_line()
				if not line:
					break
					ser.flush_input()
				lines.append(line)
			return lines

		except SerialException as e:
			print
			"Error, ", e
			return None

	def send_cmd(cmd):
	"""
	Send command to the Atlas Sensor.
	Before sending, add Carriage Return at the end of the command.
	:param cmd:
	:return:
	"""
	buf = cmd + "\r"     	# add carriage return
	try:
		ser.write(buf)
		return True
	except SerialException as e:
		print "Error, ", e
		return None

def main():
	device0 = AtlasI2C
	device1 = AtlasUART

	while True:
		time.sleep(10)
		print(device0.query("R"))
		print(device1.query)


