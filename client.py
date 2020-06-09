import socket
import threading
import getpass
import argparse
import re
from Variables import States, Client_info


class thread_recv_sound(threading.Thread):
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event() #For Stopping Thread
        self.socket = client_socket

    def run(self):
        while(self._stop_event.is_set() == False):
            recv_data = self.socket.recv(1024)
            '''
            Processing Data....

            Todo:

            '''
    def stop(self):
        self._stop_event.set()

def Sign_up(client):
    client.print_info()
    send_data = States.sign_up
    send_raw_data = send_data.encode("utf-8")
    client.connect.sendall(send_raw_data)
    recv_raw_data = client.connect.recv(1024)
    recv_data = recv_raw_data.decode("utf-8")
    state, msg = recv_data.split(":")
#    if state != States.sign_up:
#        print("Somethings went wrong while sign up")
#        return
    
    print(recv_data, 'Now sign up:')
    while True:
       #===========Loggin============
        Username = input('Please enter your name: ')
        Password = getpass.getpass('Password: ')
        CheckPassword = getpass.getpass('Password again: ')
        while Password != CheckPassword or not re.match("^[A-Za-z0-9_]+$", Username) or not re.match("^[A-Za-z0-9_]+$", Password):
            if not re.match("^[A-Za-z0-9_]+$", Username) or not re.match("^[A-Za-z0-9_]+$", Password):
                print("Username or Password contains invalid characters, please enter again.")
                print("(letters, numbers and underscores only.)")
                Username = input('Please enter your name: ')
            else:
                print("Passwords are not same, please enter again.")
            # maybe we can add some machanism for client who don't want to keep signing up
            Password = getpass.getpass('Password: ')
            CheckPassword = getpass.getpass('Password again: ')
            
        send_data = Username + ',' + Password
        send_raw_data = send_data.encode('utf-8')
        client.connect.sendall(send_raw_data)
        recv_raw_data = client.connect.recv(1024)
        recv_data = recv_raw_data.decode("utf-8")
        state, msg = recv_data.split(":")
        if state == States.initial:
            print("Sign up successfully!!")
            return States.initial
        elif state == States.sign_up:
            print("The account has been used.")    

def Login(client):
    client.print_info()
    send_data = States.login
    send_raw_data = send_data.encode("utf-8")
    client.connect.sendall(send_raw_data)
    
    recv_raw_data = client.connect.recv(1024)
    recv_data = recv_raw_data.decode("utf-8")
    print(recv_data, 'Now login:')
    while True:
       #===========Loggin============
        Username = input('Please enter your username: ')
        Password = input('Please enter your password: ')
        send_data = Username + ',' + Password
        send_raw_data = send_data.encode('utf-8')
        print(send_data)
        client.connect.sendall(send_raw_data)
        recv_raw_data = client.connect.recv(1024)
        recv_data = recv_raw_data.decode("utf-8")
        print(send_data, recv_data)
        state, msg = recv_data.split(":")
       ############################################
        if state == States.waiting_for_talk:
            print("Login successfully!!")
            return States.waiting_for_talk
        else:
            print("Username or password isn't correct.")



if __name__ == "__main__":
    #====== arg parsing =========
    parser = argparse.ArgumentParser()
    parser.add_argument("IP", type=str, help="IP of the server")
    parser.add_argument("port", type=int, help="port of the IP")
    args = parser.parse_args()
    print(args.IP, args.port)
    #======Connect to Server=====
    IP = args.IP
    port = args.port
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = Client_info(connection, IP, port)
    client.connect.connect((IP, port)) #Server IP & Port
    # Before login
    # Check operation
    recv_raw_data = client.connect.recv(1024)
    recv_data = recv_raw_data.decode("utf-8")
    print("Welcome Data:", recv_data)
    state = recv_data.split(":")[0]
    while True:
        #TODO: make the initial operation into a function and make everything into this loop
        if state == States.initial:
            operation = input("Please input the operation:('sign up'/'login'/'quit'):")
            if operation == "quit":
                print("Goodbye~")
                client.connect.sendall(operation.encode("utf-8"))
                client.connect.close()
                client.states = "quit"
                break
            elif operation == "sign up":
                state = Sign_up(client)
            elif operation == "login":
                state = Login(client)
            else:
                print("Unknown command")

        elif state == States.waiting_for_talk:
            print("Strat to talk")
            ###########TODO###########
            #     START TO TALK      #
            ##########################
            break


    #print("Login or Sign up successfully")
    '''
    ##############################################
    #======Create Thread to Recieve msg======
    # start recording
    # Maybe this line can put in the Sign_up or Login
    recv_sound = thread_recv_sound(client)
    recv_sound.start()

    while True:
        key = "" #Input Key
        if(key == ''): #Client quit
            break
        elif(key == ''): #Ask for Mic
            client.sendall(b'REQ')
            data = client.recv(1024)
            if (data == b'MIC_ACK'):
                data = input()#Change this to vocal
                data = data.encode('utf-8')
                clent.sendall(data)
            elif (data == b'MIC_REJ'):
                print('Microphone Reject') #Wait a second
                sleep(1)

    recv_sound.stop()
    recv_sound.join()
    
    client.sendall(b'quit')
    '''
    #client.close()

