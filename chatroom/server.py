import socket
import select
import json
import time
import signal
import os
import threading


ip = "127.0.0.1"
port = 9487

def save_dataset(dataset):
    with open('dataset.json', 'w') as mes_f:
        json.dump(dataset, mes_f)

def load_dataset():
    with open('dataset.json', 'r') as mes_f:
        return json.load(mes_f)

def lose_connect(data, sd):
	if len(data) == 0:
		leave_user = sd_list[sd]['u']
		read_sd.remove(sd)
		if sd_list[sd]['f'] == 'user':
			print('user \"' + leave_user + "\" logs out!", flush=True)			
			user_sta[leave_user] = 'offline'
			user_pkt = json.dumps(user_sta)
			for acc in user_sds:
				if user_sta[acc] == 'online':						
					snd_pkt(user_pkt, user_sds[acc]['user'])
			for f in user_sds[leave_user]:
				if user_sds[leave_user][f] in read_sd:
					read_sd.remove(user_sds[leave_user][f])
					user_sds[leave_user][f].close()
				del sd_list[user_sds[leave_user][f]]				
			user_sds[leave_user] = dict({})
			#print(read_sd)
		else:
			if sd in read_sd:
				read_sd.remove(sd)
			if leave_user != 'unknown':
				del user_sds[leave_user][sd_list[sd]['f']]			
			del sd_list[sd]
		#print(sd_list)
		#print(user_sds)
		sd.close()
		return True

def rcv_pkt(sd):
	data = sd.recv(32)
	
	if lose_connect(data, sd):
		return False

	read_len = int(data.decode(), 2)
	data_rcv = ''
	#time.sleep(0.01)
	#print(read_len)
	while len(data_rcv) < read_len:
		data_rcv += sd.recv(1024).decode()
	#	print(data_rcv)
	return data_rcv

def snd_pkt(data, sd):
	sd.sendall(('{0:032b}'.format(len(data))+data).encode())

def rcv_file(sender, receiver, filename, sd):
	print("receive file\"" + filename + '\"')	
	with open(os.path.join(os.path.abspath("."), 'file', sender + '_' + filename ), "wb") as f:
		data = sd.recv(1024)
		while len(data) > 0:
			f.write(data)
			data = sd.recv(1024)
	#print('1', flush=True)
	sd.sendall(b'1')
	content = 'File sent: ' + filename
	timestamp = time.strftime('%Y-%m-%d %H:%M',time.localtime())
	msg = (sender, timestamp, content)
	file_msg = (sender, filename)
	dataset[sender][receiver]['messages'].append(msg)
	dataset[sender][receiver]['files'].append(file_msg)
	if sender != receiver:
		dataset[receiver][sender]['messages'].append(msg)
		dataset[receiver][sender]['files'].append(file_msg)
	dataset[sender][receiver]['seen'] = len(dataset[sender][receiver]['messages'])
	# update client
	pkt_to_sender = receiver+'\n'+json.dumps(msg)+'\n'+json.dumps(file_msg)
	snd_pkt(pkt_to_sender, user_sds[sender]['frcv'])
	pkt_to_receiver = sender+'\n'+json.dumps(msg)+'\n'+json.dumps(file_msg)
	if user_sta[receiver] == 'online' and sender != receiver:
		snd_pkt(pkt_to_receiver, user_sds[receiver]['frcv'])
	if user_sds[sender].get(sd_list[sd]['f']) != None:
		del user_sds[sender][sd_list[sd]['f']]			
	del sd_list[sd]


def snd_file(sender, filename, sd):
	with open(os.path.join(os.path.abspath("."), 'file', sender + '_' + filename ), "rb") as f:
		data = f.read(1024)
		while len(data) > 0:
			sd.sendall(data)
			data = f.read(1024)
	if user_sds[sd_list[sd]['u']].get(sd_list[sd]['f']) != None:
		del user_sds[sd_list[sd]['u']][sd_list[sd]['f']]
	sd.shutdown(1)
	del sd_list[sd]


