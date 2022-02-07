from mq import *
import sys, time

try:
    print("Nyomj CTRL+C a megszakitáshoz.")
    
    mq = MQ();
    while True:
        perc = mq.MQPercentage()     # Segitség: https://tutorials-raspberrypi.com/configure-and-read-out-the-raspberry-pi-gas-sensor-mq-x/
        sys.stdout.write("\r")
        sys.stdout.write("\033[K")
        sys.stdout.write("LPG: %g ppm, CO: %g ppm, Füst: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
        sys.stdout.flush()
        time.sleep(0.1)

except:
    print("\nMegszakitva")