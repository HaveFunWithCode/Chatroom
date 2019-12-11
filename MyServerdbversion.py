import datetime
import socket

from utilities import color_message
from utilities import message_prefix
from utilities import loger
from DbHandler import DbHandler
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

        self.clients_sessions={}

        #init database

        self.dbinstance=DbHandler()
        self.dbinstance.db_init_tables()







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
        try:
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
                        client_socket.send(bytes('welcom...Enter your username: ', "UTF-8"))

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
                            print(
                                color_message.YELLOW + "{0} left the room".format(s.getpeername()) + color_message.ENDC)

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
                                        self.dbinstance.user_alter_status(self.clients_sessions[target]['uname'], 1)
                                        del self.clients_sessions[target]['pv']
                                    except KeyError:
                                        print(KeyError)
                                        print("error")
                            # if s have someone in pv remove it
                            self.dbinstance.user_alter_status(self.clients_sessions[s]['uname'],0)

                            del self.clients_sessions[s]
                            # remove user from room
                            self.input_sockets.remove(s)
                            s.close()

                for s in self.exceptional:
                    loger('log.txt', '{0} had problem in connection'.format(s))
                    self.input_sockets.remove(s)
                    del self.clients_sessions[s]
                    s.close()
        except Exception as ex:
            # set all user status offlin
            self.dbinstance.user_alter_status_forall_tooffline()

    def find_client(self,username):
        for k in self.clients_sessions:
            if self.clients_sessions[k]['uname'] == username:
                return k
        return None
    def message_handler(self, source,message):
        '''
        message: username for entrance(|
        information for register|
        request someone to start private chat|
        private message|
        broadcast message|

        '''





        if 'uname' not in self.clients_sessions[source]:
            if message.startswith("info:"):

                # register
                infos =str(message)[5:].split(',')
                if len(infos)!=4:
                    source.send(bytes('your format is wrong :/ try again !', "utf-8"))

                else:
                    result = self.dbinstance.user_register([str(param).strip() for param in infos]+[1])
                    if result:
                        username = infos[0]
                        self.clients_sessions[source]['uname'] = username
                        self.dbinstance.user_alter_status(username=username, staus=1)
                        source.send(
                            bytes('--------------welcome to chatroom {0} !----------------'.format(username), "UTF-8"))
                        for client in self.input_sockets:
                            if client != self.server_socket and client != source and 'uname' in self.clients_sessions[client]:
                                client.send(bytes(color_message.OKGREEN + "----{0} enter the room----".format(
                                    self.clients_sessions[source]['uname']) + color_message.ENDC, "utf-8"))
                    else:
                        source.send(bytes('something wrong is with server :/ try again !', "utf-8"))
            else:

                username=message
                userstatus = self.dbinstance.user_checkstatus(username)
                if int(userstatus)==-1:


                    # user should register in server
                    source.send(bytes("Your are not register your information yet!\n"
                                      " Enter your in following format: \n"
                                      "info: username , age, gender(0:male  1:female), country ","utf-8"))
                elif int(userstatus)==0:
                    self.clients_sessions[source]['uname'] = username
                    self.dbinstance.user_alter_status(username=username,staus=1)
                    source.send(bytes('--------------welcome to chatroom {0} !----------------'.format(message), "UTF-8"))
                    for client in self.input_sockets:
                        if client != self.server_socket and client != source:
                            client.send(bytes(color_message.OKGREEN + "----{0} enter the room----".format(
                                self.clients_sessions[source]['uname']) + color_message.ENDC, "utf-8"))

                elif int(userstatus)==-2:
                    print('connection error')


        else:
            # situation 2: request someone to start private chat
            if message.startswith('call:'):


                target_uname = message[5:]
                # 0: offline | 1:online | 2: busy  |   -1 no such username  |-2 dbconnection erro
                target_status=self.dbinstance.user_checkstatus(target_uname)
                if target_status == 1:
                    target_client = self.find_client(target_uname)
                    if target_client != None:
                        if target_client != source:


                            if 'pv' not in self.clients_sessions[target_client]:
                                self.clients_sessions[target_client]['pv'] = source
                                self.clients_sessions[source]['pv'] = target_client
                                # change user status in db
                                result=self.dbinstance.user_alter_status(username=target_uname,staus=2)
                                result=self.dbinstance.user_alter_status(username=self.clients_sessions[source]['uname'],staus=2)
                                if not result:
                                    print("server error in alter status")
                                    loger("log.txt","server error in alter status")
                                target_client.send(
                                    bytes("call:{0}".format(self.clients_sessions[source]['uname']), "UTF-8"))
                                # TODO: bug
                                try:
                                    source.send(bytes("*-------------{0}-------------*".format(target_uname), "utf-8"))
                                except Exception as ex:
                                    print(ex)
                            else:
                                source.send(bytes("{0} is busy!".format(target_uname), "utf-8"))
                        else:
                            source.send(
                                bytes("{0} is yourself!you can not chat with yourself!!".format(target_uname), "utf-8"))
                    else:
                        source.send(bytes("server erorr happened.", "UTF-8"))
                        print("server erorr.")

                elif target_status==2:
                    source.send(bytes("{0} is busy!".format(target_uname), "utf-8"))
                elif target_status==0:
                    source.send(bytes("{0} is offline!".format(target_uname), "utf-8"))
                elif target_status==-1:
                    source.send(bytes("This username have not registered yet.", "utf-8"))
                elif target_status==-2:
                    source.send(bytes("server erorr happened.", "UTF-8"))
                    print("server error in check status")

            elif message=="exit()":
                if 'pv' in self.clients_sessions[source]:
                    partner=self.clients_sessions[source]['pv']
                    # alter user status in database
                    self.dbinstance.user_alter_status(username=self.clients_sessions[source]['uname'],staus=1)
                    self.dbinstance.user_alter_status(username=self.clients_sessions[partner]['uname'],staus=1)

                    del self.clients_sessions[partner]['pv']
                    del self.clients_sessions[source]['pv']
                    partner.send(bytes("*-------------{0} exit the pv-------------*".format(self.clients_sessions[source]['uname']),"utf-8"))
                    source.send(bytes("*-------------end of private chat-------------*","utf-8"))
            elif message=="whio()":
                # TODO: handle with database later
                online_users=["{0}:{1}\n".format(self.clients_sessions[client]['uname'], "busy!" if "pv" in self.clients_sessions[client] else "free") for client in self.clients_sessions]
                source.send(bytes('\n'.join(online_users)+30*"*","utf-8"))
            else:
                now = datetime.datetime.now()
                formated_message = message_prefix.format(now.strftime("%Y-%m-%d %H:%M:%S"),
                                                str(self.clients_sessions[source]['uname']), message)
                # # check this message is pv or broadcast
                # situation 3: private message

                if 'pv' in self.clients_sessions[source]:
                    target_client = self.clients_sessions[source]['pv']
                    target_client.send(bytes(formated_message, "utf-8"))
                # save message in db
                    self.dbinstance.chat_insert_single(self.clients_sessions[source]['uname'],
                                                        self.clients_sessions[target_client]['uname'],
                                                        str(now),
                                                        message)
                # situation 4:  broadcast message
                else:


                    # send message to all except server and the people who are talking in pv
                    for client in self.input_sockets:
                        if client != self.server_socket and client != source \
                                and 'pv' not in self.clients_sessions[client] \
                                and 'uname' in self.clients_sessions[client]:
                            client.send(bytes(formated_message, "utf-8"))


if __name__ == "__main__":

    server=ChatServer('192.168.43.65',9001,100)
    server.run()

















