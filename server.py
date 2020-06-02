import socket
import threading

class thread_accept_client(threading.Thread):
    def __init__(self, listen_socket):
        super(thread_listen_client, self)
		self._stop_event = threding.Event() #For Stoping Thread
        self.socket = listen_socket

    def run(self):
	    print(u'waiting for connect...')
		while(self._stop_event.is_set() == False):
		    #Todo: client info maintain
    		connect, (host, port) = server.accept()
            print(u'the client %s:%s has connected.' % (host, port))
        
    def stop(self):
        self._stop_event.set()

if '__name__' == '__main__':
    
    #=====Create Socket to listen=====
    IP = '127.0.0.1'
    Port = 9999
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, Port))
    server.listen(5)

    #======client data======== (Todo)
	
	
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
