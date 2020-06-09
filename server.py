import socket
import threading
import json
import select
import argparse
from Variables import States, Client_info

#TODO: client database lock, client list lock

'''
class Client_info():
    def __init__(self, connect, host, port):
        self.connect = connect
        self.host = host
        self.port = port
        self.username = ""
        self.password  = ""
        self.state = States.initial
'''
class thread_accept_client(threading.Thread):
    global client_list
    global client_database
    def __init__(self, listen_socket, client_list): 
        threading.Thread.__init__(self)
        self._stop_event = threading.Event() #For Stoping Thread
        self.socket = listen_socket
        
        self.read_list = [listen_socket]

    def run(self):
        print(u'waiting for connect...',flush=True)
        while not self._stop_event.is_set():
            readable, writable, errored = select.select(self.read_list, [], [])
            for s in readable:
                if s is self.socket:
                     #Todo: client info maintain
                    connect, (host, port) = self.socket.accept()
                    print(u'the client %s:%s has connected.' % (host, port))
                    
                    new_client_info = Client_info(connect, host, port)
                    client_list.append(new_client_info)
                    send_data = States.initial +  ":" + "Welcome"
                    send_raw_data = send_data.encode("utf-8")
                    connect.sendall(send_raw_data)
                    running = thread_running_client(new_client_info)
                    running.start()
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
    global client_database

    def __init__(self, client_info):
        threading.Thread.__init__(self)
        self.info = client_info
        self._stop_event = threading.Event() #For Stoping Thread
    
    def run(self):
        print("Connection Start", flush=True)
        while not self._stop_event.is_set():
            raw_data = self.info.connect.recv(1024)
            data = raw_data.decode('utf-8')
            print("First data", data)
            if self.info.state == States.initial:
                if data == States.sign_up:
                    self.info.state = States.sign_up
                    send_data = self.info.state + ":" + "Ent"
                elif data == States.login:
                    self.info.state = States.login
                    send_data = self.info.state + ":" + "Ent"
                elif data == "quit":
                    self.info.connect.close()
                    client_list.remove(self.info)
                    self._stop_event.set()
                    return
                else:
                    send_data = self.info.state + ":" + "NoImpl"
                    print("not implement")
                send_raw_data = send_data.encode("utf-8")
                self.info.connect.sendall(send_raw_data)
                    
            elif self.info.state == States.login :
                usr,pwd = data.split(",")
                print( usr, pwd)
                if usr not in client_database or client_database[usr] != pwd:
                    send_data = self.info.state + ":" + "Wrong"
                    self.info.state = States.waiting_for_talk
                else:
                    self.info.state = States.waiting_for_talk
                    send_data = self.info.state + ":" + "Ent"
                    self.info.username = usr
                    self.info.password = pwd

                send_raw_data = send_data.encode("utf-8")
                self.info.connect.sendall(send_raw_data)

            elif self.info.state == States.sign_up:
                usr, pwd = data.split(",")
                print( usr, pwd)
                if usr in client_database:
                    send_data = self.info.state + ":" + "Rej"
                else:
                    self.info.state = States.initial
                    send_data = self.info.state + ":" + "Ent"
                    self.info.username = usr
                    self.info.password = pwd
                    client_database[usr] = pwd

                send_raw_data = send_data.encode("utf-8")
                self.info.connect.sendall(send_raw_data)

            elif self.info.state == States.waiting_for_talk:
                if data == "Req":
                    if self.lock.acquire(blocking == False):
                        self.info.state = States.talking
                        send_data =  self.info.state + ":" + "Mic_ACK"
                    else:
                        send_data =  self.info.state + ":" + "Mic_REJ"
                elif data == "quit":
                    self.info.state = States.initial
                    send_data = self.info.state + ":" + "Ent"
                send_raw_data = send_data.encode("utf-8")
                self.info.connect.sendall(send_raw_data)

            elif self.info.state == States.talking:
                if data == "quit":
                    self.info.state = States.waiting_for_talk
                    send_data = self.info.state + ":" + "Ent"
                    send_raw_data = send_data.encode("utf-8")
                    self.info.connect.sendall(send_raw_data)
                else:
                    for client in client_list:
                        if client == self.info:
                            continue
                        self.socket.sendall(raw_data)

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
    global client_database
    with open('db.json', 'r+', encoding='utf-8') as f:
        client_database = json.load(f)
        for x in client_database:
            print(x, client_database[x])

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
    
    with open('db.json', 'w', encoding='utf-8') as f:
        json.dumps(client_database)
        for x in client_database:
            print(x, client_database)  
    server.close()
