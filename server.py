import socket
import threading
import json
import select
import argparse

class Client_info():
    def __init__(self, connect, host, port):
        self.connect = connect
        self.host = host
        self.port = port
        self.usrname = ""
        self.passwd  = ""
        self.state = "Initial State"

class thread_accept_client(threading.Thread):
    global client_list
    def __init__(self, listen_socket, client_list): 
        threading.Thread.__init__(self)
        self._stop_event = threading.Event() #For Stoping Thread
        self.socket = listen_socket
        
        self.read_list = [listen_socket]
        with open('db.json', 'r+', encoding='utf-8') as f:
            self.database = json.load(f)
            for x in self.database:
                print(x, self.database[x])

    def run(self):
        print(u'waiting for connect...',flush=True)
        while not self._stop_event.is_set():
            readable, writable, errored = select.select(self.read_list, [], [])
            for s in readable:
                if s is self.socket:
                     #Todo: client info maintain
                    connect, (host, port) = self.socket.accept()
                    print(u'the client %s:%s has connected.' % (host, port))
                    
                    new_client_info = client(connect, host, port)
                    client_list.append(new_client_info)
                    connect.sendall(b'Initial:Welcome')
                    thread_running_client(new_client_info)
                '''
                else:  

                    recv_data = s.recv(1024)
                
                    print(recv_data,flush=True)
                    recv_data = recv_data.decode('utf-8').split(',')
                    #recv_data[1] = recv_data[1].replace("\n","")
                    print(self.database[recv_data[0]],'456',flush=True)
                    
                    if self.database[recv_data[0]] == recv_data[1]: #Check if user is valid
                        self.list.append({"host":host,
                                          "port":port,
                                          "usrname":recv_data[0],
                                          "passwd":recv_data[1],
                                          "Socket":connect
                                         })
                        connect.sendall(b'ACK')
                    else:
                        connect.sendall(b'NEG')
                '''
    def stop(self):
        self._stop_event.set()

class thread_running_client(threading.Thread):
    global broadcast_msg
    global mic_lock
    global client_list
    global States
    def __init__(self, client_info):
        self.info = client_info
        self._stop_event = threading.Event() #For Stoping Thread
        
        # below states should be made in a global variable(but no time QQ)
        self.initial_state = "Initial"
        self.login_state = "Login"
        self.sign_up_state = "Sign up"
        self.wait_for_talk_state = "wait for talk"
        self.talking_state = "Talking"
        
        with open('db.json', 'r+', encoding='utf-8') as f:
            self.database = json.load(f)
            for x in self.database:
                print(x, self.database[x])
    
    def run(self):
        while not self._stop_event.is_set():
            raw_data = self.info.connect.recv(1024)
            data = raw_data.decode('utf-8')
            print(data)
            if self.info.state == self.initial_state:
                if data == "sign up":
                    send_data = self.sign_up_state + ":" + "Ent"
                    self.info.state = self.sign_up_state
                elif data == "login":
                    send_data = self.login_state + ":" + "Ent"
                    self.info.state = self.login_state
                elif data == "quit":
                    self.socket.close()
                    self.list.remove(self.info)
                    self._stop_event.set()
                    return
                else:
                    send_data = self.info.stage + ":" + "NoImpl"
                    print("not implement")
                    
            elif self.info.state == self.login_state :
                usr,pwd = data.split(",")
                if usr not in self.database or self.database[usr] != pwd:
                    send_data = self.login_state + ":"
                else:
                    send_data = self.waiting_for_talk_state + ":" + "Ent"
                    self.info.state = self.waiting_for_talk_state

            elif self.info.state == self.sign_up_state:
                usr, pwd = data.split(",")
                if usr in self.database:
                    send_data = self.sign_up_state + ":" + "Rej"
                else:
                    send_data = self.wait_for_talk_state + ":" + "Ent"
                    self.info.state = self.waiting_for_talk_state
            elif self.info.state == self.waiting_for_talk_state:
                if data == "Req":
                    if self.lock.acquire(blocking == False):
                        send_data =  self.talking_state + ":" + "Mic_ACK"
                        self.info.state = self.talking_state
                    else:
                        send_data =  self.waiting_for_talk_state + ":" + "Mic_REJ"
            elif self.talking_state:
                if data == "quit":
                    send_data = self.waiting_for_talk_state + ":" + "Ent"
                    self.info.state = self.waiting_for_talk_state 
                else:
                    for client in client_list:
                        if client == self.info:
                            continue
                        client.socket.sendall(raw_data)


    def stop(self):
        self._stop_event.set()

if __name__ == "__main__":
    #===== arg parsing ===============
    parser = argparse.ArgumentParser()
    parser.add_argument("IP", help="The IP the server be")
    parser.add_argument("port", type=int, help="port of the IP")
    args = parser.parse_args()
    print(args.IP, args.port)
    #=====Create Socket to listen=====
    IP = args.IP
    Port = args.port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, Port))
    server.listen(5)

    #======client data======== (Todo)
    client_list = list()
    '''
    O)
    Format: [client_info_1 , client_info_2, ...]
    X)
    Format: [{"host":"140.112.20.35",
              "port":"1234",
              "usrname":"Bob",
              "passwd":"abc123",
              "Socket":connect}
            ]
    '''
    
    #======Start Listening======
    listening = thread_accept_client(server, client_list)
    listening.start()
    
    mic_lock = threading.Lock()
    global broadcast_msg 
    broadcast_msg = ""
    '''
    while True:
        data = server.recv(1024)
        if data == b'quit' or data == b'':
            print(b'the client has quit.')
            break
        else:
            server.sendall(b'your words has received.')
            print(b'the client say:' + data)
     
'''
    #listening.stop()
    listening.join()
     
    server.close()
