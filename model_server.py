import socket
from embeddingCalc import *

INCOMING_PORT=5006
HOST = "127.0.0.1"
OUTGOING_PORT = 5007

INCOMING_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
INCOMING_SOCKET.bind((HOST, INCOMING_PORT))
INCOMING_SOCKET.listen(1)

def StopServer():
    INCOMING_SOCKET.close()
    quit()

def ListenAndReturnData():
    global INCOMING_SOCKET
    INCOMING_SOCKET.listen(5)
    # while True:
    # print("Now listening for the revit client...")
    client, addr = INCOMING_SOCKET.accept()
    # print("Connection established to {}".format(addr))
    data = client.recv(1024)
    client.close()
    return data.decode("ascii")

def SendData(strData):
    OUTGOING_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    OUTGOING_SOCKET.connect((HOST, OUTGOING_PORT))
    OUTGOING_SOCKET.send(bytes(strData,"ascii"))
    OUTGOING_SOCKET.close()

OUTGOING_TOKEN = {
    "error": "error_ec995d88-ee8e-4288-a2da-3c93d231992b"
}

INCOMING_TOKEN = {
    "stop_server_498994a4-24a1-4496-9a41-3e6f907d0ffa": StopServer
}

def ProcessInput(data):
    if data in INCOMING_TOKEN:
        INCOMING_TOKEN[data]()
        return

    elemWords = data.split("\n")
    words = []
    for elem in elemWords:
        if(len(elemWords) == 0):
            continue
        words.append(elem.split(" "))

    if len(words) == 0:
        return "None"

    words, oddOne = oddOneOut(words)
    if len(words) == 0:
        return "None"

    names = [[w for w in w_set if "ifc" in w] for w_set in words]
    ifcNames = [names[i][0] if len(names[i]) == 0 else words[i][0] for i in range(len(names))]
    return "["+ifcNames[oddOne]+"] of \n"+ ", ".join(ifcNames)

# this is the main loop
if __name__ == "__main__":
    print("Server started...")
    while True:
        try:
            msg = ListenAndReturnData()
            print("received: %s"%msg)
            response = ProcessInput(msg)
            SendData(response)
        except Exception as e:
            SendData(OUTGOING_TOKEN["error"])
            SendData("Something went wrong: \n"+str(e))
