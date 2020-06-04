import socket
import threading
import getpass
import argparse


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
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, port)) #Server IP & Port
    # Check operation
    operation = input("Please input the operation:('sign up'/'login')")
    if operation == "sign up":
        client.sendall("sign up".encode("utf-8"))
        data = client.recv(1024)
        '''
        while data.decode('utf-8') != 'sign up ACK':
            op = input("Connection error, do you want to sign up again?(y/n)")
            if op == 'y':
                client.sendall("Sign up".encode("utf-8"))
                data = client.recv(1024)
            else:
                client.sendall(b'quit')
                client.close()
                return
        '''
        # TODO
        if data.decode('utf-8') == 'To sign up ACK':
            confirm = 0
            while not confirm:
                print('Now sign up')
               #===========Loggin============
                Username = input('Please enter your name: ')
                Password = getpass.getpass('Password: ')
                CheckPassword = getpass.getpass('Password again: ')
                while Password != CheckPassword:
                    print("Passwords are not same, please enter again.")
                    Password = getpass.getpass('Password: ')
                    CheckPassword = getpass.getpass('Password again: ')
                    
                data = Username + ',' + Password
                data = data.encode('utf-8')
                client.sendall(data)
                data = client.recv(1024)
                ##TODO 
                if(data == b'sign up ACK'):
                    print("Sign up successfully!!")
                    confirm = 1
                else:
                    print("The account has been used.")    

    elif operation == "login":
        client.sendall("login".encode("utf-8"))
        data = client.recv(1024)
        #====Check username & password====
        confirm = 0
        while not confirm:
            print('Now Login')
           #===========Loggin============
            Username = input('Please enter your name: ')
            Password = input('Password: ')
            data = Username + ',' + Password + '\n'
            data = data.encode('utf-8')
            client.sendall(data)
            data = client.recv(1024)
           ############################################
            if(data == b'ACK'): ## TODO
                print("Loggin Success!!")
                confirm = 1
            else:
                print("Username or password isn't correct.")
        ##############################################
        #======Create Thread to Recieve msg======

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
    client.close()

