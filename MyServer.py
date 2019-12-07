import datetime
import select
import socket


# TODO: add loger
# TODO: when someone left do not repeat the message
# TODO: when someone Enter the room should not print the name in rooms
# TODO: check duplicate username when someone enter
# TODO: exit from pv chat do not exit from chatroom
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
IP='192.168.1.141'
PORT=9027
print (color_message.BOLD + color_message.OKBLUE + 'starting up on %s port %s' % (IP, PORT) + color_message.ENDC)
server_socket.bind((IP, PORT))

server_socket.listen(5)

# Sockets from which we expect to read
input_sockets = [server_socket]

# Sockets to which we expect to write
outputs = [ ]


# save session for each client in the format of a Dict('uname','privatechat','chatroom_message',target)
# target :(if 'privatechat' have something in it target =privatechat else send message to all)
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
while input_sockets:
    # print("awaiting for the next event")
    readble, writable, exceptional=select.select(input_sockets, outputs, input_sockets)
    for s in readble:
        if s is server_socket:
            client_socket, client_address=s.accept()
            print(color_message.OKGREEN + "{0} enter the room...".format(client_address) + color_message.ENDC)
            client_socket.setblocking(0)
            input_sockets.append(client_socket)
            client_socket.send(bytes('welcom...Enter your username',"UTF-8"))
            clients_sessions[client_socket]={}


        else:
            message=s.recv(1024)

            if message:
                if not str(message.decode("UTF-8")).startswith('call:'):
                    # someone send a message
                    # send user enter the room message to someone
                    if 'uname' not in clients_sessions[s]:
                        clients_sessions[s]['uname'] = message.decode("UTF-8")
                        for client in input_sockets:
                            if client != server_socket and client != s:
                                client.send(bytes(color_message.OKGREEN + "{0} enter the room...".format(
                                    clients_sessions[s]['uname']) + color_message.ENDC, "utf-8"))

                    now = datetime.datetime.now()
                    message = message_prefix.format(now.strftime("%Y-%m-%d %H:%M:%S"),
                                                    str(clients_sessions[s]['uname']), message.decode("utf-8"))

                    for r in readble:
                        if r not in outputs:
                            outputs.append(r)

                    # check this message is pv or broadcast
                    if 'pv' in clients_sessions[s]:
                        target = clients_sessions[s]['pv']
                        target.send(bytes(message, "utf-8"))
                    else:
                        # send message to all except server and the people who are talking in pv
                        for client in input_sockets:
                            if client != server_socket and client != s and 'pv' not in clients_sessions[client]:
                                client.send(bytes(message, "utf-8"))
                else:
                    # someone is starting pv with someone

                    uname = message.decode("UTF-8")[5:]
                    user = find_client(clients_sessions, uname)
                    if user != None:
                        if user !=s:
                            if 'pv' not in clients_sessions[user]:
                                clients_sessions[user]['pv'] = s
                                clients_sessions[s]['pv'] = user
                                # open subprocess for both
                                user.send(bytes("call:{0}".format(clients_sessions[s]['uname']), "UTF-8"))
                                # TODO: bug
                                try:
                                    s.send(bytes("*-----------------{0}----------------*".format(uname),"utf-8"))
                                except Exception as ex:
                                    print(ex)
                            else:
                                s.send(bytes("{0} is busy!".format(uname),"utf-8"))
                        else:
                            s.send(bytes("{0} is yourself!you can not chat with yourself!!".format(uname),"utf-8"))
                    else:
                        s.send(bytes("Wrong username!", "UTF-8"))
                    # find user


            # A readable socket without data available is from a client that
            # has disconnected, and the stream is ready to be closed.
            else:
                print(color_message.YELLOW + "{0} left the room".format(s.getpeername()) + color_message.ENDC)
                # TODO: remove user pv variable

                # tell others someone left the room
                for client in input_sockets:
                    if 'pv' not in clients_sessions[s]:
                        if client != server_socket and client != s:
                            client.send(bytes(color_message.RED + "{0} left the room...".format(
                                clients_sessions[s]['uname']) + color_message.ENDC, "utf-8"))
                    else:
                        target = clients_sessions[s]['pv']
                        target.send(bytes(color_message.RED + "------{0} left the pv-------".format(
                            clients_sessions[s]['uname']) + color_message.ENDC, "utf-8"))
                        try:
                            del clients_sessions[target]['pv']
                        except KeyError:
                            print("error")
                # if s have someone in pv remove it

                del clients_sessions[s]

                if s in outputs:
                    outputs.remove(s)
                input_sockets.remove(s)
                # del message_queues[s]
                s.close()



    for s in exceptional:
        if s in outputs:
            outputs.remove(s)

        input_sockets.remove(s)
        s.close()




