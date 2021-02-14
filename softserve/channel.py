class Channel():
    def __init__(self, mqttClient, jackbordID, channelNum, jbObject):
        self.__mqttClient = mqttClient
        self.jackbordID = jackbordID
        self.__channelNum = channelNum
        self.__value = 0
        self.__jbObject = jbObject

    def updateFromServer (self, message):
        self.__value = message

    
    def get(self):
        return self.__value
    
    def set(self, value):
        self.__value = value
        newMID = self.__mqttClient.publish(topic=str(self.jackbordID + "/set/" + self.__channelNum), payload=value)[1]
        self.__jbObject.updateSentMID(newMID)