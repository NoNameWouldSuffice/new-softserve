from softservetbn import *
import time

#Uses a potentiometer to control an RGB led
#If the signal from the pot is less than 10, the led is red
#If the signal from the pot is greater than 90, the led is green
#If the signal is between 10 and 90, the led is blue

jb1 = Jackbord("red.head", "111254186336836811343", "1fa60c9fc6")


pin_no = "a2"


jb1.cmd("gvr b1")

potReading = jb1.bindChan(6) #Edit softserve to accept the letter/number pins

print("Starting while True loop. Press Ctrl-C to forgive bad design and close program")

#Channel varaibles are always null until they get a new value from mqtt
#Maybe have something where it attempts to grab the latest value of the specified channel from mqtt using a gt command?

loopCounter = 0
while True:
    try:
        loopCounter += 1
        print("Getting reading number {}".format(loopCounter))
        print(potReading.get())
        if potReading.get() != "Null":
            potReadingFloat = float(potReading.get()) #If the channel is null, then the string "Null" is passed to the float casting and throws an error
            #note: avoid sending updates that dont need to happen
            
            if potReadingFloat > 90:
                #jb1.cmd("sled {0} {1} {2} {3} {4} {5}".format(pin_no, total_leds, led_no, red, green, blue))
                jb1.cmd("sled {0} {1} {2} {3} {4} {5}".format(pin_no, 1, 0, 255, 0, 0))

            
            elif potReadingFloat < 10:
                blue = 0
                jb1.cmd("sled {0} 1 0 0 255 0".format(pin_no))
            else:
                jb1.cmd("sled {0} 1 0 0 0 255".format(pin_no))
            
        time.sleep(0.1)
    except KeyboardInterrupt:
        jb1.cmd("sled {0} {1} {2} {3} {4} {5}".format(pin_no, 1, 0, 0, 0, 0))
        break