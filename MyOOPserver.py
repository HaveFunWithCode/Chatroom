import datetime
import socket

from utilities import color_message
from utilities import message_prefix
from utilities import loger
import select


# TODO:bug check duplicate username when someone enter
# TODO: bug left the room close all connection(some situation)

class ChatServer(object):

    def __init__(self,IP,PORT,server_capacity):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.server_socket.setblocking(0)
        print(color_message.BOLD + color_message.OKBLUE + 'server is starting up on %s port %s....' % (IP, PORT) + color_message.ENDC)
        self.server_socket.bind((IP,PORT))
        self.server_socket.listen(server_capacity)
        self.input_sockets=[self.server_socket]
        # TODO: check is it needed?
        # self.outputs=[]
        self.clients_sessions={}

    def check_duplicated_user(self,username):
        is_duplicated = False
        for client in self.clients_sessions:
            if 'uname' in self.clients_sessions[client] and \
                    self.clients_sessions[client]['uname'] == username:
                is_duplicated = True
                break
        return is_duplicated

    # # TODO: has bug should fix in next stable version
    # def authenticate_user(self,client_socket):
    #     while client_socket not in self.clients_sessions:
    #         username = client_socket.recv(1024)
    #         if not self.check_duplicated_user(username):
    #
    #             # do if username is not repeatative
    #             self.input_sockets.append(client_socket)
    #             self.clients_sessions[client_socket] = {}
    #             client_socket.send(bytes('--------------welcome to chatroom!----------------', "UTF-8"))
    #             break
    #         else:
    #             client_socket.send(bytes('your username is duplicated!', "UTF-8"))
    def run(self):
        while self.input_sockets:
            self.readble, _, self.exceptional = select.select(
                self.input_sockets, [], self.input_sockets)
            for s in self.readble:
                if s is self.server_socket:
                    client_socket, client_address = s.accept()
                    print(color_message.OKGREEN + "{0} enter the server...".format(
                        client_address) + color_message.ENDC)
                    client_socket.setblocking(0)
                    self.input_sockets.append(client_socket)
                    self.clients_sessions[client_socket] = {}
                    client_socket.send(bytes('welcom...Enter your username', "UTF-8"))

                    # thread_auth=threading.Thread(target=self.authenticate_user,args=[client_socket])
                    # thread_auth.start()


                else:
                    try:
                        message = s.recv(1024).decode("UTF-8")
                    except Exception as a:
                        print(a)
                    if message:
                        self.message_handler(s, message)
                    # A readable socket without data available is from a client that
                    # has disconnected, and the stream is ready to be closed.
                    else:
                        print(color_message.YELLOW + "{0} left the room".format(s.getpeername()) + color_message.ENDC)

                        # ----------------------------------------
                        # tell others someone left the room
                        for client in self.input_sockets:

                            if client in self.clients_sessions and 'pv' not in self.clients_sessions[client]:
                                if client != self.server_socket and client != s:
                                    client.send(bytes(color_message.RED + "{0} left the room...".format(
                                        self.clients_sessions[s]['uname']) + color_message.ENDC, "utf-8"))
                            else:
                                try:
                                    target = self.clients_sessions[s]['pv']
                                    target.send(bytes(color_message.RED + "------{0} left the pv-------".format(
                                        self.clients_sessions[s]['uname']) + color_message.ENDC, "utf-8"))

                                    del self.clients_sessions[target]['pv']
                                except KeyError:

                                    print("error")
                        # if s have someone in pv remove it

                        del self.clients_sessions[s]
                        # remove user from room
                        self.input_sockets.remove(s)
                        s.close()

            for s in self.exceptional:
                loger('log.txt', '{0} had problem in connection'.format(s))
                self.input_sockets.remove(s)
                del self.clients_sessions[s]
                s.close()
    def find_client(self,username):
        for k in self.clients_sessions:
            if self.clients_sessions[k]['uname'] == username:
                return k
        return None
    def message_handler(self, source,message):
        '''
        message: username|
        request someone to start private chat|
        private message|
        broadcast message|

        '''

        #situation 1 : message: username
        if 'uname' not in self.clients_sessions[source]:


            self.clients_sessions[source]['uname'] = message
            source.send(bytes('--------------welcome to chatroom {0} !----------------'.format(message), "UTF-8"))
            for client in self.input_sockets:
                if client != self.server_socket and client != source:
                    client.send(bytes(color_message.OKGREEN + "{0} enter the room...".format(
                        self.clients_sessions[source]['uname']) + color_message.ENDC, "utf-8"))
            # TODO: check for duplicated
            # if not self.check_duplicated_user(message):
            #     self.input_sockets.append(source)
            #     self.clients_sessions[source] = {}
            #     self.clients_sessions[source]['uname'] = message
            #     source.send(bytes('--------------welcome to chatroom {0} !----------------'.format(message), "UTF-8"))
            #     # source.send(bytes("your username set as :{0}".format(message),"UTF-8"))
            #     for client in self.input_sockets:
            #         if client != self.server_socket and client != source:
            #             client.send(bytes(color_message.OKGREEN + "{0} enter the room...".format(
            #                 self.clients_sessions[source]['uname']) + color_message.ENDC, "utf-8"))
            # else:
            #     source.send(bytes('your username is duplicated!', "UTF-8"))




        else:
            # situation 2: request someone to start private chat
            if message.startswith('call:'):


                target_uname = message[5:]
                target_client = self.find_client(target_uname)
                if target_client != None:
                    if target_client != source:
                        if 'pv' not in self.clients_sessions[target_client]:
                            self.clients_sessions[target_client]['pv'] = source
                            self.clients_sessions[source]['pv'] = target_client
                            target_client.send(bytes("call:{0}".format(self.clients_sessions[source]['uname']), "UTF-8"))
                            # TODO: bug
                            try:
                                source.send(bytes("*-------------{0}-------------*".format(target_uname), "utf-8"))
                            except Exception as ex:
                                print(ex)
                        else:
                            source.send(bytes("{0} is busy!".format(target_uname), "utf-8"))
                    else:
                        source.send(bytes("{0} is yourself!you can not chat with yourself!!".format(target_uname), "utf-8"))
                else:
                    source.send(bytes("Wrong username!", "UTF-8"))
            elif message=="exit()":
                if 'pv' in self.clients_sessions[source]:
                    partner=self.clients_sessions[source]['pv']
                    del self.clients_sessions[partner]['pv']
                    del self.clients_sessions[source]['pv']
                    partner.send(bytes("*-------------{0} exit the pv-------------*".format(self.clients_sessions[source]['uname']),"utf-8"))
                    source.send(bytes("*-------------end of private chat-------------*","utf-8"))
            else:
                now = datetime.datetime.now()
                message = message_prefix.format(now.strftime("%Y-%m-%d %H:%M:%S"),
                                                str(self.clients_sessions[source]['uname']), message)
                # # check this message is pv or broadcast
                # situation 3: private message
                if 'pv' in self.clients_sessions[source]:
                    target_client = self.clients_sessions[source]['pv']
                    target_client.send(bytes(message, "utf-8"))
                # situation 4:  broadcast message
                else:

                    # send message to all except server and the people who are talking in pv
                    for client in self.input_sockets:
                        if client != self.server_socket and client != source \
                                and 'pv' not in self.clients_sessions[client]:
                            client.send(bytes(message, "utf-8"))


if __name__ == "__main__":

    server=ChatServer('192.168.43.65',9001,100)
    server.run()

















