import socket

IP='localhost'
PORT=10005



client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_socket.connect((IP,PORT))
# what is the size of chunck 
# message=client_socket.recv(1024)
# print(message.decode('utf-8'))

while True:
    message=client_socket.recv(1024)
    print(message.decode("utf-8"))
    msg=input('->')
    client_socket.send(bytes(msg,"utf-8"))

client_socket.close()


