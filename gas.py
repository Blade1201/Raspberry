from mq import *
import RPi.GPIO as GPIO
import sys, time
import requests
import schedule
from pushbullet import Pushbullet
mq = MQ();

buzzer = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, GPIO.LOW)
p = GPIO.PWM(buzzer, 1000)
p.ChangeDutyCycle(1)


pb = Pushbullet("o.dSkeB5qey7pKgy0LgfbovpEQE9uLTddl")
dev=pb.get_device("Samsung SM-A600FN")

def database():
    try:
        connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
        

        try:
        # Tábla létrehozása         # ---------------------- A Tábla létrehozása után be kell kommentelni ezt a részt
        #    with connection.cursor() as cursor:
        #        create_table_query = "CREATE TABLE `gases` (`LPG` float DEFAULT NULL," \
        #                         "`CO` float DEFAULT NULL," \
        #                         "`Füst` float DEFAULT NULL," \
        #                         "`Időpont` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp())"

        #        cursor.execute(create_table_query)
        #        print("Tábla sikeresen létrehozva")

        # Adat behelyezése
            with connection.cursor() as cursor:
                insert_query = """INSERT INTO `gases` (LPG, CO, Füst) VALUES (%s, %s, %s)""" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]);
                cursor.execute(insert_query)
                connection.commit()
                
        finally:
            connection.close()
    except Exception as ex:
        print("Kapcsolat megszakadt...")
        print(ex)

schedule.every(10).seconds.do(database)

import pymysql
from config import host,user,password,db_name


    
while True:
    perc = mq.MQPercentage()     # Segitség: https://tutorials-raspberrypi.com/configure-and-read-out-the-raspberry-pi-gas-sensor-mq-x/
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    sys.stdout.write("LPG: %g ppm, CO: %g ppm, Füst: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
    schedule.run_pending()
    
    if perc["CO"] > 1:
        GPIO.output(buzzer, GPIO.HIGH)
        p.start(1)
        push = dev.push_note("Figyelem!!!","Megemelkedett gázszint észlelve!")
        time.sleep(10)
        
    else:
        p.stop()
        GPIO.output(buzzer, GPIO.LOW)
        
    sys.stdout.flush()