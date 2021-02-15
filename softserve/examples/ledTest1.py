import time
import softserve

jb1 = softserve.Jackbord("101a")

#Initialise button on a1

jb1.cmd("btg a1")

#Initialise pot on b1 with range of 0-255 for color selection
jb1.cmd("gvr b1 0 255")

#Bind a variable to that channel on the jackbord
button = jb1.bindchan("a1")
pot = jb1.bindchan("b1")


red = 0
green = 0
blue = 0
color = "red"

oldButtonReading = True
oldPotReading = 0

def switchColors(oldColor):
    if oldColor == "red":
        return "green"
    if oldColor == "green":
        return "blue"
    if oldColor == "blue":
        return "red"


while True:
    try:
        buttonReading = bool(float(button.get()))
        potReading = round(float(pot.get()))

        # print("Button: {0}".format(buttonReading))
        # print("Pot: {0}".format(potReading))
        
        if (buttonReading and buttonReading != oldButtonReading):
            color = switchColors(color)
            print("Color is now: " + color)
        
        if (potReading != oldPotReading):
            if (color == "red"):
                red = potReading
            if (color == "green"):
                green = potReading
            if (color == "blue"):
                blue = potReading
        
        
        
        
        oldButtonReading = buttonReading
        oldPotReading = potReading
        jb1.cmd("suled 1 {0} {1} {2}".format(red, green, blue))    
        time.sleep(0.01)
    except KeyboardInterrupt:
        jb1.cmd("suled 1 0 0 0")
        break
