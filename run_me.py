from rotation_servos.py import *

servo = MaestroUART()

print(servo.get_error())

servo.set_acceleration(0, 5)
servo.set_speed(0, 32)
print('position ' + servo.get_position(0))

servo.set_target(0, 8000)

servo.close()
