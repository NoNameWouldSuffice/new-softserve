import os
from softserve.channel import Channel
from softserve.credLoader import CredLoader
import time
import ssl
import atexit

# import logging
# logging.basicConfig(level=logging.DEBUG)

try:
    # We will attempt to load dependencies from the built-in deps module which will be present if this is a standalone copy of softserve
    import softserve.deps.paho.mqtt.client as mqtt

except ImportError:
    # We could not import the deps that will be here in the standalone version of softserve, try importing the deps as if they were installed along with
    # softserve using pip
    import paho.mqtt.client as mqtt


class Jackbord():
    def __init__(self, profileID):

        # List of bound variables / channel classes
        # Mqtt broker address
        # Mqtt broker port
        # Mqtt client instance

        # The directory of where softserve has been imported from
        self.__MODPATH = os.path.dirname(__file__)

        # A flag in global space used to pass the result code from the __onMqttConnect callback and the openMqttServer method
        self.__mqttResultCode = -1

        # Dictionary that stores channel class instances for later use
        self.__channelClassList = {}  # Format: "mqtt topic" : ChannelClass instance

        self.hostAddress = "mqtta.jackbord.org"

        # Instance of the credloader class
        self.credLoader = CredLoader()

        self.__profileID = profileID

        self.hostPort = 80

        self.__mqttClient = mqtt.Client()

        self.__openMqttServer()

        self.__inLiveMode = False
        self.__printOutput = ""

        self.__previousCmdSent = ""

        self.__clientConnected = True

        self.__sendMID = -1  # The ID of the last publish request

        self.__receiveMID = -1

        atexit.register(self.__gracefulExit)

    # def onMqttLog(self, client, userdata, level, buf):
    #     print("log: ",buf)

    def __openMqttServer(self):
        # logger = logging.getLogger(__name__)
        # self.__mqttClient.enable_logger(logger)
        
        
        credDict = self.credLoader.loadCreds()
        self.__mqttClient.username_pw_set(
            credDict["username"], credDict["password"])
        self.__mqttClient.on_connect = self.__onMqttConnect
        self.__mqttClient.on_message = self.__onMqttMessage
        self.__mqttClient.on_publish = self.__onMqttPublish
        # self.__mqttClient.on_log = self.onMqttLog

        self.__mqttClient.tls_set((self.__MODPATH + "/server.CA.crt"))
        self.__mqttClient.tls_insecure_set(True)

        mqttTimeout = 5

        timeStop = time.time() + mqttTimeout

        self.__mqttClient.connect(self.hostAddress, self.hostPort)
        self.__mqttClient.loop_start()

        while self.__mqttResultCode == -1:
            time.sleep(0.1)
            if time.time() > timeStop:
                raise Exception(
                    'Failed to connect after {0} seconds'.format(mqttTimeout))

            if self.__mqttResultCode != 0 and self.__mqttResultCode != -1:
                raise Exception("Connection failed. Result code is {0}".format(
                    self.__mqttResultCode))

    def __onMqttConnect(self, client, userdata, flags, rc):
        if len(self.__channelClassList.keys()) != 0:
            for topic in self.__channelClassList.keys():
                self.__mqttClient.subscribe(str(topic))

        self.__mqttResultCode = rc

    def __onMqttMessage(self, client, userdata, message):

        if message.topic == str(self.__profileID + "/jprint") and self.__inLiveMode == True:
            self.__printOutput += (message.payload.decode() + "\n")

        if (message.topic) in self.__channelClassList.keys():
            incomingValue = message.payload.decode()

            if incomingValue != self.__channelClassList[message.topic].get():
                self.__channelClassList[message.topic].updateFromServer(
                    incomingValue)

    def __onMqttPublish(self, client, userdata, mid):
        # print("Userdata: " + str(userdata))
        # print("Result: " + str(mid))
        self.__receiveMID = mid
        # print("Receive MID is now: ", mid)

    def bindchan(self, channelNum):

        # Enforce string type on topic key
        # if not type(channelNum) == str:
        #     channelNum = str(channelNum)

        if type(channelNum) == str:
            channelNum = str(self.__parsePinString(channelNum))

        if type(channelNum) == int:
            channelNum = str(channelNum)

        # String parsing0.
        newChannelClass = Channel(
            self.__mqttClient, self.__profileID, channelNum, self)
        self.__channelClassList[str(
            self.__profileID + "/chan/" + channelNum)] = newChannelClass
        self.__mqttClient.subscribe(self.__profileID + "/chan/" + channelNum)

        return(newChannelClass)

    def cmd(self, commandString):
        # BAD PROGRAMMING: This does nothing for the desired channel is modifed by a separate program.
        # The reason why we want to do this is to cut down on redundant / spammy messages to mqtt.
        # Perhaps implement a way to check what the value of the channel on mqtt broker is?
        if commandString != self.__previousCmdSent:
            self.updateSentMID(self.__mqttClient.publish(
                str(self.__profileID + "/cmd"), payload=commandString)[1])
            self.__previousCmdSent = commandString
            self.waitUntilPublished(5, 0.1)

    def cmdlive(self):
        self.__inLiveMode = True
        self.__mqttClient.subscribe(str(self.__profileID + "/jprint"))
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
                self.__mqttClient.unsubscribe(
                    str(self.__profileID + "/jprint"))
                break

    def __parsePinString(self, pinString):
        letToNum = {"a": 0, "b": 1, "c": 2, "d": 3, "l": 4.8}

        if len(pinString) == 2:
            if pinString[0].isalpha() and pinString[1].isdigit():
                pinsPerPort = 5
                chanNum = int(
                    (letToNum.get(pinString[0].lower())) * pinsPerPort + int(pinString[1]))

                return chanNum

    def __gracefulExit(self):
        if self.__clientConnected:

            attempts = 5
            self.waitUntilPublished(attempts, 0.5)

            self.__mqttClient.disconnect()

    def updateSentMID(self, newMID):
        if newMID > self.__sendMID:
            self.__sendMID = newMID
            # print("Sent mid is now: ", newMID)

    def donePublishing(self):
        if self.__receiveMID >= self.__sendMID:
            return True
        else:
            return False

    def waitUntilPublished(self, attempts, delay):
        for attempt in range(0, attempts):
            if self.donePublishing():
                break
            else:
                # print("Failed to quit, client not done publishing")
                time.sleep(0.01)
