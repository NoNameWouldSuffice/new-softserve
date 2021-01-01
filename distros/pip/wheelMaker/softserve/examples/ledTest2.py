import softserve
import time

#Potentiometer working with the user light on port d1
#When the pot is above 90 - light goes on
#When the pot is below 10 - light goes off

jb1 = softserve.Jackbord("red.head", "111254186336836811343", "1fa60c9fc6")

jb1.cmd("gvr b1")

potReading = jb1.bindchan(6) #Edit softserve to accept the letter/number pins

print("Starting while True loop. Press Ctrl-C to forgive bad design and close program")

loopCounter = 0
while True:
    loopCounter += 1
    print("Getting reading number {}".format(loopCounter))
    print(potReading.get())
    if potReading.get() != "Null":
        potReadingFloat = float(potReading.get()) #If the channel is null, then the string "Null" is passed to the float casting and throws an error
        #note: avoid sending updates that dont need to happen
        
        if potReadingFloat > 90:
            jb1.cmd("d1 1")
        
        if potReadingFloat < 10:
            jb1.cmd("d1 0")
        
    time.sleep(0.1)
