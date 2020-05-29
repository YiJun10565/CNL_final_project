import socket


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 6688))
server.listen(5)

print(u'waiting for connect...')
connect, (host, port) = server.accept()
print(u'the client %s:%s has connected.' % (host, port))

while True:
    data = connect.recv(1024)
    if data == b'quit' or data == b'':
        print(b'the client has quit.')
        break
    else:
        connect.sendall(b'your words has received.')
        print(b'the client say:' + data)

server.close()

