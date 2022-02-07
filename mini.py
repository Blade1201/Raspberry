# Needed modules will be imported and configured 
import RPi.GPIO as GPIO
import time
  
GPIO.setmode(GPIO.BCM)
  
# The input pin which is connected with the sensor
GPIO_PIN = 24
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
  
print ("KY-021 Érzékelő Teszt [Nyomj Ctrl+C a befejezéshez]")
  
def outputFunction(null):
        print("Érzékelő zárolva")
  
# signal detection (raising edge).
GPIO.add_event_detect(GPIO_PIN, GPIO.RISING, callback=outputFunction, bouncetime=100) 
  
# Main program loop
try:
        while True:
                time.sleep(1)
  
# Scavenging work after the end of the program
except KeyboardInterrupt:
        GPIO.cleanup()