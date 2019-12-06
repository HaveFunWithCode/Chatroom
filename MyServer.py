import select
import socket
import queue
import sys



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
IP=''
PORT=10005

print (color_message.BOLD + color_message.OKBLUE + 'starting up on %s port %s' % (IP, PORT) + color_message.ENDC)
server_socket.bind((IP, PORT))

server_socket.listen(5)

# Sockets from which we expect to read
inputs = [server_socket]

# Sockets to which we expect to write
outputs = [ ]

# Outgoing message queues (socket:Queue)
message_queues={}
# ###########################
# #####  start app     ######
# ###########################

while inputs:
    # print("awaiting for the next event")
    readble, writable, exceptional=select.select(inputs, outputs, inputs)
    for s in readble:
        if s is server_socket:
            client_socket, client_address=s.accept()
            print(color_message.OKGREEN + "{0} enter the room...".format(client_address) + color_message.ENDC)
            client_socket.setblocking(0)
            inputs.append(client_socket)
            client_socket.send(bytes('welcom...',"UTF-8"))
            # Give the connection a Queue for data we want to sent to it
            message_queues[client_socket]=queue.Queue()

        else:
            message=s.recv(1024)
            if message:
                'from {}: {}'.format(s.getpeername(),message)
                message_queues[s].put(message)
                if s not in outputs:
                    outputs.append(s)

            # A readable socket without data available is from a client that
            # has disconnected, and the stream is ready to be closed.
            else:
                print(color_message.YELLOW + "{0} left the room".format(s.getpeername()) + color_message.ENDC)
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                del message_queues[s]
                s.close()

    for s in writable:
        try:
            next_msg=message_queues[s].get_nowait()

            s.send(next_msg)
        except queue.Empty:
            # print("output queue for {0} is empty".format(s.getpeername()))
            # TODO: find the reason why this line is needed
            outputs.remove(s)
    for s in exceptional:
        if s in outputs:
            outputs.remove(s)

        inputs.remove(s)
        del message_queues[s]
        s.close()




