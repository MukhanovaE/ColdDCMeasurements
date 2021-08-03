from Drivers import visa_device

class Keithley2651(visa_device.visa_device):

	def __init__(self, device_num):
		print('Initializing Keithley 2651 source, device address = ', device_num)
		super().__init__(device_num)
		
		self.SendString('smua.source.func = smua.OUTPUT_DCAMPS')
		
	def SetOutput(self, val):
		print('Output is', val, 'A')
		self.SendString(f"smua.source.leveli = {val}")
		
	def GetOutput(self):
		return self.GetFloat("print(smua.source.leveli)")
	
	def output_on(self):
		self.SendString("smua.source.output = 1")
		
	def output_off(self):
		self.SendString("smua.source.output = 0")
		
	# Voltage limit
	def limit(self, val=None):
		self.SendString(f"smua.source.limitv = {val}")
	
	def range(self, val = None):
		self.SendString(f"smua.source.rangei = {val}")
		
	def autorange(self, val):
		self.SendString(f"smua.source.autorangei = {int(val)}")
