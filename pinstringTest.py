

def psc(pinString):
    if len(pinString) == 2:
        if pinString[0].isalpha() and pinString[1].isdigit():
            print("Seems legit")
            pinsPerPort = 5
            chanNum = (ord(pinString[0].lower()) - ord("a")) * pinsPerPort + int(pinString[1])

            return chanNum