import time
import maestro
from smbus2 import SMBus
from linear import TicI2C
from typing import List

def move_linear_water(positions: List[int]):
    """
    positions is an array of positions for the linear acturator to move to
    position is 0 - 5000 (extended)
    """
    tic1 = TicI2C(SMBus(1), 14)
    position = tic1.get_current_position()
    print("Tic (14) Current position is {}.".format(position))

    tic1.exit_safe_start()
    tic1.energize()
    for position in positions:
        tic1.set_target_position(position)
        time.sleep(10) # 10 seconds

    tic1.de_energize()

def move_valve(position):
    """
    move the rotation servo
    Positions:
    1. Outlet, Syringe
    2. Inlet, Syringe
    """
    if position == 1:
        target = 2000
    elif position == 2:
        target = 1000
    servo = maestro.Controller()
    servo.setAccel(1, 4)
    servo.setSpeed(1, 10)
    servo.setTarget(1, target) # turn continuous servo
    time.sleep(1)