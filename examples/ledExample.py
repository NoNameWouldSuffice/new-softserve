import softserve
import time

#This example requires a button connected to the Jackbord on pin A3

jb1 = softserve.Jackbord("10gp")

#Initialise button on a3
jb1.cmd("btg a3")

#Bind a CHANNEL object called button to pin a1 so we can access the button on the jackbord
button = jb1.bindchan("a3")

#Do this indefinately until someone kills the python script
while True:
    #Print current value of button
    print(button.get())

    #Check if pin a3 is HIGH (=1.00)
    if button.get() == "1.00":
        #If button is pressed, turn user light red
        jb1.cmd("suled 1 255 0 0")
    
    else:
        #If button is not pressed, turn user light off
        jb1.cmd("suled 1 0 0 0")
    
    #Delay to space out the commands
    time.sleep(0.05)
