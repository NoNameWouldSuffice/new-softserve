import softserve
import time

#Uses a potentiometer to control an RGB led
#If the signal from the pot is less than 10, the led is red
#If the signal from the pot is greater than 90, the led is green
#If the signal is between 10 and 90, the led is blue

jb1 = softserve.Jackbord("red.head", "111254186336836811343", "1fa60c9fc6")


total_leds = 4


jb1.cmd("gvr b1")
jb1.cmd("sledn {0}".format(total_leds))

potReading = jb1.bindchan(6)

print("Starting while True loop. Press Ctrl-C to forgive bad design and close program")

#Channel varaibles are always null until they get a new value from mqtt

loopCounter = 0
while True:
    try:
        loopCounter += 1
        print("Getting reading number {}".format(loopCounter))
        print(potReading.get())
        #IMPORTANT: Filter out the value "Null" for when the channel is first bound and still has it's default value
        if potReading.get() != "Null":
            potReadingFloat = float(potReading.get()) #If the channel is null, then the string "Null" is passed to the float casting and throws an error
            
            if potReadingFloat > 90:
                jb1.cmd("sled 1 255 0 0")

            
            elif potReadingFloat < 10:
                blue = 0
                jb1.cmd("sled 1 0 255 0")
            else:
                jb1.cmd("sled 1 0 0 255")
            
        time.sleep(0.1)
    except KeyboardInterrupt:
        print("sending led turn off")
        jb1.cmd("sledoff")
        break