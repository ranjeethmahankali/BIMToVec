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

SPECIAL_TOKEN = {
    "stop_server_498994a4-24a1-4496-9a41-3e6f907d0ffa": StopServer
}

def ProcessInput(data):
    if data in SPECIAL_TOKEN:
        SPECIAL_TOKEN[data]()
        return

    words = data.split(" ")
    if len(words) == 0:
        return "None"

    for w in words:
        print(w)

    return oddOneOut(words)

if __name__ == "__main__":
    print("Server started...")
    while True:
        msg = ListenAndReturnData()
        print("received: %s"%msg)
        response = ProcessInput(msg)
        SendData(response)