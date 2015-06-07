from evdev import InputDevice, _input, DeviceInfo
import os

class ReadInputDevice(InputDevice):
	def __init__(self, dev):
		'''
		:param dev: path to input device
		'''

		#: Path to input device.
		self.fn = dev

		#: A non-blocking file descriptor to the device file.
		self.fd = os.open(dev, os.O_RDONLY | os.O_NONBLOCK)

		# Returns (bustype, vendor, product, version, name, phys, capabilities).
		info_res = _input.ioctl_devinfo(self.fd)

		#: A :class:`DeviceInfo <evdev.device.DeviceInfo>` instance.
		self.info = DeviceInfo(*info_res[:4])

		#: The name of the event device.
		self.name = info_res[4]

		#: The physical topology of the device.
		self.phys = info_res[5]

		#: The evdev protocol version.
		self.version = _input.ioctl_EVIOCGVERSION(self.fd)

		#: The raw dictionary of device capabilities - see `:func:capabilities()`.
		self._rawcapabilities = _input.ioctl_capabilities(self.fd)

		#: The number of force feedback effects the device can keep in its memory.
		self.ff_effects_count = _input.ioctl_EVIOCGEFFECTS(self.fd)
