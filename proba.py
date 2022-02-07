from __future__ import division
import time
from adafruit_servokit import ServoKit 


servo_min = 150
servo_max = 600
servo_mid = 350

def set_servo_pulse(channel,pulse):
    pulse_lenght = 1000000
    pulse_lenght //= 60
    print('{0}us per period'.format(pulse_lenght))
    pulse_lenght //= 4096
    print('{0}us per bit'.format(pulse_lenght))
    pulse *= 1000
    pulse //= pulse_lenght
    pwm.set_pwm(channel,0,pulse)

pwm.set_pwm_freq(60)

print('Moving servo on channel 0,press Ctrl-C to Quit...')
while True:
    pwm.set_pwm(0,0,servo_min)
    time.sleep(1)
    pwm.set_pwm(0,0,servo_max)
    time.sleep(1)
    pwm.set_pwm(1,0,servo_min)
    time.sleep(1)
    pwm.set_pwm(1,0,servo_mid)
    time.sleep(1)