thread_queue = []
def thread_controller():
	while True:
		if len(thread_queue) > 0:
			thread_queue[0].start()
			thread_queue[0].join()
			thread_queue.remove(thread_queue[0])
			print("done", flush=True)
thread = threading.Thread(target = thread_controller)
thread.setDaemon(True)
thread.start()

def end(signum, frame):
	print('Bye~', flush=True)
	for sd in sd_list:
		sd.shutdown(1)
		sd.close()
	acc_file.close()
	save_dataset(dataset)	

	exit(0)
signal.signal(signal.SIGINT, end)
signal.signal(signal.SIGTERM, end)
   
sd_list = dict({}) # sd's function {sd0 : 'no', sd1 : {'f' : 'in', 'u' : 'username'}, sd2 : {'f' : 'user', 'u' : 'username'}}
user_pwd = dict({}) # {'ko870903' : '73ed1a188fceb7c10108aa7b1e5b340f', # password is ko880816
					#  'joe0123'  : 'e82b37d84c2fb486fb04a83cd4764f34',  # password is 94879487
					#  'sam880222': '5f4dcc3b5aa765d61d8327deb882cf99'} # password is password
user_sta = dict({}) # {'ko870903' : 'offline', 'joe0123'  : 'offline', 'sam880222': 'offline'} 	
user_sds = dict({}) # {'user_name' : {'user' : sd0, 'mrcv' : sd1, 'frcv' : sd2}}



if not os.path.exists('./file'):
	os.makedirs('./file')

# import account info
acc_file = open("account.txt", "a+")
acc_file.seek(0, 0) # seek to the head of the file
for acc in acc_file.readlines():
    acc = acc.split()
    user_pwd[acc[0]] = acc[1]
    user_sta[acc[0]] = 'offline'
    user_sds[acc[0]] = dict({})
acc_file.seek(0, 2) # seek to the end of the file

dataset = load_dataset()
ip_addr = (ip, port)
s_sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s_sd.bind(ip_addr)
s_sd.listen()
read_sd = [s_sd]
write_sd = []
ex_sd = []  # PASS

