import paho.mqtt.client as mqtt



class Jackbord():
    def __init__(self, jackbordID, username, password):

        #List of bound variables / channel classes
        #Mqtt broker address
        #Mqtt broker port
        #Mqtt client instance

        self.__channelClassList = {} #Format: "mqtt topic" : ChannelClass instance

        self.hostAddress = "mqtta.jackbord.org"
        print(type(self.hostAddress))

        self.__jackbordID = jackbordID

        self.hostPort = 1883

        self.__mqttClient = mqtt.Client()

        self.__openMqttServer(username, password)
    

    def __openMqttServer(self, username, password):
        self.__mqttClient.username_pw_set(username, password)
        self.__mqttClient.on_connect = self.__onMqttConnect
        self.__mqttClient.on_message = self.__onMqttMessage

        #Connect to the mqtt broker
        self.__mqttClient.connect(self.hostAddress, self.hostPort)
        #Start our mqtt client loop
        self.__mqttClient.loop_start()


    def __onMqttConnect(self, client, userdata, flags, rc):
            print("Connected to Mqtt server with result code ", (rc))
    
    def __onMqttMessage(self, client, userdata, message):
        if (message.topic) in self.__channelClassList.keys():
            incomingValue = message.payload.decode()

            if incomingValue != self.__channelClassList[message.topic].get():
                self.__channelClassList[message.topic].updateFromServer(incomingValue)
    
    def bindVar(self, topic):
        
        #Enforce string type on topic key
        if not type(topic) == str:
            topic = str(topic)

        newChannelClass = channel(self.__mqttClient, self.__jackbordID, topic)
        self.__channelClassList[str(self.__jackbordID + "/" + topic)] = newChannelClass
        self.__mqttClient.subscribe(self.__jackbordID + "/" + topic)

        return(newChannelClass)
    
    def cmd(self, commandString):
        self.__mqttClient.publish(str(self.__jackbordID + "/cmd"), payload=commandString)
    
    def cmdlive(self):
        print("This is live command mode for the not softserve:")
        print("Please hit Ctrl + C to return to python interpreter")
        print("Yes, this is quite developmental. Yes, this is really only if you are in python interactive shell")

        while True:
            command = input("JB CMD>>")
            self.cmd(command)





class channel():
    def __init__(self, mqttClient, jackbordID, topic):
        self.__mqttClient = mqttClient
        self.__jackbordID = jackbordID
        self.__topic = topic
        self.__value = "Null"

    def updateFromServer (self, message):
        self.__value = message
        print("Message updated")

    
    def get(self):
        return self.__value
    
    def set(self, value):
        self.__value = value
        self.__mqttClient.publish(topic=str(self.__jackbordID + "/" + self.__topic), payload=value)
