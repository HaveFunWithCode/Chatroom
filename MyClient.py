import socket
import sys
import threading

class ChatClient(object):
    def __init__(self,IP,PORT):
        self.IP=IP
        self.PORT=PORT
        self.client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_socket.connect((IP,PORT))
        self.client_socket.setblocking(False)

    def send_message(self):
        print('chatroom Manual:'
              '\n1) for private message to a username, write: call:username \n'
              '2) for exit the private chat please write: exit()\n3) ------------------------------------\n')
        while True:
            msg=input('->')
            if msg:
                self.client_socket.send(bytes(msg,"utf-8"))


    def run(self):
        t1 = threading.Thread(target=self.send_message)
        t1.start()

        while True:
            try:
                while True:
                    message = self.client_socket.recv(1024)
                    if not message:
                        print('connection close!')
                        sys.exit()
                    if message.decode("utf-8").startswith("call:"):
                        pvname = message.decode("utf-8")[5:]
                        print("*-----------------{0}----------------*".format(pvname))

                    else:
                        print(message.decode("utf-8"))
            except IOError:
                pass

if __name__=='__main__':
    client=ChatClient('192.168.43.65',9001)
    client.run()






