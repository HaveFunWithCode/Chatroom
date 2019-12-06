import datetime
import select
import socket
import queue
import sys
import time


class color_message:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# ###########################
# #####preparing server######
# ###########################
# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(0)

# Bind the socket to the port
IP='192.168.43.65'
PORT=9021
print (color_message.BOLD + color_message.OKBLUE + 'starting up on %s port %s' % (IP, PORT) + color_message.ENDC)
server_socket.bind((IP, PORT))

server_socket.listen(5)

# Sockets from which we expect to read
inputs = [server_socket]

# Sockets to which we expect to write
outputs = [ ]

# Outgoing message queues (socket:Queue)
message_queues={}
# save session for each client in the format of a Dict('uname','privatechat','chatroom_message'
clients_sessions={}

def find_client(clients_sessions,name):
    for k in clients_sessions:
        if clients_sessions[k]['uname']==name:
            return k
    return None



# ###########################
# #####  start app     ######
# ###########################
message_prefix='({}){}: {}'
while inputs:
    # print("awaiting for the next event")
    readble, writable, exceptional=select.select(inputs, outputs, inputs)
    for s in readble:
        if s is server_socket:
            client_socket, client_address=s.accept()
            print(color_message.OKGREEN + "{0} enter the room...".format(client_address) + color_message.ENDC)
            client_socket.setblocking(0)
            inputs.append(client_socket)
            client_socket.send(bytes('welcom...Enter your username',"UTF-8"))
            # Give the connection a Queue for data we want to sent to it
            message_queues[client_socket]=queue.Queue()
            clients_sessions[client_socket]={}


        else:
            message=s.recv(1024)

            if message:
                if not str(message.decode("UTF-8")).startswith('call:') :
                    if 'uname' not in clients_sessions[s]:
                        clients_sessions[s]['uname'] = message.decode("UTF-8")
                        for client in inputs:
                            if client != server_socket and client != s:
                                client.send(bytes(color_message.OKGREEN + "{0} enter the room...".format(clients_sessions[s]['uname']) + color_message.ENDC, "utf-8"))


                    now = datetime.datetime.now()
                    message=message_prefix.format(now.strftime("%Y-%m-%d %H:%M:%S"),str(clients_sessions[s]['uname']),message.decode("utf-8"))
                    # message_queues[s].put(message)
                    # add new messages to all user queues
                    for key in message_queues.keys():
                        message_queues[key].put(message + '\n')
                    # if s not in outputs:
                    #     outputs.append(s)
                    for r in readble:
                        if r not in outputs:
                            outputs.append(r)

                    for client in inputs :
                        if client!= server_socket and client!=s:
                            client.send(bytes(message,"utf-8"))
                else:
                    uname=message.decode("UTF-8")[5:]
                    user=find_client(clients_sessions,uname)
                    if user != None:
                        if 'pv' not in clients_sessions[user]:
                            clients_sessions[user]['pv']=s
                            clients_sessions[s]['pv']=user
                            # open subprocess for both
                            user.send(bytes("call:{0}".format(clients_sessions[s]['uname']),"UTF-8"))
                        else:
                            s.send(bytes("{0} is busy!".format(uname)))
                    else:
                        s.send(bytes("Wrong username!","UTF-8"))
                    # find user


            # A readable socket without data available is from a client that
            # has disconnected, and the stream is ready to be closed.
            else:
                print(color_message.YELLOW + "{0} left the room".format(s.getpeername()) + color_message.ENDC)
                # TODO: remove user pv variable
                # clients_sessions[user]['pv'] = s
                # clients_sessions[s]['pv'] = user
                # tell others someone left the room
                for client in inputs:
                    if client != server_socket and client != s:
                        client.send(bytes(color_message.RED + "{0} left the room...".format(
                            clients_sessions[s]['uname']) + color_message.ENDC, "utf-8"))

                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                del message_queues[s]
                s.close()


    # for s in writable:
    #     try:
    #         next_msg=message_queues[s].get_nowait()
    #
    #         s.send(bytes(next_msg,"utf-8"))
    #     except queue.Empty:
    #         # print("output queue for {0} is empty".format(s.getpeername()))
    #         # TODO: find the reason why this line is needed
    #         outputs.remove(s)
    for s in exceptional:
        if s in outputs:
            outputs.remove(s)

        inputs.remove(s)
        del message_queues[s]
        s.close()




