import socket


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 6688))

while True:
    data = input()
    data = data.encode('utf-8')
    if data == b'quit':
        print(b'connect quit.')
        break
    else:
        client.sendall(data)
        rec_data = client.recv(1024)
        print(b'form server receive:' + rec_data)

client.sendall(b'quit')
client.close()
