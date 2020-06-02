import socket
import threading
import json
import select

class thread_accept_client(threading.Thread):
    def __init__(self, listen_socket, client_list): 
        threading.Thread.__init__(self)
        self._stop_event = threading.Event() #For Stoping Thread
        self.socket = listen_socket
        self.list = client_list
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
                    self.read_list.append(connect)
                else:       
                    recv_data = s.recv(1024)
                
                    print(recv_data,flush=True)
                    recv_data = recv_data.decode('utf-8').split(',')
                    recv_data[1] = recv_data[1].replace("\n","")
                    print(self.database[recv_data[0]],'456',flush=True)
                    
                    print(len(recv_data[1]),flush=True)
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
            
    def stop(self):
        self._stop_event.set()


if __name__ == "__main__":
    
    #=====Create Socket to listen=====
    IP = '127.0.0.1'
    Port = 23459
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, Port))
    server.listen(5)

    #======client data======== (Todo)
    client_list = list()
    '''
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
