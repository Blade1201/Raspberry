import RPi.GPIO as GPIO
from time import sleep
def main():
	reed = 24     # Segitség: https://www.instructables.com/RaspberryPi-3-Magnet-Sensor-With-Mini-Reed-Sensor/
	buzzer = 25 # + vége megy a GPIO 25-be - vége a Ground-ba
	led = 26  # Led hoszabbik lába 330k ohm ellenállás segitségével(vagyis a led lehet bárhol)
	          # megy a GPIO 26-ba,rövid lába pedig a Ground-ba
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(reed, GPIO.IN)
	GPIO.setup(led, GPIO.OUT)
	GPIO.setup(buzzer, GPIO.OUT)
	GPIO.output(buzzer, GPIO.LOW)
	p = GPIO.PWM(buzzer, 1000)
	p.ChangeDutyCycle(1)
	count = 0
	while True:
		val = GPIO.input(reed)
		if not(val):
			GPIO.output(led, GPIO.HIGH)
			GPIO.output(buzzer, GPIO.HIGH)
			p.start(1)
			print("Érzékelő zárolva!")
		else:
			p.stop()
			GPIO.output(led, GPIO.LOW)
			GPIO.output(buzzer, GPIO.LOW)
		sleep(.75)
	GPIO.cleanup()
GPIO.setwarnings(False)
main()