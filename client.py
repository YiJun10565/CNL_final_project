import socket
import threading

class thread_recv_sound(threading.Thread):
    def __init__(self, client_socket):
        super(thread_recv_sound, self).__init__
        self._stop_event = threding.Event() #For Stoping Thread
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


if "__name__" == "__main__":
    #======Connect to Server=====
    IP = '127.0.0.1'
    port = 9999
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, port)) #Server IP & Port
	
    #====Check username & password====
	confirm = 0
	while(not confirm):
	    #===========Loggin============
        Username = input('Please enter your name: ')
        Password = input('Password: ')
	    data = Username + ',' + Password + '\n'
	    data = data.encode('utf-8')
        client.sendall(data)
		data = client.recv(1024)
		if(data == b'ACK'):
		    print("Loggin Success!!")
			confirm = 1
		else:
		    print("Username or password isn\'t correct.")
    
    #======Create Thread to Recieve msg======
    recv_sound = thread_recv_sound(client)
    recv_sound.start()

    while True: #Todo: check authorization to talk
        data = input() #Change this to vocal
        data = data.encode('utf-8')
        client.sendall(data)

    recv_sound.stop()
    recv_sound.join()

    client.sendall(b'quit')
    client.close()