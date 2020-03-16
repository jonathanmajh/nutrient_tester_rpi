import time
from typing import List

from smbus2 import SMBus

import maestro
from linear import TicI2C


def move_water_linear(positions: List[int]):
    """
    positions is an array of positions for the linear acturator to move to
    position is 0 to -4000 (extended)
    """
    tic = TicI2C(SMBus(1), 14)
    position = tic.get_current_position()
    print("Tic (14) Current position is {}.".format(position))

    tic.exit_safe_start()
    tic.energize()
    for position in positions:
        tic.set_target_position(position)
        time.sleep(10) # 10 seconds

    tic.de_energize()

def move_reactant_linear(completed: int):
    """
    based moves actuator based on how many tests have been completed
    position is 0 to -4000 (extended)
    Each test need to move 13 (0.15 mm)
    """
    tic = TicI2C(SMBus(1), 15)
    position = tic.get_current_position()
    print("Tic (15) Current position is {}.".format(position))

    tic.exit_safe_start()
    tic.energize()
    tic.set_target_position(int(-1*completed * 13.3333333)) # TODO displacement for each test
    time.sleep(1)
    # should syringe be pulled back a bit after outputing an amount of reactant?
    tic.de_energize()


def move_water_valve(position):
    """
    move the rotation servo
    Positions:
    1. Outlet, Syringe
    2. Inlet, Syringe
    """
    # valid position from 3000 - 10000
    if position == 1:
        target = 3000
    elif position == 2:
        target = 10000
    servo = maestro.Controller()
    servo.setTarget(4, target) # turn continuous servo
    time.sleep(2)
