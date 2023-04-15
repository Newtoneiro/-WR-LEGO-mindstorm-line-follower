#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent, MoveTank, Motor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor
from time import sleep
import sys

# output
engines = MoveTank(OUTPUT_D, OUTPUT_A)
switch = TouchSensor(INPUT_2)
motor = Motor(OUTPUT_B)
#input
left_sensor = ColorSensor(INPUT_1)
left_sensor.mode = left_sensor.MODE_COL_COLOR

right_sensor = ColorSensor(INPUT_4)
right_sensor.mode = right_sensor.MODE_COL_COLOR

def main():
    base_speed_percent = int(sys.argv[1])
    forward_turn_speed_percent = int(sys.argv[2])
    backward_turn_speed_percent = int(sys.argv[3])

    # dla 40 30 30
    # 35-40 to już zbyt szybko

    def go():
        while not switch.is_pressed:
            left = left_sensor.color
            right = right_sensor.color

            if left == ColorSensor.COLOR_NOCOLOR or right == ColorSensor.COLOR_NOCOLOR:
                engines.off()

            elif left == ColorSensor.COLOR_WHITE and right != ColorSensor.COLOR_WHITE : # right
                engines.on(SpeedPercent(forward_turn_speed_percent), SpeedPercent(-backward_turn_speed_percent))

            elif left != ColorSensor.COLOR_WHITE  and right == ColorSensor.COLOR_WHITE : # left
                engines.on(SpeedPercent(-backward_turn_speed_percent), SpeedPercent(forward_turn_speed_percent))

            elif left != ColorSensor.COLOR_BLACK and right != ColorSensor.COLOR_BLACK: # straight
                engines.on(SpeedPercent(base_speed_percent), SpeedPercent(base_speed_percent))

            elif left == right: # same
                engines.on(SpeedPercent(base_speed_percent), SpeedPercent(base_speed_percent))

        engines.off()
        print("Heisenbot stopped")

    try:
        while(True):
            print("Press to start Heisenbot")
            switch.wait_for_bump()
            go()
            motor.off()
            sleep(1)

    except KeyboardInterrupt:
        print("Heisenbot stopped")
        engines.off()
        sys.exit()


if __name__ == "__main__":
    main()
