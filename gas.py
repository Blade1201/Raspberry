from mq import *
import RPi.GPIO as GPIO
import sys, time
mq = MQ();

buzzer = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, GPIO.LOW)
p = GPIO.PWM(buzzer, 1000)
p.ChangeDutyCycle(1)


channel = 21                   # DO láb GPIO 21, + 5V , GND pedig GND
GPIO.setup(channel, GPIO.IN)


def callback(channel):
    print("\nTűz észlelve!")
   
        
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)
    
    
while True:
    perc = mq.MQPercentage()     # Segitség: https://tutorials-raspberrypi.com/configure-and-read-out-the-raspberry-pi-gas-sensor-mq-x/
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    sys.stdout.write("LPG: %g ppm, CO: %g ppm, Füst: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
     
    
    if perc["CO"] > 1:
        GPIO.output(buzzer, GPIO.HIGH)
        p.start(1)
        
    else:
        p.stop()
        GPIO.output(buzzer, GPIO.LOW)
        
    sys.stdout.flush()
    time.sleep(0.1)
    



import MySQLdb  # MySQL használata MySQLdb könyvtár használatával
                # Opció 2 -- pymysql könyvtár használata

# Kapcsolat teremtés a connect metódus segitségével
db = MySQLdb.connect("localhost","felhasznalo","jelszo","adatbazis")

# db objektum létrehozása a cursor() MySQLdb metódusa segitségével
cursor = db.cursor()

# SQL parancs végrehajtása az execute() metódus segitségével
cursor.execute("""INSERT INTO gases (LPG, CO, Füst) VALUES (%s, %s, %s) """,( perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
db.commit()
 
time.sleep(60)



CREATE TABLE `gases` (
`LPG` FLOAT NULL DEFAULT NULL,
`CO` FLOAT NULL DEFAULT NULL,
`Füst` FLOAT NULL DEFAULT NULL,
`Időpont` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
COLLATE='utf8_hungarian_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
;



# Grafana -- grafikon lekérdezések

SELECT Füst as value, "Füst" as metric, UNIX_TIMESTAMP(Időpont) as time_sec FROM gases WHERE $__timeFilter(Időpont) order by time_sec asc

SELECT LPG as value, "LPG" as metric, UNIX_TIMESTAMP(Időpont) as time_sec FROM gases WHERE $__timeFilter(Időpont) order by time_sec asc

SELECT CO as value, "CO" as metric, UNIX_TIMESTAMP(Időpont) as time_sec FROM gases WHERE $__timeFilter(Időpont) order by time_sec asc