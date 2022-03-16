from mq import *
import RPi.GPIO as GPIO
import adafruit_dht
import sys,time
import threading
import board
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess
import psutil
import requests
import schedule
from pushbullet import Pushbullet
import pymysql
from config import host,user,password,db_name


for proc in psutil.process_iter():
    if proc.name()=='libgpiod_pulsein' or proc.name() =='lipgpiod_pulsei':
        proc.kill()

mq = MQ()

sensor = adafruit_dht.DHT11(23)
led = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(led, GPIO.OUT)

i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

disp.fill(0)
disp.show()

width = disp.width
height = disp.height
image = Image.new("1", (width, height))

draw = ImageDraw.Draw(image)

draw.rectangle((0, 0, width, height), outline=0, fill=0)

padding = -2
top = padding
bottom = height - padding
x = 0

font = ImageFont.load_default()

def tempandhumidity():
    
    while True:
        try:
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            temp = sensor.temperature
            humidity = sensor.humidity
            print("\n Hőmérséklet: {}*C Páratartalom: {}% ".format(temp, humidity))
            draw.text((x+30, top+5), str(temp)+' *C',  font=font, fill=255)
            draw.text((x+55, top+15), str(humidity)+' %', font=font, fill=255)
            draw.text((x, top+5), 'Ho: ',  font=font, fill=255)
            draw.text((x, top+15), 'Para: ',  font=font, fill=255)
            disp.image(image)
            disp.show()
            time.sleep(0.1)

            
            
            if temp>=28:
                print("\nKlima Bekapcsolva")
                GPIO.output(led, True)
            if temp<=20:
                print("\nFűtés Bekapcsolva")
                GPIO.output(led, False)
                
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2)
            continue
        
        except Exception as error:
            sensor.exit()
            raise error
        
        time.sleep(1)
    
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


def lightsensor():
    
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



buzzer = 25

GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, GPIO.LOW)
p = GPIO.PWM(buzzer, 1000)
p.ChangeDutyCycle(1)


pb = Pushbullet("o.Fn1WBnZneP9sUEVQCP9WAJs7sAzvZcIw")
dev=pb.get_device("Samsung SM-A600FN")


def database_gas():
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
        #        create_table_query = "CREATE TABLE `Gáz Szint` (`LPG` float DEFAULT NULL," \
        #                         "`CO` float DEFAULT NULL," \
        #                         "`Füst` float DEFAULT NULL," \
        #                         "`Időpont` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp())"

        #        cursor.execute(create_table_query)
        #        print("Tábla sikeresen létrehozva")

        # Adat behelyezése
            with connection.cursor() as cursor:
                perc = mq.MQPercentage()
                insert_query = """INSERT INTO `Gáz Szint` (LPG, CO, Füst) VALUES (%s, %s, %s)""" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"])
                cursor.execute(insert_query)
                connection.commit()
                
        finally:
            connection.close()
    except Exception as ex:
        print("Sikertelen Adatbázis mentés...")
        print("Kapcsolat megszakadt...")
        print(ex)


def database_temp():
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
            #        create_table_query = "CREATE TABLE `Hőmérséklet és Páratartalom` (`Hőmérséklet` int(2) DEFAULT NULL," \
            #                         "`Páratartalom` int(2) DEFAULT NULL," \
            #                         "`Időpont` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp())"

            #        cursor.execute(create_table_query)
            #        print("Tábla sikeresen létrehozva")

            # Adat behelyezése
            with connection.cursor() as cursor:
                temp = sensor.temperature
                humidity = sensor.humidity
                insert_query = """INSERT INTO `Hőmérséklet és Páratartalom` (Hőmérséklet, Páratartalom) VALUES (%s, %s)""" % (
                temp,humidity)
                cursor.execute(insert_query)
                connection.commit()

        finally:
            connection.close()
    except Exception as ex:
        print("Sikertelen Adatbázis mentés...")
        print("Kapcsolat megszakadt...")
        print(ex)



def gas_print():
    perc = mq.MQPercentage()
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    sys.stdout.write("LPG: %g ppm, CO: %g ppm, Füst: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
    
    
def gas():
    while True:
        perc = mq.MQPercentage()
        gas_print()
         
        if perc["CO"] > 1:
             
            GPIO.output(buzzer, GPIO.HIGH)
            p.start(1)
            push = dev.push_note("Figyelem!!!", "Megemelkedett gázszint észlelve!")
            time.sleep(10)

        else:
            p.stop()
            GPIO.output(buzzer, GPIO.LOW)

        sys.stdout.flush()
         
         

schedule.every(15).seconds.do(database_gas)
schedule.every(10).seconds.do(database_temp)
schedule.every(5).seconds.do(gas_print)
         
         
flame_sensor = 20    # DC láb a 20-as láb-ba, + láb az 5V-ba, Gnd a Gnd-ba -- Az AO láb nem kell!!!
GPIO.setup(flame_sensor, GPIO.IN)


buzzer2 = 6

GPIO.setup(buzzer2, GPIO.OUT)
GPIO.output(buzzer2, GPIO.LOW)
o = GPIO.PWM(buzzer2, 1000)
o.ChangeDutyCycle(1)


def flame():
    while True:
        if GPIO.input(20) == True:
            push = dev.push_note("Figyelem!!!", "Tűz észlelve!")
            GPIO.output(buzzer2, GPIO.HIGH)
            o.start(1)
            time.sleep(3)
        else:
            o.stop()
            GPIO.output(buzzer2, GPIO.LOW)


def continuous():
    while True:
        schedule.run_pending()
        time.sleep(1)


temperature = threading.Thread(target=tempandhumidity)
temperature.start()

light = threading.Thread(target=lightsensor)
light.start()

gasSensor = threading.Thread(target=gas)
gasSensor.start()

flameSensor = threading.Thread(target=flame)
flameSensor.start()

continueSchedule = threading.Thread(target=continuous)
continueSchedule.start()