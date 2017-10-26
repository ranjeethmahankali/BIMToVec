import socket

port=15555
host = "127.0.0.1"
incomingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
incomingSocket.bind((host, port))

incomingSocket.listen(5)
# while True:
client, addr = incomingSocket.accept()
print("Connection established to {}".format(addr))
data = client.recv(1024)
client.close()

msg = data.decode("ascii")
print("message: %s"%msg)


reply = "I am the python server, here for your tensorflow needs."
outgoingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
outgoingSocket.connect(("127.0.0.1", 15556))
outgoingSocket.send(bytes(reply,"ascii"))
outgoingSocket.close()