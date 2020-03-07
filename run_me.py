# from rotation_servos import *

# servo = MaestroUART()

# print(servo.get_error())

# servo.set_acceleration(0, 5)
# servo.set_speed(0, 32)
# print('position ' + servo.get_position(0))

# servo.set_target(0, 8000)

# servo.close()

from linear import TicI2C
from smbus2 import SMBus
import time
bus = SMBus(1)

tic1 = TicI2C(bus, 14)
tic2 = TicI2C(bus, 15)

position = tic1.get_current_position()
print("Tic1 Current position is {}.".format(position))
position = tic2.get_current_position()
print("Tic2 Current position is {}.".format(position))

new_target = -1000
new_target = int(input('please enter new position (0, -5000): '))
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