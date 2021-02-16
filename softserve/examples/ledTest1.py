import time
import softserve

#####
# The aim of this example is to give general use cases for the command and channel feature of the softserve library.
# This example involves controlling the RGB user led in the Jackbord with a button to select a color and a pot to change the intensity of that color

# This example requires a push-button connected to pin A1 and a potentiometer / variable resistor connected to pin B1 of the Jackbord.
# This example also requires both the jackbord and the computer running it to both be connected to the internet.


#Initialise a connection with the jackbord with a profileID of 101a
jb1 = softserve.Jackbord("profile-id-here")

#Initialise button on a1
jb1.cmd("btg a1")

#Initialise pot on b1 with range of 0-255 for color selection
jb1.cmd("gvr b1 0 255")
jb1.cmd("setuct b1 1.1")
print(jb1.donePublishing())

#Set up channel objects to record the readings for the button on pin a1 and the potentiometer on pin b1 respectively
#The channel objects button and pot are what we will use to retrieve the latest readings from the jackbord
button = jb1.bindchan("a1")
pot = jb1.bindchan("b1")


#Variables to keep track of the red, green and blue intensities and a variable to keep track of the color being modifies
red = 0
green = 0
blue = 0
color = "red"

#Variables to keep track of the previous reading from the potentiometer and button
#This is important because we want this program to act on changes in the readings, i.e. we want to switch color when the button has just been pushed
#And when the pot reading has just been changed
oldButtonReading = False
oldPotReading = 0



#A funtion to return the next color when the button has been pressed given the previous color
def switchColors(oldColor):
    if oldColor == "red":
        return "green"
    if oldColor == "green":
        return "blue"
    if oldColor == "blue":
        return "red"

print("Program ready. Push the button to switch color being adjusted, twist dial to change the intensity of that color")


while True:
    try:
        #Fetch the latest reading from the button and potentiometer and return them as usable data types
        buttonReading = bool(float(button.get()))
        potReading = round(float(pot.get()))

        # print("Button: {0}".format(buttonReading))
        # print("Pot: {0}".format(potReading))
        
        if (buttonReading and buttonReading != oldButtonReading):
            color = switchColors(color)
        
        if (potReading != oldPotReading):
            if (color == "red"):
                red = potReading
            if (color == "green"):
                green = potReading
            if (color == "blue"):
                blue = potReading
        
        if (buttonReading and buttonReading != oldButtonReading) or (potReading != oldPotReading):
            print("\n\n")
            print("Current color is {0}, {1}, {2}".format(red, green, blue))
            print("Color being changed: {0}, current intensity: {1}".format(color, potReading))
            print("\nPress Ctrl-C to quit")
        
        
        
        
        oldButtonReading = buttonReading
        oldPotReading = potReading
        jb1.cmd("suled 1 {0} {1} {2}".format(red, green, blue))    
        time.sleep(0.01)
    except KeyboardInterrupt:
        jb1.cmd("suled 1 0 0 0")
        print("\nThanks you and goodbye")
        break
