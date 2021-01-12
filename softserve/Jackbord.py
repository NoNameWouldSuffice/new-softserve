import os
from softserve.channel import Channel
import time
import ssl

try:
    #We will attempt to load dependencies from the built-in deps module which will be present if this is a standalone copy of softserve
    import softserve.deps.paho.mqtt.client as mqtt

except ImportError:
    #We could not import the deps that will be here in the standalone version of softserve, try importing the deps as if they were installed along with
    #softserve using pip
    import paho.mqtt.client as mqtt


class Jackbord():
    def __init__(self, jackbordID, username, password):

        #List of bound variables / channel classes
        #Mqtt broker address
        #Mqtt broker port
        #Mqtt client instance

        #TEMPORARY: Retrieve the path of the softserve library (Or at least where the channel sub-module is) on the system
        self.__MODPATH = os.path.dirname(__file__)

        self.__channelClassList = {} #Format: "mqtt topic" : ChannelClass instance

        self.hostAddress = "mqttb.jackbord.org"

        self.__jackbordID = jackbordID

        self.hostPort = 8883

        self.__mqttClient = mqtt.Client()

        self.__openMqttServer(username, password)

        self.__inLiveMode = False
        self.__printOutput = ""

        self.__previousCmdSent = ""


        
    

    def __openMqttServer(self, username, password):
        self.__mqttClient.username_pw_set(username, password)
        self.__mqttClient.on_connect = self.__onMqttConnect
        self.__mqttClient.on_message = self.__onMqttMessage

        self.__mqttClient.tls_set((self.__MODPATH + "/server.CA.crt"))
        self.__mqttClient.tls_insecure_set(True)


        self.__mqttClient.connect(self.hostAddress, self.hostPort)

        self.__mqttClient.loop_start()


    def __onMqttConnect(self, client, userdata, flags, rc):
            print("Connected to Mqtt server with result code ", (rc))
            pass
    
    def __onMqttMessage(self, client, userdata, message):
        
        if message.topic == str(self.__jackbordID + "/jprint") and self.__inLiveMode == True:
            self.__printOutput += (message.payload.decode() + "\n")
        
        if (message.topic) in self.__channelClassList.keys():
            incomingValue = message.payload.decode()

            if incomingValue != self.__channelClassList[message.topic].get():
                self.__channelClassList[message.topic].updateFromServer(incomingValue)
        

    
    def bindchan(self, channelNum):
        
        #Enforce string type on topic key
        # if not type(channelNum) == str:
        #     channelNum = str(channelNum)

        if type(channelNum) == str:
            channelNum = str(self.__parsePinString(channelNum))

        if type(channelNum) == int:
            channelNum = str(channelNum)

        #String parsing0.
        newChannelClass = Channel(self.__mqttClient, self.__jackbordID, channelNum)
        self.__channelClassList[str(self.__jackbordID + "/chan/" + channelNum)] = newChannelClass
        self.__mqttClient.subscribe(self.__jackbordID + "/chan/" + channelNum)

        return(newChannelClass)
    
    def cmd(self, commandString):
        #BAD PROGRAMMING: This does nothing for the desired channel is modifed by a separate program.
        #The reason why we want to do this is to cut down on redundant / spammy messages to mqtt.
        #Perhaps implement a way to check what the value of the channel on mqtt broker is?
        if (commandString != self.__previousCmdSent):
            self.__mqttClient.publish(str(self.__jackbordID + "/cmd"), payload=commandString)
            self.__previousCmdSent = commandString
    
    def cmdlive(self):
        self.__inLiveMode = True
        self.__mqttClient.subscribe(str(self.__jackbordID + "/jprint"))
        print("This is live command mode for the not softserve:")
        print("Please hit Ctrl + C to return to python interpreter")
        print("Yes, this is quite developmental. Yes, this is really only if you are in python interactive shell")

        while True:
            try:
                time.sleep(1)
                if not self.__printOutput == "":
                    print(self.__printOutput)
                    self.__printOutput = ""

                
                command = input("JB CMD>>")
                self.cmd(command)
                    
            except KeyboardInterrupt:
                self.__inLiveMode = False
                self.__mqttClient.unsubscribe(str(self.__jackbordID + "/jprint"))
                print()
                break

    
    def __parsePinString(self, pinString):
        if len(pinString) == 2:
            if pinString[0].isalpha() and pinString[1].isdigit():
                pinsPerPort = 5
                chanNum = (ord(pinString[0].lower()) - ord("a")) * pinsPerPort + int(pinString[1])

                return chanNum