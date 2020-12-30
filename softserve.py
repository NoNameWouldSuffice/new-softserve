import paho.mqtt.client as mqtt
from queue import Queue
import time

#TODO / THOUGHTS / possible features:
#   Type enforcing: Give the user the ability to specify what data-type the variable will be automagically interpreted as
#   this at best could be super efficient, and save programmers the hassle of needing to do their own type conversion
#   at worst, it would step on the toes of people who don't know exactly why their code isn't working but has something to do
#   with this hidden layer

#   Credentials saved to config file?

#DISPLAY FEEDBACK FROM THE JACKBORD

class Jackbord():
    def __init__(self, jackbordID, username, password):

        #List of bound variables / channel classes
        #Mqtt broker address
        #Mqtt broker port
        #Mqtt client instance

        self.__channelClassList = {} #Format: "mqtt topic" : ChannelClass instance

        self.hostAddress = "mqtta.jackbord.org"

        self.__jackbordID = jackbordID

        self.hostPort = 1883

        self.__mqttClient = mqtt.Client()

        self.__openMqttServer(username, password)

        self.__inLiveMode = False
        self.__printOutput = ""

        self.__previousCmdSent = ""


        
    

    def __openMqttServer(self, username, password):
        self.__mqttClient.username_pw_set(username, password)
        self.__mqttClient.on_connect = self.__onMqttConnect
        self.__mqttClient.on_message = self.__onMqttMessage


        self.__mqttClient.connect(self.hostAddress, self.hostPort)

        self.__mqttClient.loop_start()


    def __onMqttConnect(self, client, userdata, flags, rc):
            #print("Connected to Mqtt server with result code ", (rc))
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
        newChannelClass = channel(self.__mqttClient, self.__jackbordID, channelNum)
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



class channel():
    def __init__(self, mqttClient, jackbordID, channelNum):
        self.__mqttClient = mqttClient
        self.jackbordID = jackbordID
        self.__channelNum = channelNum
        self.__value = "Null"

    def updateFromServer (self, message):
        self.__value = message

    
    def get(self):
        return self.__value
    
    def set(self, value):
        self.__value = value
        self.__mqttClient.publish(topic=str(self.jackbordID + "/set/" + self.__channelNum), payload=value)


if __name__ == "__main__":
    jb1 = Jackbord("red.head", "111254186336836811343", "1fa60c9fc6")
