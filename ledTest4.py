from softservetbn import *
from random import randint
import time

#Cylces through each of the 4 leds and gives it a random color
#The potentiometer controls the speed at which the program cycles through the leds

jb1 = Jackbord("red.head", "111254186336836811343", "1fa60c9fc6")

total_leds = 4
pin_no = "a2"
led_no = 0
red = 0
green = 0
blue = 0

delay = 0

jb1.cmd("gvr b1")
potReading = jb1.bindChan(6)

print("Smart LED Program Started")
jb1.cmd("sled {0} {1} {2} {3} {4} {5}".format(pin_no, total_leds, led_no, red, green, blue))

while True:
    red = randint(0, 255)
    green = randint(0, 255)
    blue = randint(0, 255)



    

    if led_no >= total_leds:
        led_no = 0
    else:
        led_no += 1
    
    #Variables are difficult to put into python command.
    #They would need to be string formatted into the command
    jb1.cmd("sled {0} {1} {2} {3} {4} {5}".format(pin_no, total_leds, led_no, red, green, blue))

    if potReading.get() != "Null":
        delay = float(potReading.get())


    time.sleep(0.01 + (delay * 0.005))