while True:
	readable, writable, exceptional = select.select(read_sd, write_sd, ex_sd, 10e-3)
	'''
	if not (readable or writable or exceptional):
		print("Time out!")
		break
	'''
	#if readable != []:
		#print(readable, flush=True)
	for sd in readable:
		if sd.fileno() == -1:
			#print("select closed sd")
			continue
		if sd is s_sd: #new connect
			c_sd, c_addr = sd.accept()
			c_sd.setblocking(0)
			read_sd.append(c_sd)
			sd_list[c_sd] = dict({'f' : 'no', 'u' : 'unknown'})
			#print(sd_list)

		elif sd_list[sd]['f'] == 'no':
			data_rcv = rcv_pkt(sd)
			if data_rcv == False:
				continue
			data_rcv = data_rcv.split('\n')
			sd_list[sd] = dict({'f' : data_rcv[1], 'u' : data_rcv[0]})
			sd.sendall(b'1')
			if data_rcv[0] != 'unknown':
				user_sds[data_rcv[0]][data_rcv[1]] = sd
			if data_rcv[1] == 'mrcv':
				msg_pkt = json.dumps(dataset[data_rcv[0]])
				snd_pkt(msg_pkt, sd)
			# print("socket with "+data_rcv[0]+ " for "+data_rcv[1]+" is built\n")

		# check login
		elif sd_list[sd]['f'] == 'in':
			data_rcv = rcv_pkt(sd)
			if data_rcv == False:
				continue
			data_rcv = data_rcv.split('\n')
			password = user_pwd.get(data_rcv[0])
			if password == None:
				ack = 'u'
				sd.sendall(ack.encode())
			elif password == data_rcv[1]:
				ack = 'a'
				sd.sendall(ack.encode())
				user_sta[data_rcv[0]] = 'online'
				sd_list[sd] = dict({'f' : 'user', 'u' : data_rcv[0]})				
				user_sds[data_rcv[0]]['user'] = sd
				print('user \"' + data_rcv[0] + '\" logs in!')
				user_pkt = json.dumps(user_sta)
				for acc in user_sds:
					if user_sta[acc] == 'online':						
						snd_pkt(user_pkt, user_sds[acc]['user'])
			else:
				ack = 'p'
				sd.sendall(ack.encode())

		elif sd_list[sd]['f'] == 'up':
			data_rcv = rcv_pkt(sd)
			if data_rcv == False:
				continue
			data_rcv = data_rcv.split('\n')
			if data_rcv[0] in user_pwd.keys():
				ack = 'u'
				sd.sendall(ack.encode())
			else:
				ack = 'a'
				sd.sendall(ack.encode())
				user_sta[data_rcv[0]] = 'offline'
				user_pwd[data_rcv[0]] = data_rcv[1]
				user_sds[data_rcv[0]] = dict({})
				dataset[data_rcv[0]] = dict({})		
				#print(user_sta)
				user_pkt = json.dumps(user_sta)				
				for acc in user_sds:
					dataset[data_rcv[0]][acc] = dict({'seen': 0, 'messages': [], 'files': []})
					dataset[acc][data_rcv[0]] = dict({'seen': 0, 'messages': [], 'files': []})
					if user_sta[acc] == 'online':
						snd_pkt(data_rcv[0]+'\n', user_sds[acc]['mrcv'])
						snd_pkt(user_pkt, user_sds[acc]['user'])
				acc_file.writelines([data_rcv[0]+'\t'+data_rcv[1]+'\n'])

		elif sd_list[sd]['f'] == 'user':
			#print(sd_list)
			data_rcv = rcv_pkt(sd)
			if data_rcv == False:
				continue
			content = json.loads(data_rcv)
			#print(content)
			for info in content:
				dataset[sd_list[sd]['u']][info[0]]['seen'] = info[1]
			sd.shutdown(1)	#send ack to client

		elif sd_list[sd]['f'] == 'msnd':
			data_rcv = rcv_pkt(sd)
			if data_rcv == False:
				continue
			data_rcv = data_rcv.split('\n')
			sender = sd_list[sd]['u']
			receiver = data_rcv[0]
			content = json.loads(data_rcv[1])
			timestamp = time.strftime('%Y-%m-%d %H:%M',time.localtime())
			msg = (sender, timestamp, content)
			dataset[sender][receiver]['messages'].append(msg)
			if sender != receiver:
				dataset[receiver][sender]['messages'].append(msg)
			dataset[sender][receiver]['seen'] = len(dataset[sender][receiver]['messages'])
			pkt_to_sender = receiver+'\n'+json.dumps(msg)
			snd_pkt(pkt_to_sender, user_sds[sender]['mrcv'])
			pkt_to_receiver = sender+'\n'+json.dumps(msg)
			if user_sta[receiver] == 'online' and sender != receiver:
				snd_pkt(pkt_to_receiver, user_sds[receiver]['mrcv'])

		elif sd_list[sd]['f'] == 'f_up':
			data_rcv = rcv_pkt(sd)
			if data_rcv == False:
				continue
			data_rcv = data_rcv.split('\n')
			sender = sd_list[sd]['u']
			receiver = data_rcv[0]
			filename = json.loads(data_rcv[1])
			sd_list[sd]['f'] = 'f_up'
			read_sd.remove(sd)
			sd.setblocking(1)
			thread = threading.Thread(target = rcv_file, args = (sender, receiver, filename, sd,))
			thread_queue.append(thread)
			sd.sendall(b'1')
		
		elif sd_list[sd]['f'] == 'f_down':
			data_rcv = rcv_pkt(sd)
			if data_rcv == False:
				continue
			data_rcv = data_rcv.split('\n')
			sender = data_rcv[0]
			filename = json.loads(data_rcv[1])
			sd_list[sd]['f'] = 'f_down'
			user_sds[sd_list[sd]['u']]['f_down'] = sd

			read_sd.remove(sd)
			sd.setblocking(1)
			thread = threading.Thread(target = snd_file, args = (sender, filename, sd))
			thread.setDaemon(True)
			thread.start()