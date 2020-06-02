import socket
import threading

class thread_accept_client(threading.Thread):
    def __init__(self, listen_socket, client_list):
        super(thread_listen_client, self)
        self._stop_event = threding.Event() #For Stoping Thread
        self.socket = listen_socket
        self.list = client_list
		
    def run(self):
	    print(u'waiting for connect...')
	    while(self._stop_event.is_set() == False):
    		#Todo: client info maintain
    		connect, (host, port) = self.socket.accept()
    		print(u'the client %s:%s has connected.' % (host, port))
    		recv_data = self.socket.recv(1024)
    		recv_data = recv_data.decode('utf-8').split(',')
			if(): #Check if user is valid
        		self.list.append({"host":host,
                                  "port":port,
                                  "usrname":recv_data[0],
                                  "passwd":recv_data[1],
                                  "Socket":connect
                                 })
		   else:
		       connect.sendall(b'Username or password isn\'t correct.')
			   connect.close()
        
    def stop(self):
        self._stop_event.set()

if "__name__" == "__main__":
    
    #=====Create Socket to listen=====
    IP = '127.0.0.1'
    Port = 9999
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
	
    #======Start Listening======
    listening = thread_accept_client(server)
    listening.start()
    

    while True:
        data = connect.recv(1024)
        if data == b'quit' or data == b'':
            print(b'the client has quit.')
            break
        else:
            connect.sendall(b'your words has received.')
            print(b'the client say:' + data)
     
	 
	 listening.stop()
	 listening.join()
	 
     server.close()
