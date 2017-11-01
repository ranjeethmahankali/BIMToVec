import socket
from reader_model import *

INCOMING_PORT=5006
HOST = "127.0.0.1"
OUTGOING_PORT = 5007

def ListenAndReturnData():
    incomingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    incomingSocket.bind((HOST, INCOMING_PORT))

    incomingSocket.listen(5)
    # while True:
    print("Now listening for the revit client...")
    client, addr = incomingSocket.accept()
    print("Connection established to {}".format(addr))
    data = client.recv(1024)
    client.close()
    incomingSocket.close()
    return data.decode("ascii")

def SendData(strData):
    outgoingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    outgoingSocket.connect((HOST, OUTGOING_PORT))
    outgoingSocket.send(bytes(strData,"ascii"))
    outgoingSocket.close()

if __name__ == "__main__":
    msg = ListenAndReturnData()
    print("received: %s"%msg)
    SendData("I am the python server, here for your tensorflow needs.")