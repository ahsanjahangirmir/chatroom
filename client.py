'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util
import time

input_checker = ["msg", "list", "file", "help", "quit"]

class Client:
    
    
    def __init__(self, username, dest, port):
        
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(None)
        self.name = username
        self.connection_status = True; # bool variable defined to indicate connection status and control the flow of both loops
        self.sock.connect((self.server_addr, self.server_port)) 
        
        # DO NOT uncomment this code while running tests. Only uncomment for beauty while manual testing to check file sharing. Thank you!
        
        # print("Joining server", end="")
        # for i in range(3):
        #     print(".", end="", flush=True)
        #     time.sleep(0.5)
        # print("")
        

    def start(self):
        
        join_message = util.make_message("join", 1, self.name) # create type 1 join message
        self.sock.send(join_message.encode('utf-8')) # starting by sending the server a JOIN message.

        while self.connection_status:
            
            user_input = input() #wait for user input
            
            if (user_input.split()[0] not in input_checker): #check if user input matches valid list of commands
                print("incorrect userinput format") 
            
            else:
            
                if user_input == "help":
                    
                    print('Need help? We got you covered homie. Please check the following list of possible inputs and their functions: \n')
                    print('1) Request a list of all the usernames of clients connected to the application-server:' + '\033[1m' + 'list' + '\033[0m' + '\n')
                    print('2) Send a message from this client to other clients connected to the server:' + '\033[1m' + 'msg <number_of_users> <username1> <username2> ... <message>' + '\033[0m' + '\n')
                    print('3) Send a file to other clients connected to the server:' + '\033[1m' + 'file <number_of_users> <username1> <username2> ... <file_name>' + '\033[0m' + '\n')
                    print('4) Print all the possible user inputs and their format:' + '\033[1m' + 'help' + '\033[0m' + '\n')
                    print('5) Disconnect from the application server:' + '\033[1m' + 'quit' + '\033[0m' + '\n')
                
                elif user_input == "list":
                    
                    request_message = "request_users_list"
                    self.sock.send(request_message.encode("utf-8")) # encode and send list request to server
                
                elif user_input == "quit":
                    
                    disconnect_message = util.make_message("disconnect", 1, self.name) # create disconnect message
                    self.sock.send(disconnect_message.encode("utf-8")) # encode and send disconnect message to server 
                    print("quitting")
                    self.connection_status = False # collapse threads (Main Thread and daemon thread T) 

                elif user_input.split()[0] == "msg":

                    input_splitter = user_input.split() # split words from userinput into a list.
                    number_of_recipients = int(input_splitter[1]) 
                    send_message = "send_message" + " " + " ".join(input_splitter[1:]) # create send_message protocol message
                    self.sock.send(send_message.encode('utf-8')) # encode and send message to server

                elif user_input.split()[0] == "file":
                    
                    input_splitter = user_input.split() # split words from userinput into a list.
                    number_of_recipients = int(input_splitter[1]) 
                
                    try:
                        f_name = input_splitter[number_of_recipients + 2] # store name of file using list indexing
                        f = open(f_name, 'r') # open file for reading
                        f_contents = f.read() # read file contents and store as a string in f_contents
                        f.close() # close file
                        send_file = "send_file" + " " + " ".join(input_splitter[1:]) + " " + f_contents # create message to send to server
                        self.sock.send(send_file.encode('utf-8')) # send encoded message to server with protocol added
                
                    except:
                        print("Error: Unable to send file.")

    def receive_handler(self):

        while self.connection_status:
            
            msg = self.sock.recv(4096).decode('utf-8') # receive messages from server with a 4096 byte buffer

            msg_splitter = msg.split() # split message from server and store in a list

            if len(msg) > 0:
                
                if msg_splitter[0] == "response_users_list": 
                    
                    response_list = "list: " + " ".join(msg_splitter[1:]) # create print statement according to output format
                    print(response_list) # print list of users received from server (after removing protocol)
                
                elif msg_splitter[0] == "forward_file": 
                    
                    f_name = self.name + "_" + msg_splitter[2] # create name of file
                    sender_name = msg_splitter[1]
                    f_contents = " ".join(msg_splitter[3:]) 
                    f = open(f_name, "w") # create a file in current dir with name f_name
                    f.write(f_contents) # write contents to file
                    f.close() # close file
                    print(f"file: {sender_name}: {str(msg_splitter[2])}") # prompt user

                elif msg_splitter[0] == "forward_message": 
                    
                    print(' '.join(msg_splitter[1:])) # print received message to user 

                elif msg == "err_unknown_message":
                    
                    print("disconnected: server received an unknown command")
                    self.connection_status = False # collapse threads (Main Thread and daemon thread T)

                elif msg == "err_server_full":
                    
                    print("disconnected: server full")
                    self.connection_status = False # collapse threads (Main Thread and daemon thread T)

                elif msg == "err_username_unavailable":
                    
                    print("disconnected: username not available")
                    self.connection_status = False # collapse threads (Main Thread and daemon thread T)

###

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a", ["user=", "port=", "address="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
