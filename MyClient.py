import socket
import sys
import threading

IP='192.168.43.65'
PORT=9015

client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)

def send_message():
    while True:
        msg=input('->')
        if msg:
            client_socket.send(bytes(msg,"utf-8"))

# what is the size of chunck
# message=client_socket.recv(1024)
# print(message.decode('utf-8'))
t1=threading.Thread(target=send_message)
t1.start()
while True:
    try:
        while True:
            message=client_socket.recv(1024)
            if not message:
                print('connection close!')
                sys.exit()
            print(message.decode("utf-8"))
    except IOError:
        pass
    # print(message.decode("utf-8"))
    # msg=input('->')
    # client_socket.send(bytes(msg,"utf-8"))





