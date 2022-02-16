import math
import softserve
import time

#This example requires a button connected to the Jackbord on pin A3

jb1 = softserve.Jackbord("personality-id-goes-here")

#Initialise button on a3
jb1.cmd("btg a3")

#Bind a CHANNEL object called button to pin a1 so we can access the button on the jackbord
button = jb1.bindchan("a3")


i = 0
while True:
    #Cycle between blue and red
    r = int(127 + 127 * math.sin(i)) #Returns a value for red between 0 and 254
    b = 254 - r

    #Print current button reading from pin a3
    print(button.get())

    #Check if button on a3 is pushed
    if button.get() == "1.00":
        #Update the color of the user led
        jb1.cmd("suled 1 {0} 0 {1}".format(r, b))
    
    else:
        #If button is not pressed, turn the user led off
        jb1.cmd("suled 1 0 0 0")
    
    i += .2
    time.sleep(0.05)
