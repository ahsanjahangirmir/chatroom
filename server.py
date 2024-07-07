'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util
import threading
import time

active_clients_dict = {} #global dictionary to store usernames and conn objects in key-value pairs

class Server:

    def __init__(self, dest, port):   
        
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))

    def client_handler(self, conn, addr): # function to handle messages received from clients

        global active_clients_dict

        this_username = "" # str to store username of client in thread

        while True:     

                msg = conn.recv(4096).decode('utf-8') # recieving messages from client

                msg_splitter = msg.split() # each word from message separated into a list

                if len(msg) > 0:
                    
                    if msg_splitter[0] == "join": # handle join message from client
                    
                        if len(active_clients_dict.keys()) == (util.MAX_NUM_CLIENTS): # conditional to check if server is full
                            
                            conn.send("err_server_full".encode("utf-8")) # error message encoded and sent to client
                            print("disconnected: server full")
                            break
                    
                        elif msg_splitter[1] in active_clients_dict.keys(): # conditional to check for username duplication
                            
                            conn.send("err_username_unavailable".encode("utf-8")) # error message encoded and sent to client
                            print("disconnected: username not available")
                            break
                    
                        else: 
                            
                            print(f"join: {str(msg_splitter[1])}")
                            this_username = str(msg_splitter[1])
                            active_clients_dict[this_username] = conn # username-socket pair appended to dictionary of active clients
                    
                    elif msg == "request_users_list": # handle client request for list of users connected to server
                        
                        sorted_usernames = sorted(active_clients_dict.keys()) # sort usernames in alphabetical order
                        response_users_list = "response_users_list " + " ".join(sorted_usernames) # making message to reply to client
                        conn.send(response_users_list.encode('utf-8')) # response list encoded and sent to client
                        print(f'request_users_list: {this_username}')

                    elif msg_splitter[0] == "disconnect": #handle client request to disconnect from server
                        
                        print(f"disconnected: {this_username}") 
                        del active_clients_dict[this_username] # remove username-socket pair from client dictionary and exit loop
                        break

                    elif msg_splitter[0] == "send_message": 
                        
                        number_of_recipients = int(msg_splitter[1])
                        forward_message = "forward_message msg: " + this_username + ": " + " ".join(msg_splitter[(2 + number_of_recipients):]) # create forwarding message
                        recipient_usernames = list(set(msg_splitter[2:(2 + number_of_recipients)])) # removing duplicate entries of recipients using set notation

                        for username in recipient_usernames:
                            
                            if username in active_clients_dict.keys():
                                
                                recipient_socket = active_clients_dict[username] # retrieve socket (value) using username (key)
                                recipient_socket.send(forward_message.encode('utf-8')) # forward encoded message to recipient client
                                print(f"msg: {this_username}")
                            
                            else:
                                
                                print(f"msg: {this_username} to non-existent user {username}") # recipient username does not exist in client dictionary
                    
                    elif msg_splitter[0] == "send_file":
                        
                        number_of_recipients = int(msg_splitter[1]) # storing number of recipients
                        f_name = str(msg_splitter[number_of_recipients + 2]) # storing name of file
                        f_contents = " ".join(msg_splitter[(number_of_recipients + 3):]) # storing contents of file
                        recipient_usernames = list(set(msg_splitter[2:(2 + number_of_recipients)])) # storing list of recipient names after removing duplicates
                        forward_file = "forward_file " + this_username + " " + f_name + " " + f_contents # creating message to forward file

                        for username in recipient_usernames:
                            
                            print(f"file: {this_username}")
                            
                            if username in active_clients_dict.keys(): # client exists in dictionary
                            
                                recipient_socket = active_clients_dict[username] # retrieve socket (value) using username (key)
                                recipient_socket.send(forward_file.encode('utf-8')) # forward encoded message to recipient client
                            
                            else:
                            
                                print(f"file: {this_username} to non-existent user {username}") # client does not exist in dictionary

                    else: 
                       
                        conn.send("err_unknown_message".encode("utf-8")) # server does not recognize this protocol
                        print(f"disconnected: {this_username} sent unknown command")
                        del active_clients_dict[this_username] # remove client from dictionary using username key and exit loop
                        break

    def start(self):

        # print("Server: Online") # DO NOT uncomment this code while running tests. Only uncomment for beauty while manual testing to check file sharing. Thank you!
        
        self.sock.listen() # listening for connections

        while True:
            conn, addr = self.sock.accept() # blocking
            client_thread = threading.Thread(target=self.client_handler, args=(conn, addr)) #defining thread object for each connection
            client_thread.start() # starting thread object targeting handler function
    
### 

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a", ["port=", "address="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    SERVER = Server(DEST, PORT)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
