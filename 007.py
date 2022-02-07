import RPi.GPIO as GPIO
import adafruit_dht
import time
import threading
import psutil

for proc in psutil.process_iter():
    if proc.name()=='libgpiod_pulsein' or proc.name() =='lipgpiod_pulsei':
        proc.kill()

sensor = adafruit_dht.DHT11(23)
led = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(led, GPIO.OUT)

def tempandhumidity():
    
    while True:
        try:
            temp = sensor.temperature
            humidity = sensor.humidity
            print("Hőmérséklet: {}*C Páratartalom: {}% ".format(temp, humidity))
            
            if temp>=28:
                print("Bekapcsolva")
                GPIO.output(led, True)
            if temp<=20:
                print("Kikapcsolva")
                GPIO.output(led, False)
                
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            continue
        
        except Exception as error:
            sensor.exit()
            raise error
        
        time.sleep(2.0)
    
value = 0
ldr = 4   #Középső a 3v3
led1 = 21
GPIO.setup(led1,GPIO.OUT)

def rc_time(ldr):
    
    count = 0
    
    GPIO.setup(ldr,GPIO.OUT)
    GPIO.output(ldr, False)  
    GPIO.setup(ldr, GPIO.IN)
    
    while(GPIO.input(ldr) ==0):
        count +=1
        
    return count
def lightfilter():
    
    try:
        while True:
            value = rc_time(ldr)
            if(value<1):
                pass
                GPIO.output(led1, True)
            if(value >1):
                pass
                GPIO.output(led1, False)
        
    except KeyboardInterrupt:
        pass
    
    finally:
        GPIO.cleanup()

temperature = threading.Thread(target = tempandhumidity)
temperature.start()

lightdepartment = threading.Thread(target = lightfilter)
lightdepartment.start()