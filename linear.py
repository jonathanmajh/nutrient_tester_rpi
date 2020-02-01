# Uses the smbus2 library to send and receive data from a Tic.
# Works on Linux with either Python 2 or Python 3.
#
# NOTE: The Tic's control mode must be "Serial / I2C / USB".
# NOTE: For reliable operation on a Raspberry Pi, enable the i2c-gpio
#   overlay and use the I2C device it provides (usually /dev/i2c-3).
# NOTE: You might nee to change the 'SMBus(3)' line below to specify the
#   correct I2C device.
# NOTE: You might need to change the 'address = 11' line below to match
#   the device number of your Tic.
 
from smbus2 import SMBus, i2c_msg
import time
 
class TicI2C(object):
  def __init__(self, bus, address):
    self.bus = bus
    self.address = address
 
  # Sends the "Exit safe start" command.
  def exit_safe_start(self):
    command = [0x83]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)
 
  # sends the "Enter safe start" command
  def enter_safe_start(self):
    command = [0x8F]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # sends the "Energize" command
  def energize(self):
    command = [0x85]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # sends the "De engerize" command
  def de_energize(self):
    command = [0x86]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # Sets the target position.
  #
  # For more information about what this command does, see the
  # "Set target position" command in the "Command reference" section of the
  # Tic user's guide.
  def set_target_position(self, target):
    command = [0xE0,
      target >> 0 & 0xFF,
      target >> 8 & 0xFF,
      target >> 16 & 0xFF,
      target >> 24 & 0xFF]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)
 
  # Gets one or more variables from the Tic.
  def get_variables(self, offset, length):
    write = i2c_msg.write(self.address, [0xA1, offset])
    read = i2c_msg.read(self.address, length)
    self.bus.i2c_rdwr(write, read)
    return list(read)
 
  # Gets the "Current position" variable from the Tic.
  def get_current_position(self):
    b = self.get_variables(0x22, 4)
    position = b[0] + (b[1] << 8) + (b[2] << 16) + (b[3] << 24)
    print(position)
    if position >= (1 << 31):
      position -= (1 << 32)
    return position
 
# Open a handle to "/dev/i2c-3", representing the I2C bus.
bus = SMBus(1)
 
# Select the I2C address of the Tic (the device number).

 
tic1 = TicI2C(bus, 14)
tic2 = TicI2C(bus, 15)
 
position = tic1.get_current_position()
print("Tic1 Current position is {}.".format(position))
position = tic2.get_current_position()
print("Tic2 Current position is {}.".format(position))
 
new_target = -1000
print("Setting target position to {}.".format(new_target));
tic1.exit_safe_start()
tic1.set_target_position(new_target)
tic2.exit_safe_start()
tic2.set_target_position(new_target)
tic1.energize()
tic2.energize()
print("finished setting new position")
print("sleeping 10 seconds")
time.sleep(10)
tic1.de_energize()
tic2.de_energize()