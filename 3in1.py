from mq import *
import RPi.GPIO as GPIO
import adafruit_dht
import sys,time
import threading
import board
import socket
import os
import Adafruit_PCA9685
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

sensor = adafruit_dht.DHT11(board.D23)
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
            print("\nHőmérséklet: {}*C   Páratartalom: {}% ".format(temp, humidity))
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
        print("\nSikertelen Adatbázis mentés...")
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
        print("\nSikertelen Adatbázis mentés...")
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
            time.sleep(10)

        else:
            p.stop()
            GPIO.output(buzzer, GPIO.LOW)

        sys.stdout.flush()
         
         

schedule.every(15).seconds.do(database_gas)
schedule.every(10).seconds.do(database_temp)
schedule.every(5).seconds.do(gas_print)



listensocket = socket.socket()
PORT = 21567
IP = socket.gethostname()
maxConnections = 1
listensocket.bind(('',PORT))
listensocket.listen(maxConnections)

GPIO.setwarnings(False)
GPIO.setup(17, GPIO.IN)
GPIO.setup(16, GPIO.OUT)

print("Elindult!")

CMD =["U","d","G","g","A","a","B","b","R","r","E","e","S","L","l"]




pwm = Adafruit_PCA9685.PCA9685()
servo_min = 150
servo_max = 600
servo_mid = 390



pwm.set_pwm_freq(60)


def garazs_ajto_be():
    pwm.set_pwm(1, 0, servo_max)
    time.sleep(0.8)
    pwm.set_pwm(1, 0, 0)


def garazs_ajto_ki():
    pwm.set_pwm(1, 0, servo_min)
    time.sleep(0.7)
    pwm.set_pwm(1, 0, 0)


def ajto_be():
    pwm.set_pwm(0, 0, servo_min)

def ajto_ki():
    pwm.set_pwm(0, 0, servo_mid)


def ablak_le():
    pwm.set_pwm(2, 0, servo_max)


def ablak_fel():
    pwm.set_pwm(2, 0, servo_mid)


def ablak_le_b():
    pwm.set_pwm(15, 0, servo_mid)


def ablak_fel_b():
    pwm.set_pwm(15, 0, servo_max)


def redony_le():
    pwm.set_pwm(4, 0, servo_min)
    time.sleep(0.2)
    pwm.set_pwm(4, 0, 0)


def redony_fel():
    pwm.set_pwm(4, 0, servo_max)
    time.sleep(0.2)
    pwm.set_pwm(4, 0, 0)


def redony_le_b():
    pwm.set_pwm(5, 0, servo_min)
    time.sleep(0.2)
    pwm.set_pwm(5, 0, 0)


def redony_fel_b():
    pwm.set_pwm(5, 0, servo_max)
    time.sleep(0.2)
    pwm.set_pwm(5, 0, 0)


def rain_drop():
    try:
        while True:
            if (GPIO.input(17) == 0):
                pwm.set_pwm(1, 0, servo_min)
                time.sleep(0.6)
                pwm.set_pwm(1, 0, 0)
                print("\nESŐ")

    except KeyboardInterrupt:
        print("\nHiba az ESŐ érzékelőben!")
        GPIO.cleanup()


def vezerlo():
    while True:
        clientsocket, address = listensocket.accept()
        try:
            while True:
                data = clientsocket.recv(1024).decode()
                if not data:
                    break
                if data == CMD[0]:
                    ajto_be()
                    print("Ajtó be")
                if data == CMD[1]:
                    ajto_ki()
                    print("Ajtó ki")
                if data == CMD[2]:
                    garazs_ajto_be()
                    print("Garázskapú fel")
                if data == CMD[3]:
                    garazs_ajto_ki()
                    print("Garázskapú le")
                if data == CMD[4]:
                    ablak_le()
                    print("Ablak(J) ki")
                if data == CMD[5]:
                    ablak_fel()
                    print("Ablak(J) be")
                if data == CMD[6]:
                    ablak_fel_b()
                    print("Ablak(B) ki")
                if data == CMD[7]:
                    ablak_le_b()
                    print("Ablak(B) be")
                if data == CMD[8]:
                    redony_fel()
                    print("Redőny(J) fel")
                if data == CMD[9]:
                    redony_le()
                    print("Redőny(J) le")
                if data == CMD[10]:
                    redony_fel_b()
                    print("Redőny(B) fel")
                if data == CMD[11]:
                    redony_le_b()
                    print("Redőny(B) le")
                if data == CMD[12]:
                    print("STOP")
                if data == CMD[13]:
                    GPIO.output(16, GPIO.HIGH)
                    print("Led be")
                if data == CMD[14]:
                    GPIO.output(16, GPIO.LOW)
                    print("Led ki")
        except KeyboardInterrupt:
            print("Kivétel")
            clientsocket.close()

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

continueSchedule = threading.Thread(target=continuous)
continueSchedule.start()

androidApplication = threading.Thread(target=vezerlo)
androidApplication.start()

rainSensor = threading.Thread(target=rain_drop)
rainSensor.start()