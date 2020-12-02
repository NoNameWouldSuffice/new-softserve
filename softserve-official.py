###SOFTSERVE SOFTWARE SERVER V11-1
###LACHLAN R. PAULSEN, 2019. All rights reserved?
###CHANGELOG:

#Mqtt support has appeared (finally). It is likely to go through some improvement
#During the next few updates but hey, it works!

#Have opened up sending raw udp commands back to the world. Remember, with great
#power comes great responsibility.

#Thoughts:
#Need to improve error handling in places where it should be improved. Not limited to:
# Connecting to mqtt brokers - use error codes?
# Check if port/address is valid?
# If someone trys to pass "ha" as a ip address
#Test tables anyone?

#Also streamlined making multiple remotes in git a tad more streamlined with the multiremote
#Python script you see in the repo (if you have it. Which you shouldn't)


import socket
import threading
import time
import parse #Used for interpreting formatted strings from other servers as variables.
             #This is good shit. Need to use more of it if I plan to re-draft the
             #code.

import paho.mqtt.client as mqtt
import sys

###CHANNELS class

class CHANNELS():

    #__INIT__ function: This sets up the CHANNELS object upon instantiation (however that's spelled) with all of the proper values and variables
    def __init__(self):
        #Whether or not the UDP server prints out semi-useful output. What? It might prove useful to someone eventually...
        self.__verbosity = False

        #The dictionary containing the local channels. Change the numbers here to add or subtract channels
        self.__channelList = {
        "1" : "Null", "2": "Null",
        "3" : "Null", "4" : "Null",
        "5" : "Null", "6" : "Null",
        "7" : "Null", "8" : "Null",
        "9" : "Null", "10" : "Null",
        }

        #Get the ip of this machine using getMyIP function
        #A bit of a caveat here - This may not automatically get the right ip if this computer is connected to multiple networks
        self.myIP = self.__getMyIP()

        #Define the port that this server will use for communication here. Change this and it will use that port
        self.__UDP_PORT = 6000

        #Create a udp sock for sending data to other servers
        self.__senderSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #Tell the socket to reuse an existing address if it is available. This is to counter the "Adress already in use" error
        self.__senderSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #Create a udp sock for receiving data from other servers
        self.__receiverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__receiverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #Create the recv_udp subthread. This means that when we call self.__recvSubThread.start() it will launch the recv_udp function in an independent thread that's independent from the main program (However uses and maintains the same variables as the main program)
        #The daemon=True sets this thread to stop whenever the main program gets killed.
        self.__recvSubThread = threading.Thread(target = self.__recv_udp, daemon=True)

        #How long this server will wait for feedback from another server before it gives up. Time is in seconds (0.5 is half a second, cetera)
        self.feedbackWaitLimit = 3.0

        #remoteServerFeedback: This variable acts as an intermediary between the getRemoteChannel function, which returns the value of a channel on a remote server, and the recv_udp subthread.
        self.__remoteServerFeedback = ""

        #invalidChannelNumberError: This is the "error" string we send to a client who tried using a channel number we don't have
        self.__invalidChannelNumberError = "%INVCHANUM%"

        self.__mqttClient = mqtt.Client()

        self.__mqttChannels = {}

        #SHORTCUTS: These make the main functions in this module callable using 3 letters instead of who knows how many.
        #For example, channelClass.getRemoteChannel() will function the same as channelCLass.GRC()

        #A user can now call the getRemoteChannel and setRemoteChannel with channelClass.GRC() and channelClass.SRC() respectively
        self.GRC = self.getRemoteChannel
        self.SRC = self.setRemoteChannel

        #Same goes for local channel commands
        self.GLC = self.getLocalChannel
        self.SLC = self.setLocalChannel

        #And the returnChannelList as well
        self.RCL = self.returnChannelList

        #And verbosity
        self.VBT = self.verbosityToggle

        #And channel list generation
        self.CCL = self.createChannelList

        #And with getting the set channels from a remote server
        self.GSC = self.getSetChannels

        #More so with openMqttServer
        self.OMS = self.openMqttServer

        #And again with single mqtt bind and batch mqtt bind
        self.SMB = self.singleMqttBind
        self.BMB = self.batchMqttBind

        #And again with returning a mqtt list
        self.RML = self.returnMqttList

        #Oh look. A rawUdpSend function
        self.RUS = self.rawUdpSend

        #Open the udp server after softserve configuration has completed
        #Successfully.
        self.__openUDPServer()


    #This is the function that toggles verbosity on and off
    #I have it here mostly to give us some meta verbosity like turning verbosity on, turning verbosity off
    def verbosityToggle(self):
        if self.__verbosity == True:
            self.__verbosity = False
            print("Turning off verbosity...")
        else:
            self.__verbosity = True
            print("Turning on verbosity...")


    ###CREATE CHANNEL LIST function:
    #Use this function to generate a new channel list for this program instead of
    #The default 1 to 10. This function will completely remove you current channel list
    #Including all of it's values, so only run use this function once in the beginning
    #Of your program
    # IDEA: Should this be only a one-shot function? The worst case scenario is when
    #A user has put this inside a while true loop and their channel list is constantly
    #Destroyed and effectively useless. Need to consider.
    def createChannelList(self, start, stop):
        newChannelList = {}
        for numID in range(start, stop + 1):
            newChannelList[str(numID)] = "Null"

        if self.__verbosity:
            print("Have created a new channel list with channel numbers {0} to {1}".format(start, stop))


        self.__channelList = newChannelList

    #GETMYIP function:
    #Returns an ip adress that this server is using.
    #Note that this may not always return the proper ip if the machine that this is running on has muliple network connections (i.e. Internal wireless + usb dongle or Internal wireless + ethernet cable)
    def __getMyIP(self):
        try:
            #Create a dummy socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #Connect to a dummy ip address and port
            s.connect(("8.8.8.8", 80))
            #Get the ip address that we just used to connect to that dummy port
            myIP = (s.getsockname()[0])
            #Close the dummy socket
            s.close()
        except OSError:
            print("Have failed to determine our ip address on the network.\nYou sure you're connected to any network?")
            sys.exit()


        return myIP

    #rawUdpSend function:
    #This is the generic function used to send udp commands to other servers
    def rawUdpSend(self, UDP_ip, UDP_data):

        # Send a udp >>>>>>>>>>
        self.__senderSock.sendto(UDP_data.encode('utf-8'), (UDP_ip, self.__UDP_PORT))

    #RECV_UDP function:
    #This is out main server loop. This function is operated in a seperate dedicated thread so it can constantly wait for a response without holding up the rest of the program.
    #It also interprets any string data receives and forwards it to the proper functions if it deems the received string to be a command.
    def __recv_udp(self):
        while True:
            #Wait and listen for a response. When received, update the data and addr variables
            primaryData, addr = self.__receiverSock.recvfrom(1024)
            #Extract the client's ip from the addr variable that is naturally attached to any UDP command we receive
            clientIP = addr[0]
            #Decode data from UTF-8 back into a regular string (UTF-8 encoded strings have an annoying b in front of them however encoding them is necessary for python 3 socket networking to like them)
            primaryData = primaryData.decode('UTF-8')

            #If the verbosity has been turned on, print out the raw data we have received
            if self.__verbosity:
                print(primaryData)

            #Split the initial data list into seperate commands by pipes | into sub commands the user want's to chain
            primaryDataList = [x.strip() for x in primaryData.split("|")]

            #Iterate thought the sub commands
            for secondaryData in primaryDataList:

                #Split the string into a list by spaces i.e "This is a string" will be turned into ["This", "is", "a", "string"]
                secondaryDataList = secondaryData.split(" ")

                #If the verbosity has been turned on, print out this list
                if self.__verbosity:
                    print(secondaryDataList)

                #If the dataList's first item is either "sc" or "SC" then we know we have received a set channel command
                if secondaryDataList[0] == "sc" or secondaryDataList[0] == "SC":
                    #Check whether or not the list is long enough to be a valid set channel command (should be at least "COMMAND", "CHANNEL", "VALUE")
                    if len(secondaryDataList) >= 3:
                        #Forward the data to the setChannel function
                        self.__setChannel(secondaryDataList, clientIP)

                #If the dataList's first item is either "gcl" or "GCL" then we know we have received a get channel command
                elif secondaryDataList[0] == "gcl" or secondaryDataList[0] == "GCL":
                    #Check whether or not the list is long enough to ba a valid get channel command (should be at least "COMMAND", "CHANNEL")
                    if len(secondaryDataList) >= 2:
                        #Forward the data to the getChannel function
                        self.__giveChannel(secondaryDataList, clientIP)

                #If the dataList's first item is either "gsc" or "GSC", then we know we have received a get set channels command
                elif secondaryDataList[0] == "gsc" or secondaryDataList[0] == "GSC":
                    self.__giveSetChannels(clientIP)



                else:
                    self.__interpretServerFeedback(secondaryDataList, clientIP)


    #GIVE CHANNEL: This function sends the value of a channel to another server upon the server sending a "GET CHANNEL" command to us
    def __giveChannel(self, dataList, clientIP):
        #If verbosity is turned on, let the user know what's going down in the background
        if self.__verbosity:
            print("We have received a get channel command from {0}".format(clientIP))
        #Extract the channel number that the client want's to receive the value of from the raw data list
        channelNum = dataList[1]

        #Check if said channel number actually exists here else it's not our problem
        if channelNum in self.__channelList.keys():
            #If verbosity is on, print out what we have just done
            if self.__verbosity:
                print("Sending the value of channel %s to address %s" % (channelNum, clientIP))

            outputString = "%s" % (self.__channelList[channelNum])

            #Send the signed value of the requested channel to the client
            self.rawUdpSend(clientIP, outputString)
        #If the person has requested to change the value of a channel we don't have, send them a polite message saying they goofed.
        else:
            if self.__verbosity:
                print("Get Channel has been given an invalid channel number. Are you supposed to provide this channel?")
            self.rawUdpSend(clientIP, self.__invalidChannelNumberError)


    #SET CHANNEL: This function updates the value of a given channel upon another server sending a "SET CHANNEL" command to us
    def __setChannel(self, dataList, clientIP):

        #If verbosity is turned on, let the user know what's going down in the background
        if self.__verbosity:
            print("We have received a set channel command from {0}".format(clientIP))

        #Extract the number of the channel that the client has requested to be updated from the datalist
        channelNum = dataList[1]

        #Actually check if said channel exists on this server
        if channelNum in self.__channelList.keys():

            #This loop then assumes that everything after the channel number is the value and stitches it back together, adding in a space between the item until it hits the last item
            value = ""
            position = 0
            for str in dataList[2:]:
                position += 1
                value += str
                if position != len(dataList[2:]):
                    value += " "

            #If verbosity is turned on, oh you get the idea
            if self.__verbosity:
                print("Setting the value of channel %s to %s" % (channelNum, value))

            #Actually update the value of the local channel here
            self.__channelList[channelNum] = value

            if self.__verbosity:
                print(self.__channelList)

        #If the person has requested to change the value of a channel we don't have, send them a polite message saying they goofed.
        else:
            if self.__verbosity:
                print("Set Channel has been given an invalid channel number. Are you sure you are supposed to provide this channel?")
            self.rawUdpSend(clientIP, self.__invalidChannelNumberError)

        #If this channel is a mqtt bound channel, update the value on the mqtt broker
        if channelNum in self.__mqttChannels.keys():
            self.__mqttClient.publish(topic=self.__mqttChannels[channelNum], payload=value)

    #INTERPRET SERVER FEEDBACK:
    #This function assumes that the string we have received is feedback from another channel server / the value of a channel we have requested from another server and stich it together and save as the global variable
    #remoteServerFeedback. Most of the time this would store any invalid commands or miscelaneous crap sent to us over udp. However, we will look to this variable whenever we query another server using the getRemoteChannel function.
    #Odds are that if this variable is changed within the 3 seconds we wait for a response from a server, it is the value we are looking for. To make doubly sure, we check if this variable has come from the ip we have queried.
    def __interpretServerFeedback(self, dataList, clientIP):

        #Same loop de swoop thing that stitches back together the value we want to see
        value = ""
        position = 0
        for str in dataList:
            position += 1
            value += str
            if position != len(dataList):
                value += " "

        #Update the global remoteServerFeedback variable here
        self.__remoteServerFeedback = (value, clientIP)



    #GET REMOTE CHANNEL:
    #This function is designed to be called from someone else's program whenever they want to get the value of an external server's channel. It will return said value back into someone else's code
    def getRemoteChannel(self, remoteIP, channelNum):
        #If the user has put in the channel number as anything that isn't a string, turn it into a string
        #Putting in any non-numerical input as a channel number can and will break the program. We can't act on invalid input.
        #IDEA: Should we print out an error saying why they screwed up when the program breaks.
        if type(channelNum) != str:
            channelNum = str(channelNum)

        #If the global remoteServerFeedback is not empty, clear it now so if we try to query a non-existant server this function doesn't return a wrong variable
        if self.__remoteServerFeedback != "":
            self.__remoteServerFeedback = ""

        #Create an empty outputVale variable. All this does is store a copy of the global remoteServerFeedback so we can clear it ready for the next use.
        outputValue = ""

        #Redundant comment here is redundant
        if self.__verbosity:
            print("Requesting the value of channel %s in server at %s" % (channelNum, remoteIP))

        #send the request for the value of some other server's channel here in the COMMAND CHANNEL format
        #Has now been changed to gcl for Get channel lachlan to funtion with the jackbord
        self.rawUdpSend(remoteIP, "gcl %s" % (channelNum))

        #Set the time waited clock variable to 0.0. Yes, there is probably a better way like an actualy timer object or something but this just works
        timeWaited = 0.0

        #Wait for a response from the server until max wait time has been reached
        while timeWaited < self.feedbackWaitLimit:

            #If we have received the external server's feedback via the global remoteServerFeedback variable, stop waiting
            if self.__remoteServerFeedback:
                if self.__verbosity:
                    print("Have received %s as the value of channel %s from server at %s after %s seconds" % (self.__remoteServerFeedback[0], channelNum, self.__remoteServerFeedback[1], timeWaited))

                #Check if the data really has come from the server we have queried
                if remoteIP == self.__remoteServerFeedback[1]:
                    if self.__verbosity:
                        print("This is the data we are looking for")
                    #Make a copy of the global remoteServerFeedback variable here
                    outputValue = self.__remoteServerFeedback[0]
                    break
                else:
                    if self.__verbosity:
                        print("Hold up. This data did not come from the server at %s. It came from %s. Continuing wait for proper feedback" % (remoteIP, self.__remoteServerFeedback[1]))
                    #Empty the false server feedback
                    self.__remoteServerFeedback = ""

            #Wait an increment of 0.01 seconds so that we update the timeWaited variable by time and not space
            time.sleep(0.01)
            #Update how long we have waited by
            timeWaited += 0.01

        #If we never received any feedback whatsoever and the verbosity is on, tell the user
        if not self.__remoteServerFeedback and self.__verbosity:
            print("Failed to get channel from remote server after a %s second wait" % (self.feedbackWaitLimit))
            outputValue = ""


        #Empty out remoteServerFeedback for next time
        self.__remoteServerFeedback = ""

        #Return the value of the requested external channel
        return outputValue

    #SET REMOTE CHANNEL:
    #This function is designed to be use in someone else's code whenever they want to update the value of an external server's channel
    #This is basically a glorified send_udp function however I wanted symmetry since getRemoteChannel got it's own function and I don't trust the user with access directly to the send_udp function
    #which should by all accounts be a strictly internal function
    def setRemoteChannel(self, remoteIP, channelNum, value):
        #If the user has put in the channel number as anything that isn't a string, turn it into a string
        #Putting in any non-numerical input as a channel number can and will break the program. We can't act on invalid input.
        #IDEA: Should we print out an error saying why they screw ed up when the program breaks.
        if type(channelNum) != str:
            channelNum = str(channelNum)

        if self.__verbosity:
            print("Changing the value of channel %s in server at %s to %s" % (channelNum, remoteIP, value))

        #Send the request to the external server to update the channel of our choosing to the value of our choosing
        self.rawUdpSend(remoteIP, "sc %s %s" % (channelNum, value))

    #GET LOCAL CHANNEL:
    #From our local channel list retrieve the value of a channel by channel number and return it to the user
    def getLocalChannel(self, channelNum):
        #All channel numbers are strings. Turn it into a string just in case the user passed it as an integer
        if type(channelNum) != str:
            channelNum = str(channelNum)
        #If the channel number given by the user is in our dictionary, return the value of that channel
        if channelNum in self.__channelList.keys():
            if self.__verbosity:
                print("Returning the value of local channel ", channelNum)
            return self.__channelList[channelNum]

    #SET LOCAL CHANNEL
    #Update a channel value in our own channel list
    def setLocalChannel(self, channelNum, value):
        #All channel numbers are strings. Turn it into a string just in case the user passed it as an integer
        if type(channelNum) != str:
            channelNum = str(channelNum)
        #If the channel number given by the user is in our dictionary, update that channel
        if channelNum in self.__channelList.keys():
            self.__channelList[channelNum] = value

            if channelNum in self.__mqttChannels.keys():
                #Does this throw us into perpetual loops?
                self.__mqttClient.publish(topic=self.__mqttChannels[channelNum], payload=value)

            if self.__verbosity:
                print("Updating the value of local channel %s to %s" % (channelNum, value))

    #returnChannelList: Prints out the channel list, as I have made it private
    #This is only temporary and added for debugging purposes
    def returnChannelList(self):
        if self.__verbosity:
            print("Displaying a temporary channel dictionary. This will not be updated")
        return dict(zip(self.__channelList.keys(), self.__channelList.values()))


    #OPEN UDP SERVER:
    #This function binds the networking sock to the address and port we want to receive commands with and starts the recvSubThread um thread, essentially opening this server for business.
    #This is now run automagically.
    def __openUDPServer(self):
        #Bind the ip and port for receiving and sending.
        #We now use the empty string "" socket wildcard so we can receive incoming
        #Messages from all our interfaces.
        self.__receiverSock.bind(("", self.__UDP_PORT))
        #Start the receiving thread here
        self.__recvSubThread.start()

    #The function can be used to query a channel server to return a list of all it's non-null channels and their variables
    def getSetChannels(self, remoteIP):

        #If the global remoteServerFeedback is not empty, clear it now so if we try to query a non-existant server this function doesn't return a wrong variable
        if self.__remoteServerFeedback != "":
            self.__remoteServerFeedback = ""

        #Create an empty outputVale variable. All this does is store a copy of the global remoteServerFeedback so we can clear it ready for the next use.
        outputValue = ""

        #Redundant comment here is redundant
        if self.__verbosity:
            print("Requesting a list of set channels from server at %s" % (remoteIP))

        #Send the list for the request
        self.rawUdpSend(remoteIP, "gsc")

        #Set the time waited clock variable to 0.0. Yes, there is probably a better way like an actualy timer object or something but this just works
        timeWaited = 0.0

        #Wait for a response from the server until max wait time has been reached
        while timeWaited < self.feedbackWaitLimit:

            #If we have received the external server's feedback via the global remoteServerFeedback variable, stop waiting
            if self.__remoteServerFeedback:
                if self.__verbosity:
                    print("Have received the list of set channels from server at %s after %s" % (self.__remoteServerFeedback[1], timeWaited))

                #Check if the data really has come from the server we have queried
                if remoteIP == self.__remoteServerFeedback[1]:
                    if self.__verbosity:
                        print("This is the data we are looking for")
                    #Make a copy of the global remoteServerFeedback variable here
                    outputValue = self.__remoteServerFeedback[0]
                    break
                else:
                    if self.__verbosity:
                        print("Hold up. This data did not come from the server at %s. It came from %s. Continuing wait for proper feedback" % (remoteIP, self.__remoteServerFeedback[1]))
                    #Empty the false server feedback
                    self.__remoteServerFeedback = ""

            #Wait an increment of 0.01 seconds so that we update the timeWaited variable by time and not space
            time.sleep(0.01)
            #Update how long we have waited by
            timeWaited += 0.01

        #If we never received any feedback whatsoever and the verbosity is on, tell the user
        if not self.__remoteServerFeedback and self.__verbosity:
            print("Failed to get the list of set channels after %s second wait" % (self.feedbackWaitLimit))
            outputValue = ""


        #Empty out remoteServerFeedback for next time
        self.__remoteServerFeedback = ""

        #Begin interpreting the string as a dictionary:
        outputChannelDict = {}

        if outputValue:
            #From the string of lines split it up into a list of every line. (i.e.) "line1\nline2" will become ["line1", "line2"]
            outputLineList = outputValue.split("\n")
            #Define our format string. The parse module can be seen as the inverse of python's str.format() method.
            #Think of str.format() as format string + vars = formatted string. Parse is like formatted string + format string = vars. Therefore we can use
            #parse to retreive variables from any formatted string we receive
            ###THOUGHT: Could we use this sort of string comprehension for other parts of this program?
            format_string = "Chan {0} = {1}"

            #Check to see if there is one or more lines in this list. WE DO NEED BETTER DATA VALIDATION HERE!!!
            #Expected would be "Channel 1 = five\nChannel 2 = six". Boundary would be "Channel 1 = five".
            #Invalid would be any string that doesn't follow the format "Channel {0} = {1}"
            if len(outputLineList) >= 1:
                for channelPair in outputLineList:
                    newChannelNum, newChannelValue = parse.parse(format_string, channelPair)
                    outputChannelDict[newChannelNum] = newChannelValue




                #Return the value of the requested external channel
                return outputChannelDict
        else:
            return("")

    #GIVE SET CHANNELS: This function is automatically run whenever we receive a "gsc" command from a server wanting our list of set channels and provides them with just that
    #The string that this actually sends through UDP is in a human readable format that follows how this command is
    #handled by the Jackbord but this string gets interpreted as a dictionary by other softserve servers
    def __giveSetChannels(self, remoteIP):
        nonNullChannels = {}
        formattedChannelString = ""
        for channelNum in list(self.__channelList.keys()):
            #Check to see if this channel isn't Null
            if self.__channelList[channelNum] != "Null":
                nonNullChannels[channelNum] = self.__channelList[channelNum]

        #Append formatted lines to the output string. We are wanting the channels
        #in this string to be ordered so we are iterating over an ordered list of the dict keys
        #We also have to turn each channel number back into an integer so that python sorts them correctly (i.e. no 1, 10, 2, 20)
        for channelNum in sorted([int(x) for x in list(nonNullChannels.keys())]):
            #Append the formatted pair to the string. We need to make sure that the channelNum is a string again
            #so we can properly query our channel list dictionary
            formattedChannelString += ("Chan {0} = {1}".format(channelNum, nonNullChannels[str(channelNum)]))
            if channelNum != sorted(list(nonNullChannels.keys()))[-1]:
                formattedChannelString += ("\n")

        self.rawUdpSend(remoteIP, formattedChannelString)

    ###MQTT functions:

    ### onMqttConnect callback function:
    ##This function is called whenever the mqtt client has connected
    ##To a server. This just prints out the result code of the connect if
    ##Verbosity is on
    def __onMqttConnect(self, client, userdata, flags, rc):
        if self.__verbosity:
            print("Connected to Mqtt server with result code ", (rc))

    ###onMqttMessage callback function:
    ##This function is called whenever the mqtt client has connected
    ##To a server. This handles the updating of local mqtt bound channels
    ##Whenever the mqtt client receives a message.
    def __onMqttMessage(self, client, userdata, message):
        #Check if we have any channels bound to the topic we've just received
        if message.topic in self.__mqttChannels.values():
            #Search through our mqtt channels to find the channel number that is
            #bound to the topic we've just received
            for channelNum, topic in self.__mqttChannels.items():
                if topic == message.topic:

                    #Likely here we need to make sure that we ignore messages that aren't unique.
                    #This is to avoid perpetual loops of sending update messages to the poor jackbord

                        #When we've found that channel number, update that channel
                        #With the appropriate message
                        self.__channelList[channelNum] = message.payload.decode()
                        if self.__verbosity:
                            print("Have received a value of {0} for channel {1} from mqtt server".format(message.payload.decode(), channelNum))


    ###OPEN MQTT SERVER:
    ##This function is responsible for connecting to an mqtt client, subscribing
    ##To everything happening on the topic (we sift through it later) and start the
    ##Independent paho mqtt client loop to effectively open up our quasi mqtt server
    def openMqttServer(self, brokerAddress, brokerPort, user=None, password=None):
        #If the user have given us a username AND a password, make it so that
        #Our client will use them when connecting to the server
        if user != None and password != None:
            self.__mqttClient.username_pw_set(user, password)

        #Configure the mqtt client to use the onMqttMessage and on mqttConnect
        #Functions whenever it connects or receives something
        self.__mqttClient.on_connect = self.__onMqttConnect
        self.__mqttClient.on_message = self.__onMqttMessage

        #Connect to the mqtt broker
        self.__mqttClient.connect(brokerAddress, int(brokerPort))
        #Start our mqtt client loop
        self.__mqttClient.loop_start()
        #Subscribe to everything so we get all messages from the broker

        #THOUGHTS: We should likely make it so that we initially subscribe to nothing and selectively subscribe to topics
        #bound to channels. More investigation required.
        self.__mqttClient.subscribe("#")

    ###SINGLE MMQTT BIND
    ##Used to do individual channel topic binds

    #Review the error messages / reasons for refusing an mqtt binding here
    def singleMqttBind(self, channelNum, mqttTopic):
        #Check if the channel specified exists
        if channelNum not in self.__channelList.keys():
            #If it doesn't tell the user
            #IDEA: How to standardise verbosity statements?
            if self.__verbosity:
                print("Failed to associate channel {0} with topic {1}. Reason: Channel does not exist".format(channelNum, mqttTopic))
        #Check if the topic specified is already bound to another channel
        elif mqttTopic in self.__mqttChannels.values():
            if self.__verbosity:
                print("Failed to associate channel {0} with topic {1}. Reason: Topic already assigned to channel".format(channelNum, mqttTopic))

        else:
            #If it passes those checks, add the channel / topic pair to our mqtt channels dict
            self.__mqttChannels[channelNum] = mqttTopic


    ###BATCH MQTT BIND:
    ##Used whenver you have a lot of mqtt topics to bind to channels
    #NOTE: We should probably make single mqtt bind a function that we can call repeatedly here
    def batchMqttBind(self, bindList):

        #Keep a record of channels that successfully get associated with mqtt topics here
        #Used for Verbosity statements
        newChannelAssociations = []

        #Declare the format string that will be used by parse to extract the channel number
        #And mqtt topic of each channel to be bound
        format_string = "{0} | {1}"

        #Go through each bindString in our list of bind strings
        for bindString in bindList:
            #Extract the specified channel number and mqtt topic for this associate
            channelNum, mqttTopic = parse.parse(format_string, bindString)

            #Strip both strings of any extra spaces
            channelNum.strip(" ")
            mqttTopic.strip(" ")
            #Check if the channel specified exists
            if channelNum not in self.__channelList.keys():
                if self.__verbosity:
                    print("Failed to associate channel {0} with topic {1}. Reason: Channel does not exist".format(channelNum, mqttTopic))
            #Check if the topic specified is already bound to another channel
            elif mqttTopic in self.__mqttChannels.values():
                if self.__verbosity:
                    print("Failed to associate channel {0} with topic {1}. Reason: Topic already assigned to channel".format(channelNum, mqttTopic))

            else:
                #If it passes those checks, add the channel / topic pair to our mqtt channels dict
                self.__mqttChannels[channelNum] = mqttTopic
                #Add the channel num to our list of successful associations
                newChannelAssociations.append(channelNum)

        if self.__verbosity:
                print("Successfully associated channels {0}".format(newChannelAssociations))

    def returnMqttList(self):
        if self.__verbosity:
            print("Displaying a temporary MQTT channel dictionary. This will not be updated")
        return dict(zip(self.__mqttChannels.keys(), self.__mqttChannels.values()))







if __name__ == "__main__":
    channelClass = CHANNELS()
