#Note: Class does not import methods used in Jackbord.py because an already existing Jackbord object is
# a mandatory parameter of this class

class MqttTopic():
    def __init__(self, mqttClient, jackbordID, mqttTopic, jbObject):
        self.__mqttClient = mqttClient
        self.jackbordID = jackbordID
        self.mqttTopic = mqttTopic
        self.__value = 0
        self.__jbObject = jbObject

    def updateFromServer(self, message):
        self.__value = message

    def get(self):
        return self.__value

    def set(self, value):
        self.__value = value
        newMID = self.__mqttClient.publish(
            topic=self.mqttTopic, payload=value)[1]
        self.__jbObject.updateSentMID(newMID)
