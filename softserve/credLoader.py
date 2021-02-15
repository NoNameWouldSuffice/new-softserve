import json
from json.decoder import JSONDecodeError
import os
import softserve

import tkinter as tk
from tkinter import filedialog

class CredLoader():
    def __init__(self):
        self.__credPath = os.path.dirname(__file__) + "/mqttCreds.json"

    def importCreds(self):
        root = tk.Tk()
        root.withdraw()

        filePath = filedialog.askopenfilename()

        try:
            with open(filePath) as newCredFile:
                credDict = json.load(newCredFile)
                if "username" in credDict and "password" in credDict:
                    with open(self.__credPath, "w") as storedCredFile:
                        json.dump(credDict, storedCredFile)
                        print("Credentials successfully imported")
                else:
                    print("JSON file does not contain username and password")
        except:
                print('Failed to read as JSON file')
    
    def loadCreds(self):
        try:
            with open(self.__credPath) as loadedCredFile:
                credDict = json.load(loadedCredFile)
                if "username" in credDict and "password" in credDict:
                    return credDict
                else:
                    raise JSONDecodeError("JSON file does not contain username and password")
        
        except Exception as e:

            exceptionType = type(e).__name__
            print(exceptionType)

            if exceptionType == "FileNotFoundError":
                print("\n####################\n CRED FILE NOT FOUND. \n YOU MUST IMPORT A VALID CRED FILE BY IMPORTING SOFTSERVE AND USING \n THE COMMAND softserve.importCreds()\n\n")
                raise
            
            if exceptionType == "JSONDecodeError":
                print("\n####################\n CRED FILE EXIST BUT IS CORRUPTED. \n YOU MUST IMPORT A NEW CRED FILE BY IMPORTING SOFTSERVE AND USING \n THE COMMAND softserve.importCreds()\n\n")
                raise






# if __name__ == "__main__":
#     cl = CredLoader()
#     print("Wah")

#     cl.importCreds()
#     credDict = cl.loadCreds()
#     print(credDict)