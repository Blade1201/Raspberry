from time import sleep
import time
import socket
import Adafruit_PCA9685
import threading
import RPi.GPIO as GPIO
import os

listensocket = socket.socket()
PORT = 21567
IP = socket.gethostname()
maxConnections = 1
listensocket.bind(('',PORT))
listensocket.listen(maxConnections)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.setup(16, GPIO.OUT)


print("elindult")

CMD =["U","d","G","g","A","a","B","b","R","r","E","e","S","L","l"]




pwm = Adafruit_PCA9685.PCA9685()
servo_min = 100  
servo_max = 600  
servo_mid = 350

def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

                  

    pulse_length //= 4096     
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)


pwm.set_pwm_freq(60)
      


def garazs_ajto_be():
    pwm.set_pwm(1, 0, servo_min)
    sleep(0.2)
    pwm.set_pwm(1, 0, 0)
def garazs_ajto_ki():
    pwm.set_pwm(1, 0, servo_max)
    sleep(0.2)
    pwm.set_pwm(1, 0, 0)
def ajto_be():
    pwm.set_pwm(0, 0, servo_min)
def ajto_ki():
    pwm.set_pwm(0, 0, servo_max)
def ablak_le():
    pwm.set_pwm(2, 0, servo_min)
def ablak_fel():
    pwm.set_pwm(2, 0, servo_mid)
def ablak_le_b():
    pwm.set_pwm(3, 0, servo_min)
def ablak_fel_b():
    pwm.set_pwm(3, 0, servo_max)
def redony_le():
    pwm.set_pwm(4, 0, servo_min)
    sleep(0.2)
    pwm.set_pwm(4, 0, 0)
def redony_fel():
    pwm.set_pwm(4, 0, servo_max)
    sleep(0.2)
    pwm.set_pwm(4, 0, 0)
def redony_le_b():
    pwm.set_pwm(5, 0, servo_min)
    sleep(0.2)
    pwm.set_pwm(5, 0, 0)
def redony_fel_b():
    pwm.set_pwm(5, 0, servo_max)
    sleep(0.2)
    pwm.set_pwm(5, 0, 0)
def rain_drop():
    try:
        while True:
            if (GPIO.input(17) == 0):
                sleep(0.1)
                pwm.set_pwm(0, 0, servo_min)
                pwm.set_pwm(2, 0, servo_min)
                print ("eso")

    except KeyboardInterrupt:
        print ("hiba az eso erzekeloben")
        GPIO.cleanup()
            
def vezerlo():
    while True:
        print('Waiting for connection.')
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
                    print("Redöny(J) fel")
                if data == CMD[9]:
                    redony_le()
                    print("Redöny(J) le")
                if data == CMD[10]:
                    redony_fel_b()
                    print("Redöny(B) fel")
                if data == CMD[11]:
                    redony_le_b()
                    print("Redöny(B) le")
                if data == CMD[12]:
                    print("STOP")
                if data == CMD[13]:
                    GPIO.output(16,GPIO.LOW)
                    print("Led be")
                if data == CMD[14]:
                    GPIO.output(16,GPIO.HIGH)
                    print("Led ki")    
        except KeyboardInterrupt:
            print("except")
    clientsocket.close();

t2 = threading.Thread(target = vezerlo)
t3 = threading.Thread(target = rain_drop)


t3.start()
t2.start()