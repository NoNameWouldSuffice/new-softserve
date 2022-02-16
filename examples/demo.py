import softserve

#All communication to a jackbord happens through a softserve Jackbord class. 
#You can control multiple Jackbords by making multiple Jackbord classes. 

#Create a Jackbord object named jb1. You need to provide the personality id of the Jackbord. 
#It is diffent to the 2 word ID (e.g. red.head, green.beard, etc.) used to create the personality.
#Find it by hovering over the 2 word id of a personality with your mouse on the dashboard
jb1 = softserve.Jackbord("personality-id-here")

#A Jackboard object has 5 important methods you can use to communicate with the Jackbord.

#Jackbord.cmd(): Sends a command to the jackbord. Command can be any octagon command from the dashboard.
#Receiving responses to commands from the Jackbord is not supported.

jb1.cmd("l1 1") #Turn on the user light on the Jackbord jb1.

jb1.cmd("add 5 6") #Does run this command on the Jackbord. Doesn't return the answer.

#Jackbord.bindchan(): Used to bind a channel / pin on the jackbord to a local CHANNEL object. 
#Jackbord.bindchan(): Creates a CHANNEL object tied to a channel / pin on the Jackbord.
#A CHANNEL object is kept up-to-date with the latest value of the channel / pin.

pin = jb1.bindchan("b1") #Creates a CHANNEL class tied to the b1 pin on the Jackbord

#The value stored in a CHANNEL object can be changed using it's .set() method. This will also update the value on the Jackbord

pin.set(1.00) #Sets the value of pin b1 to 1.00

#The value can be found using the CHANNEL object's .get() method. 
#This will return a 0 by default until the first change is made.

reading = pin.get() #Retrieve a reading from b1 and saves it as reading

#Jackbord.publish(): Used to publish a value to an mqtt topic on the Jackbord
jb1.publish("topic", "Value") #Publishes "Value" to the mqtt topic "topic"

#Jackbord.subscribe(): Used to subscribe to an MQTT topic on the Jackbord. 
#Returns a MQTOPIC object that works the same as CHANNEL in Jackbord.bindchan() 
#but is kept up to date with the value of the topic on the Jackbord.

topic = jb1.subscribe("topic")
topic.set("New Value") #Sets value of topic in topic object and topic on jackbord
topic.get() #Returns current value of topic

#Finally the Jackbord object has a live command mode that can be used in an interactive shell.
#This will also display responses / outputs from the jackbord as they arrive
#When a jackbord object has been created in the shell, run the command:
#  jb1.cmdlive().

