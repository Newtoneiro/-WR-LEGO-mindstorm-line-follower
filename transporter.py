#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent, MoveTank, Motor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, InfraredSensor
from ev3dev2.sound import Sound
from time import sleep
import sys

# states
FIND_FROM = 0
GO_TO_PACKAGE = 1
LIFT = 2
BACK_TO_TRACK = 3
FIND_TO = 4
GO_TO_TARGET_SPOT = 5
LOWER = 6
END = 99
# output
engines = MoveTank(OUTPUT_D, OUTPUT_A)
switch = TouchSensor(INPUT_2)
motor = Motor(OUTPUT_B)
# input
left_sensor = ColorSensor(INPUT_1)
left_sensor.mode = left_sensor.MODE_COL_COLOR
right_sensor = ColorSensor(INPUT_4)
right_sensor.mode = right_sensor.MODE_COL_COLOR
proximity_sensor = InfraredSensor(INPUT_3)
proximity_sensor.mode = proximity_sensor.MODE_IR_PROX
# console input
base_speed_percent = int(sys.argv[1])
forward_turn_speed_percent = int(sys.argv[2])
backward_turn_speed_percent = int(sys.argv[3])
rotations = int(sys.argv[4])
rotation_speed_percent = int(sys.argv[5])
FROM = int(sys.argv[6])
TO = int(sys.argv[7])
turn_90_sleep_time = 2
turn_180_sleep_time = 4.4
turn_90_speed_percent = int(sys.argv[8])
proximity_threshold = float(sys.argv[9])

spkr = Sound()

def main():
    def go(follow_colors: list, stop):
        left, right, proximity = read_sensors()
        while not stop(left, right, proximity) and not switch.is_pressed:
            if left == ColorSensor.COLOR_NOCOLOR or right == ColorSensor.COLOR_NOCOLOR:
                engines.off()

            elif left == ColorSensor.COLOR_WHITE and right in follow_colors : # right
                engines.on(SpeedPercent(forward_turn_speed_percent), SpeedPercent(-backward_turn_speed_percent))

            elif left in follow_colors and right == ColorSensor.COLOR_WHITE : # left
                engines.on(SpeedPercent(-backward_turn_speed_percent), SpeedPercent(forward_turn_speed_percent))

            elif left not in follow_colors and right not in follow_colors: # straight
                engines.on(SpeedPercent(base_speed_percent), SpeedPercent(base_speed_percent))

            elif left == right: # same
                engines.on(SpeedPercent(base_speed_percent), SpeedPercent(base_speed_percent))

            left, right, proximity = read_sensors()

        engines.off()
        return left, right, proximity

    def read_sensors():
        left = left_sensor.color
        right = right_sensor.color
        proximity = proximity_sensor.proximity
        return left,right,proximity
    
    def lower():
        motor.on_for_rotations(SpeedPercent(rotation_speed_percent), rotations) # opuszcza

    def lift():
        motor.on_for_rotations(SpeedPercent(-rotation_speed_percent), rotations) # podnosi

    try:
        CURRENT_STATE = FIND_FROM
        from_90_on_left = False
        to_90_on_left = False
        while(CURRENT_STATE != END and not switch.is_pressed):
            if CURRENT_STATE == FIND_FROM:
                l, r, _ = go([ColorSensor.COLOR_BLACK], lambda left, right, p: left == FROM or right == FROM )

                if l == FROM:
                    engines.on(SpeedPercent(-turn_90_speed_percent), SpeedPercent(turn_90_speed_percent + 5))
                    from_90_on_left = True
                elif r == FROM:
                    engines.on(SpeedPercent(turn_90_speed_percent + 5), SpeedPercent(-turn_90_speed_percent))
                    from_90_on_left = False

                sleep(turn_90_sleep_time)
                engines.off()
                CURRENT_STATE = GO_TO_PACKAGE

            elif CURRENT_STATE == GO_TO_PACKAGE:
                go([ColorSensor.COLOR_BLACK, FROM], lambda l, r, proximity: proximity <= proximity_threshold)
                CURRENT_STATE = LIFT

            elif CURRENT_STATE == LIFT:
                lift()
                engines.on(SpeedPercent(-turn_90_speed_percent), SpeedPercent(turn_90_speed_percent))
                sleep(turn_180_sleep_time)
                engines.off()
                # zjazd z zielonego pola
                go([ColorSensor.COLOR_BLACK], lambda left, right, p: left != FROM or right != FROM)
                CURRENT_STATE = BACK_TO_TRACK

            elif CURRENT_STATE == BACK_TO_TRACK:
                l, r, p = go([ColorSensor.COLOR_BLACK], lambda left, right, p:
                             left in [ColorSensor.COLOR_BLACK, FROM] and right in [ColorSensor.COLOR_BLACK, FROM] )
                
                if from_90_on_left:
                    engines.on(SpeedPercent(-turn_90_speed_percent), SpeedPercent(turn_90_speed_percent + 5))
                else:
                    engines.on(SpeedPercent(turn_90_speed_percent + 5), SpeedPercent(-turn_90_speed_percent))

                sleep(turn_90_sleep_time)
                engines.off()
                CURRENT_STATE = FIND_TO

            elif CURRENT_STATE == FIND_TO:
                l, r, _ = go([ColorSensor.COLOR_BLACK], lambda left, right, p: left == TO or right == TO )

                if l == TO:
                    engines.on(SpeedPercent(-turn_90_speed_percent), SpeedPercent(turn_90_speed_percent + 5))
                    to_90_on_left = True
                elif r == TO:
                    engines.on(SpeedPercent(turn_90_speed_percent + 5), SpeedPercent(-turn_90_speed_percent))
                    to_90_on_left = False

                sleep(turn_90_sleep_time)
                engines.off()
                CURRENT_STATE = GO_TO_TARGET_SPOT

            elif CURRENT_STATE == GO_TO_TARGET_SPOT:
                go([ColorSensor.COLOR_BLACK, FROM], lambda left, right, p: left == TO and right == TO)
                CURRENT_STATE = LOWER

            elif CURRENT_STATE == LOWER:
                lower()
                spkr.speak('Yejiemy Panovyeee')
                CURRENT_STATE = END

    except KeyboardInterrupt:
        print("Artur stopped")
        engines.off()
        motor.off()
        sys.exit()


if __name__ == "__main__":
    while(True):
        print("Press to start Artur")
        switch.wait_for_bump()
        spkr.speak('Yejiemy Panovieee')
        main()
        sleep(1)
        switch.wait_for_bump()

# z zielonego na czerwony
# python3 artur.py 15 70 65 2 50 3 5 15 1