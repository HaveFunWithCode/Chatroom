import os
import socket
import sys
import threading
import subprocess

IP='192.168.1.141'
PORT=9022

client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)

def send_message():
    print('for private message to someone, write call:name')
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
            if message.decode("utf-8").startswith("call:"):
                pvname=message[5:]
                # os.system('clear')
                print("*--------------------------------------*")
                print('{0} pv->>'.format(pvname))
            else:
                print(message.decode("utf-8"))
    except IOError:
        pass
    # print(message.decode("utf-8"))
    # msg=input('->')
    # client_socket.send(bytes(msg,"utf-8"))





