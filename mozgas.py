import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

led1=17
led2=21
pirpin=19

GPIO.setup(led1,GPIO.OUT)
GPIO.setup(led2,GPIO.OUT)
GPIO.setup(pirpin,GPIO.IN)

def LIGHTS(pirpin):
	print("Mozgás észlelve!")
	print("Lámpa be")
	GPIO.output(led1,GPIO.HIGH)
	GPIO.output(led2,GPIO.HIGH)
	
	time.sleep(10)
	print("Lámpa ki")
	GPIO.output(led1,GPIO.LOW)
	GPIO.output(led2,GPIO.LOW)
print("A mozgás érzékelő indul...")
time.sleep(1)
print("Elindult")

try:
	GPIO.add_event_detect(pirpin, GPIO.RISING, callback=LIGHTS)
	while 1:
		time.sleep(1)
except KeyboardInterrupt:
	print("")
	print("A mozgás érzékelő kikapcsol...")
	GPIO.cleanup()
